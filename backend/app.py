
import os
import logging
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body, BackgroundTasks, Depends, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel
import json
import asyncio
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
from contextlib import asynccontextmanager
import base64
import requests
from fastapi.responses import StreamingResponse
import io
from fastapi import HTTPException
import pandas as pd
from pathlib import Path
import numpy as np
from functools import lru_cache
import time
import aiohttp

# 设置日志
# 设置更详细的日志格式
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 数据库设置
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 全局变量
APP_ID = "2e7137fb-9a22-4246-8593-f0a9b4fc9695"
AUTH_STRING = "bce-v3/ALTAK-YLij17TdPMsg11izg9HAn/3168a0aea58dfbbe24023103d4dec3830d225aca"
BASE_URL = "https://qianfan.baidubce.com/v2/app"
HEADERS = {
    "Authorization": f"Bearer {AUTH_STRING}",
    "Content-Type": "application/json"
}

## 语音合成
VOCIE_APP_ID = "105869441"
API_KEY = "gbQkp2BAStGOpIhoEBONd7JP"
SECRET_KEY = "aUzTQGuHCaWP9ikIz6ZnZmEVYgYOQHA3"
SCOPE = "audio_voice_assistant_get"  # 根据您的需求设置

TOKEN_URL = 'http://aip.baidubce.com/oauth/2.0/token'
async def get_baidu_token():
    """获取百度 API 的 access token"""
    params = {
        'grant_type': 'client_credentials',
        'client_id': API_KEY,
        'client_secret': SECRET_KEY
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(TOKEN_URL, params=params)
            result = response.json()
            
            if 'access_token' in result and 'scope' in result:
                if SCOPE and (SCOPE not in result['scope'].split(' ')):
                    raise HTTPException(status_code=400, detail='scope is not correct')
                
                logger.info(f"成功获取 TOKEN: {result['access_token']}; 期时间(秒): {result['expires_in']}")
                return result['access_token']
            else:
                raise HTTPException(status_code=400, detail='API_KEY 或 SECRET_KEY 可能不正确: 在 token 响应中未找到 access_token 或 scope')
        
        except httpx.RequestError as e:
            logger.error(f"获取 token 时发生网络错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取 token 时发生网络错误: {str(e)}")
        
        except json.JSONDecodeError as e:
            logger.error(f"解析 token 响应时发生错误: {str(e)}")
            raise HTTPException(status_code=500, detail=f"解析 token 响应时发生错误: {str(e)}")
    
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, index=True)
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# 全局变量存储处理后的数据
processed_data = {}

async def process_all_data():
    """在服务器启动时处理所有数据文件"""
    logger.info("开始处理所有数据文件...")
    for data_type, file_name in DATA_FILES.items():
        try:
            logger.info(f"处理数据文件: {file_name}")
            df = pd.read_csv(f'data/{file_name}', encoding='utf-8', low_memory=False)  # 添加 low_memory=False
            
            # 重命名第一列为 date 并设置为索引
            df = df.rename(columns={'指标名称': 'date'})
            df.set_index('date', inplace=True)
            
            # 尝试解析日期，指定格式
            try:
                df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
            except ValueError:
                # 如果指定格式失败，则使用自动推断
                df.index = pd.to_datetime(df.index)
            
            df.sort_index(inplace=True)
            
            # 清理数据：移除逗号，转换为数值类型，处理无效值
            for col in df.columns:
                df[col] = df[col].apply(lambda x: str(x).replace(',', '') if pd.notnull(x) else x)
                df[col] = pd.to_numeric(df[col], errors='coerce')  # 使用coerce将无效值转换为NaN
                # 将无限值替换为 NaN
                df[col] = df[col].replace([np.inf, -np.inf], np.nan)
            
            # 存储处理后的数据
            processed_data[data_type] = df
            logger.info(f"成功处理数据文件: {file_name}, 包含 {len(df.columns)} 个指标")
            
        except Exception as e:
            logger.error(f"处理数据文件 {file_name} 时出错: {str(e)}")
            raise

# 创建一个全局的异步队列
response_queue = asyncio.Queue()

# 全局字典来存储正在进行的对话
ongoing_conversations = {}

async def save_responses_worker():
    while True:
        conversation_id, full_response = await response_queue.get()
        try:
            db = SessionLocal()
            save_message(db, conversation_id, "assistant", full_response)
        except Exception as e:
            logger.error(f"Error saving response: {e}")
        finally:
            db.close()
        response_queue.task_done()

async def precache_priority_pages():
    """预先缓存优先级较高的页面数据"""
    logger.info("开始预缓存优先页面数据...")
    start_time = time.time()
    
    # 获取总数据量
    temp_data = get_cached_page_data(1, 9, None)
    total_items = temp_data["total"]
    total_pages = (total_items + 8) // 9  # 向上取整
    
    # 定义优先缓存的页面
    priority_pages = (
        # 前10页
        list(range(1, 11)) + 
        # 最后10页
        list(range(max(11, total_pages - 9), total_pages + 1))
    )
    
    # 预缓存优先页面
    for page in priority_pages:
        try:
            get_cached_page_data(page, 9, None)
            logger.debug(f"已缓存第 {page} 页")
        except Exception as e:
            logger.error(f"缓存第 {page} 页时出错: {str(e)}")
    
    end_time = time.time()
    logger.info(f"优先页面预缓存完成，共 {len(priority_pages)} 页，耗时: {end_time - start_time:.2f}秒")

# 后台缓存任务
async def background_cache_task():
    """在后台缓存其他页面"""
    try:
        temp_data = get_cached_page_data(1, 9, None)
        total_items = temp_data["total"]
        total_pages = (total_items + 8) // 9
        
        # 获取所有需要缓存的页面
        all_pages = set(range(1, total_pages + 1))
        # 排除已经缓存的优先页面
        priority_pages = set(list(range(1, 21)) + list(range(max(21, total_pages - 19), total_pages + 1)))
        remaining_pages = all_pages - priority_pages
        
        logger.info(f"开始后台缓存剩余 {len(remaining_pages)} 页...")
        
        for page in remaining_pages:
            try:
                get_cached_page_data(page, 9, None)
                if page % 50 == 0:  # 每50页记录次进度
                    logger.info(f"后台已缓存到第 {page} 页")
                # 添加小延迟，避免占用太多资源
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"后台缓存第 {page} 页时出错: {str(e)}")
                
        logger.info("后台缓存任务完成")
        
    except Exception as e:
        logger.error(f"后台缓存任务出错: {str(e)}")

# 修改应用启动生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 跳过启动时的数据处理，直接启动服务器
    logger.info("应用启动完成")
    yield
    logger.info("应用关闭")

app = FastAPI(lifespan=lifespan)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://120.48.150.254:3000", "http://120.48.150.254:3100",
        "http://106.12.206.107:8080",
     "http://localhost:3000", "http://localhost:3100", "http://127.0.0.1:3000", "http://127.0.0.1:3100"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# API 调用辅助函数
async def make_api_call(endpoint: str, method: str = "POST", data: dict = None, files: dict = None, timeout: float = 30.0):
    url = f"{BASE_URL}/{endpoint}"
    headers = HEADERS.copy()
    
    logger.info(f"正在调用 API: {url}")
    logger.info(f"请求数据: {data}")

    async with httpx.AsyncClient(timeout=timeout) as client:
        if method == "POST":
            if files:
                del headers["Content-Type"]
                response = await client.post(url, headers=headers, data=data, files=files)
            else:
                response = await client.post(url, headers=headers, json=data)
        else:
            response = await client.get(url, headers=headers, params=data)
    
    logger.info(f"收到响应状态码: {response.status_code}")
    
    try:
        return {
            "status_code": response.status_code,
            "content": response.json(),
            "headers": dict(response.headers)
        }
    except json.JSONDecodeError:
        return {
            "status_code": response.status_code,
            "content": response.text,
            "headers": dict(response.headers)
        }

@app.post("/conversation")
async def create_conversation(db: Session = Depends(get_db)):
    """创建新对话"""
    data = {"app_id": APP_ID}
    result = await make_api_call("conversation", data=data)
    if result["status_code"] != 200:
        raise HTTPException(status_code=result["status_code"], detail=result["content"])
    
    conversation_id = result["content"]["conversation_id"]
    db_conversation = Conversation(conversation_id=conversation_id)
    db.add(db_conversation)
    db.commit()
    
    return result["content"]

@app.post("/upload_file")
async def upload_file(
    file: UploadFile = File(...),
    app_id: str = Form(...),
    conversation_id: str = Form(...)
):
    """上传文件到对话"""
    data = {
        "app_id": app_id,
        "conversation_id": conversation_id
    }
    files = {"file": (file.filename, file.file, file.content_type)}
    
    result = await make_api_call("conversation/file/upload", data=data, files=files)
    if result["status_code"] != 200:
        raise HTTPException(status_code=result["status_code"], detail=result["content"])
    return result["content"]

class ChatRequest(BaseModel):
    query: str
    conversation_id: str
    stream: bool = False
    file_ids: Optional[List[str]] = None

async def make_api_call_stream(endpoint: str, data: dict):
    url = f"{BASE_URL}/{endpoint}"
    headers = HEADERS.copy()
    
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", url, headers=headers, json=data) as response:
            async for chunk in response.aiter_text():
                yield chunk

def save_message(db: Session, conversation_id: str, role: str, content: str):
    db_message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    db.add(db_message)
    db.commit()
    logger.info(f"保存了 {role} 消息: {content[:100]}...")  # 记录前100个字符


@app.post("/stream")
async def stream(
    db: Session = Depends(get_db),
    conversation_id: str = Body(...), 
    query: str = Body(...), 
    file_ids: List[str] = Body(default=None)
):
    # 保存用户查询
    save_message(db, conversation_id, "user", query)

    # 初始化对话响应
    ongoing_conversations[conversation_id] = ""

    data = {
        "app_id": APP_ID,
        "query": query,
        "stream": True,
        "conversation_id": conversation_id
    }
    if file_ids:
        data["file_ids"] = file_ids

    logger.info(f"开始为对话 {conversation_id} 生成流式响应")
    return StreamingResponse(
        process_stream(make_api_call_stream("conversation/runs", data), conversation_id),
        media_type='text/event-stream'
    )

async def process_stream(stream, conversation_id: str):
    try:
        async for chunk in stream:
            logger.debug(f"Received chunk: {chunk[:100]}...")  # Log the first 100 characters of each chunk
            yield chunk  # 返回原始数据块

            # 处理数据块累积完整响应
            if chunk.startswith('data: '):
                try:
                    data = json.loads(chunk[6:])
                    if 'answer' in data:
                        ongoing_conversations[conversation_id] += data['answer']
                        logger.debug(f"Added to response: {data['answer'][:50]}...")  # Log the first 50 characters added
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {e}")
            else:
                logger.warning(f"Received unexpected chunk format: {chunk[:50]}...")
    except Exception as e:
        logger.error(f"Stream processing error: {e}")
    finally:
        # 流结束后，直接保存完整响应
        logger.info(f"Stream ended for conversation {conversation_id}")
        await save_full_response(conversation_id)

async def save_full_response(conversation_id: str):
    try:
        full_response = ongoing_conversations.pop(conversation_id, "")
        logger.debug(f"Full response for conversation {conversation_id}: {full_response[:100]}...")  # Log the first 100 characters of the full response
        if full_response:
            logger.info(f"流式响应结束，保存完整响应：{full_response[:100]}...")  # 记录前100个字符
            db = SessionLocal()
            try:
                save_message(db, conversation_id, "assistant", full_response)
            finally:
                db.close()
        else:
            logger.warning(f"流式响应结束，但full_response为空")
    except Exception as e:
        logger.error(f"Error saving full response: {e}")

@app.post("/chat")
async def chat(
    chat_request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """发送聊天消息到模型"""
    try:
        data = {
            "app_id": APP_ID,
            "query": chat_request.query,
            "stream": chat_request.stream,
            "conversation_id": chat_request.conversation_id
        }
        if chat_request.file_ids:
            data["file_ids"] = chat_request.file_ids
        
        background_tasks.add_task(save_message, db, chat_request.conversation_id, "user", chat_request.query)
        
        result = await make_api_call("conversation/runs", data=data, timeout=120.0)
        if result["status_code"] != 200:
            logger.error(f"API 调用错误: {result['content']}")
            raise HTTPException(status_code=result["status_code"], detail=result["content"])
        
        assistant_content = result["content"]["result"]
        background_tasks.add_task(save_message, db, chat_request.conversation_id, "assistant", assistant_content)
        
        return result["content"]
    except Exception as e:
        logger.error(f"聊天处理错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations")
async def get_conversations(db: Session = Depends(get_db)):
    """获取所有对话"""
    conversations = db.query(Conversation).all()
    return conversations

@app.get("/conversation/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str, db: Session = Depends(get_db)):
    """获取特定对话的所有消息"""
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
    return messages




# 在处理 /asr 路的函数中
@app.post("/asr")
async def asr(file: UploadFile = File(...)):
    contents = await file.read()
    logger.debug(f"Received audio file of size: {len(contents)} bytes")
    
    try:
        text = await speech_to_text(contents)
        logger.info(f"ASR result: {text}")
        return {"text": text}
    except Exception as e:
        logger.error(f"Error in ASR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def speech_to_text(audio_data: bytes):
    url = "https://vop.baidu.com/server_api"

    token = await get_baidu_token()

    headers = {
        "Content-Type": 'application/json',
        'Accept': 'application/json'
    }

    payload = {
        "format": "pcm",
        "rate": 16000,
        "channel": 1,
        "cuid": "your_cuid",
        "token": token,
        "speech": base64.b64encode(audio_data).decode('utf-8'),
        "len": len(audio_data)
    }

    logger.debug(f"Sending request to Baidu ASR API with payload: {payload}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()  # 如果响应状态码不是2xx，引发异常
            result = response.json()
            logger.debug(f"Received response from Baidu ASR API: {result}")

            if result.get("err_no") == 0:
                if result["result"]:
                    return result["result"][0]
                else:
                    logger.warning("ASR result is empty")
                    return ""
            else:
                error_msg = f"ASR Error: {result.get('err_msg', 'Unknown error')}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise



@app.post("/tts")
async def text_to_speech_api(text: str):
    """文本转语音接口"""
    try:
        audio_data = await text_to_speech(text)
        return StreamingResponse(io.BytesIO(audio_data), media_type="audio/basic")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def text_to_speech(text: str):
    url = "http://tsn.baidu.com/text2audio"
    
    token = await get_baidu_token()
    
    params = {
        "tex": text,
        "tok": token,
        "cuid": "your_cuid",
        "ctp": 1,
        "lan": "zh",
        "spd": 5,
        "pit": 5,
        "vol": 5,
        "per": 0,
        "aue": 4  # 改为4,返回pcm-16k格式
    }
    
    response = requests.get(url, params=params)
    
    if response.headers["Content-Type"].startswith("audio/basic"):
        return response.content
    else:
        raise Exception(f"TTS错误: {response.text}")
    

# 添加新的数据模型
class ChartDataResponse(BaseModel):
    total: int
    data: List[dict]
    columns: List[str]

# 定义数据文件映射
DATA_FILES = {
    'merged_data': 'DATAMERGED-20241203-完整数据集-修复版.csv'
}

# PKL文件缓存路径
CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 添加缓存装饰器用于缓存处理后的分页数据
@lru_cache(maxsize=1000)  # 保持较大的缓存大小
def get_cached_page_data(page: int, page_size: int, search: str = None):
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    # 准备所有指标数据
    all_indicators = []
    
    # 遍历所有数据集
    for data_type, df in processed_data.items():
        for column in df.columns:
            # 优化数据处理：一次性处理时间和数值
            times = df.index.strftime('%Y-%m-%d').tolist()
            
            # 处理无效值：将 inf, -inf 和 NaN 转换为 None
            values = df[column].replace([np.inf, -np.inf], np.nan).tolist()
            values = [None if pd.isna(x) else float(x) for x in values]  # 确保数值可以被JSON序列化
            
            # 创建指标对象
            indicator = {
                'id': f"{data_type}_{column}",
                'title': column,
                'code': data_type.upper(),
                'source': '国家统计局',
                'times': times,
                'values': values
            }
            
            # 如果有搜索条件，进行过滤
            if search:
                if search.lower() not in column.lower() and search.lower() not in data_type.lower():
                    continue
            
            all_indicators.append(indicator)
    
    # 计算总数和分页数据
    total = len(all_indicators)
    page_data = all_indicators[start_idx:end_idx] if all_indicators else []
    
    return {
        "total": total,
        "data": page_data,
        "page": page,
        "page_size": page_size
    }

@app.get("/api/chart-data")
async def get_chart_data(
    page: int = Query(1, description="页码，从1开始"),
    page_size: int = Query(9, description="每页数据量"),
    search: str = Query(None, description="搜索关键词")
):
    """获取所有图表数据，支持分页和搜索"""
    try:
        # 记录开始时间
        start_time = time.time()
        logger.info(f"开始处理图表数据请求: page={page}, page_size={page_size}, search={search}")
        
        # 使用缓存获取数据
        cache_key = f"{page}_{page_size}_{search}"
        result = get_cached_page_data(page, page_size, search)
        
        # 记录处理时间
        process_time = time.time() - start_time
        logger.info(f"图表数据处理完成，耗时: {process_time:.3f}秒")
        
        # 添加处理时间到响应中
        result["process_time"] = process_time
        
        return result
        
    except Exception as e:
        logger.error(f"获取图表数据时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 添加缓存清理接口
@app.post("/api/clear-chart-cache")
async def clear_chart_cache():
    """清理图表数据缓存"""
    try:
        get_cached_page_data.cache_clear()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 添加GDP数据端点
@app.get("/api/gdp-data")
async def get_gdp_data():
    """获取完整的GDP季度数据，包含置信区间"""
    try:
        logger.info("开始获取GDP数据...")

        # 强制使用update目录下的GDP完整数据文件
        gdp_complete_file = 'update/gdp_complete_data.csv'

        if not os.path.exists(gdp_complete_file):
            # 备用文件路径
            gdp_complete_file = 'data/gdp_complete_data.csv'
            if not os.path.exists(gdp_complete_file):
                raise HTTPException(status_code=404, detail="GDP数据文件不存在")

        # 直接读取GDP完整数据文件
        df_final = pd.read_csv(gdp_complete_file, encoding='utf-8')
        # 确保date列是datetime类型
        df_final['date'] = pd.to_datetime(df_final['date'])
        # 处理confidence_interval列
        df_final['confidence_interval'] = df_final['confidence_interval'].fillna('')
        logger.info(f"使用GDP完整数据文件: {gdp_complete_file}，共 {len(df_final)} 条记录")

        # 排序数据
        df_final = df_final.sort_values('date').reset_index(drop=True)

        # 准备返回数据，处理置信区间格式
        confidence_intervals_formatted = []
        for _, row in df_final.iterrows():
            confidence_interval = row['confidence_interval']
            if pd.notna(confidence_interval) and confidence_interval != '' and confidence_interval != 0:
                try:
                    # 如果是字符串格式的数组，需要解析
                    if isinstance(confidence_interval, str) and '[' in confidence_interval:
                        import ast
                        confidence_intervals_formatted.append(ast.literal_eval(confidence_interval))
                    else:
                        # 如果是单个数值，转换为上下界数组
                        interval_value = float(confidence_interval)
                        gdp_value = float(row['gdp_value'])
                        confidence_intervals_formatted.append([
                            gdp_value - interval_value,
                            gdp_value + interval_value
                        ])
                except:
                    confidence_intervals_formatted.append(None)
            else:
                confidence_intervals_formatted.append(None)

        gdp_data = {
            'dates': df_final['date'].dt.strftime('%Y-%m-%d').tolist(),
            'quarters': df_final['quarter'].tolist(),
            'values': df_final['gdp_value'].tolist(),
            'is_predicted': df_final['is_predicted'].tolist(),
            'confidence_intervals': confidence_intervals_formatted,
            'total_records': len(df_final),
            'latest_value': float(df_final['gdp_value'].iloc[-1]),
            'latest_quarter': df_final['quarter'].iloc[-1],
            'historical_count': len(df_final[~df_final['is_predicted']]),
            'predicted_count': len(df_final[df_final['is_predicted']])
        }

        logger.info(f"GDP数据获取完成，共 {len(df_final)} 条记录，其中预测数据 {gdp_data['predicted_count']} 条")
        return gdp_data

    except Exception as e:
        logger.error(f"获取GDP数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取GDP数据失败: {str(e)}")

# 添加月度预测数据端点
@app.get("/api/monthly-prediction-data")
async def get_monthly_prediction_data(
    page: int = Query(1, description="页码，从1开始"),
    page_size: int = Query(20, description="每页数据量"),
    search: str = Query(None, description="搜索关键词")
):
    """获取月度预测数据，合并历史数据和预测数据"""
    try:
        logger.info(f"开始获取月度预测数据: page={page}, page_size={page_size}, search={search}")

        # 读取完整合并数据文件
        merged_file = 'update/月度数据完整合并结果.csv'
        if not os.path.exists(merged_file):
            raise HTTPException(status_code=404, detail="月度数据完整合并文件不存在")

        # 尝试不同编码读取文件
        df = None
        for encoding in ['utf-8', 'gbk', 'gb2312']:
            try:
                df = pd.read_csv(merged_file, encoding=encoding)
                logger.info(f"完整合并数据使用 {encoding} 编码读取成功，形状: {df.shape}")
                break
            except UnicodeDecodeError:
                continue

        if df is None:
            raise HTTPException(status_code=500, detail="无法读取月度数据完整合并文件")

        # 处理数据
        df = df.dropna(how='all')  # 删除全空行

        # 检查第一列的名称，可能是 'timestamp' 或 'date' 或 '指标名称'
        time_column = df.columns[0]
        if time_column not in ['timestamp', 'date', '指标名称']:
            raise HTTPException(status_code=500, detail=f"时间列名称错误: {time_column}")

        # 如果时间列是 '指标名称'，需要特殊处理日期格式
        if time_column == '指标名称':
            # 将 '2024M6' 格式转换为 '2024-06'
            df[time_column] = df[time_column].str.replace('M', '-', regex=False)

        df[time_column] = pd.to_datetime(df[time_column])

        # 获取时间列和数据列
        data_columns = df.columns[1:]  # 排除时间列

        # 创建指标数据
        indicators = []

        for i, column in enumerate(data_columns):
            # 找到该列第一个非空值的位置
            first_valid_idx = df[column].first_valid_index()
            if first_valid_idx is None:
                continue  # 如果该列完全没有数据，跳过

            # 从第一个非空值开始处理数据
            column_data = df.loc[first_valid_idx:].copy()

            times = []
            values = []
            is_predicted = []

            for _, row in column_data.iterrows():
                # 只处理非空值
                if pd.notna(row[column]):
                    date_str = row[time_column].strftime('%Y-%m-%d')
                    times.append(date_str)

                    # 处理数值格式：去除逗号分隔符和空格，并检查预测标记
                    value_str = str(row[column]).strip()
                    is_pred = False

                    # 调试日志：记录2026年数据处理
                    if '2026' in date_str:
                        logger.info(f"处理2026年数据: {date_str}, 原始值: {value_str}, 列名: {column}")

                    if not value_str or value_str.lower() == 'nan':
                        if '2026' in date_str:
                            logger.info(f"跳过2026年数据(空值): {date_str}")
                        times.pop()
                        continue

                    # 检查并处理(预测)标记
                    if '(预测)' in value_str:
                        is_pred = True
                        value_str = value_str.replace('(预测)', '').strip()

                    # 移除逗号并尝试转换为浮点数
                    try:
                        clean_value = value_str.replace(',', '')
                        if not clean_value:
                            if '2026' in date_str:
                                logger.info(f"跳过2026年数据(清理后为空): {date_str}")
                            times.pop()
                            continue
                        float_value = float(clean_value)
                        values.append(float_value)

                        # 调试日志：记录2026年数据成功处理
                        if '2026' in date_str:
                            logger.info(f"成功处理2026年数据: {date_str} = {float_value}")

                    except (ValueError, TypeError) as e:
                        # 如果转换失败，跳过这个数据点
                        if '2026' in date_str:
                            logger.info(f"跳过2026年数据(转换失败): {date_str}, 错误: {e}")
                        times.pop()
                        continue

                    is_predicted.append(is_pred)

            # 如果该列没有任何有效数据，跳过
            if len(times) == 0:
                continue

            # 创建指标对象
            indicator = {
                'id': f'monthly_merged_{i}',
                'title': column,
                'code': 'MONTHLY_MERGED',
                'source': '历史+预测数据',
                'times': times,
                'values': values,
                'is_predicted': is_predicted
            }

            # 如果有搜索条件，进行过滤
            if search and search.strip():
                if search.lower() not in column.lower():
                    continue

            indicators.append(indicator)

        # 4. 分页处理
        total = len(indicators)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_indicators = indicators[start_idx:end_idx]

        result = {
            'data': page_indicators,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

        logger.info(f"合并数据完成，共 {total} 个指标，返回 {len(page_indicators)} 个")
        return result

    except Exception as e:
        logger.error(f"获取月度预测数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取月度预测数据失败: {str(e)}")

# 添加首页关键指标数据端点
@app.get("/api/key-indicators")
async def get_key_indicators():
    """获取首页关键经济指标数据"""
    try:
        logger.info("开始获取关键经济指标数据...")

        # 获取当前时间信息
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        # 经济数据通常滞后发布，需要获取实际可用的最新数据时间点
        # GDP季度数据：滞后1个季度发布
        # 月度数据：滞后1个月发布

        # 确定可获得的最新季度数据
        if current_month <= 3:
            # 1-3月，最新季度数据是去年Q4
            latest_quarter = f"{current_year-1}Q4"
        elif current_month <= 6:
            # 4-6月，最新季度数据是今年Q1
            latest_quarter = f"{current_year}Q1"
        elif current_month <= 9:
            # 7-9月，最新季度数据是今年Q2
            latest_quarter = f"{current_year}Q2"
        else:
            # 10-12月，最新季度数据是今年Q3
            latest_quarter = f"{current_year}Q3"

        # 确定可获得的最新月度数据
        if current_month == 1:
            # 1月，最新月度数据是去年12月
            latest_month_year = current_year - 1
            latest_month_num = 12
        else:
            # 其他月份，最新月度数据是上个月
            latest_month_year = current_year
            latest_month_num = current_month - 1

        latest_month_str = f"{latest_month_year}-{latest_month_num:02d}"

        logger.info(f"当前时间: {current_date.strftime('%Y-%m-%d')}")
        logger.info(f"最新可用季度数据: {latest_quarter}")
        logger.info(f"最新可用月度数据: {latest_month_str}")

        # 1. 获取GDP数据 - 返回最新可用季度的数据
        gdp_file = 'data/gdp_complete_data.csv'
        gdp_data = None
        if os.path.exists(gdp_file):
            df_gdp = pd.read_csv(gdp_file, encoding='utf-8')

            # 查找最新可用季度的数据
            latest_quarter_data = df_gdp[df_gdp['quarter'] == latest_quarter]
            if not latest_quarter_data.empty:
                # 找到最新可用季度数据
                row = latest_quarter_data.iloc[-1]  # 如果有多行，取最后一行
                gdp_data = {
                    'name': 'GDP不变价:当季同比',
                    'value': float(row['gdp_value']),
                    'quarter': row['quarter'],
                    'unit': '%',
                    'is_predicted': bool(row['is_predicted'])
                }
                logger.info(f"找到最新可用季度 {latest_quarter} 的GDP数据: {gdp_data['value']}%")
            else:
                # 如果没找到目标季度，查找最近的季度数据
                logger.warning(f"未找到目标季度 {latest_quarter} 的GDP数据，使用最新可用数据")
                latest_row = df_gdp.iloc[-1]
                gdp_data = {
                    'name': 'GDP不变价:当季同比',
                    'value': float(latest_row['gdp_value']),
                    'quarter': latest_row['quarter'],
                    'unit': '%',
                    'is_predicted': bool(latest_row['is_predicted'])
                }

        # 2. 获取其他月度指标数据 - 返回最新可用月份的数据
        monthly_indicators = []

        # 优先使用含区间的月度数据文件
        monthly_file_with_interval = 'update/月度关键数据预测结果含区间.csv'
        monthly_file_original = 'update/月度关键数据预测结果.csv'
        merged_file = 'data/DATAMERGED-20241203-完整数据集-修复版.csv'

        # 按优先级尝试读取文件
        df_monthly = None
        data_source = None

        # 1. 优先尝试含区间的文件
        if os.path.exists(monthly_file_with_interval):
            for encoding in ['utf-8', 'gbk', 'gb2312']:
                try:
                    df_monthly = pd.read_csv(monthly_file_with_interval, encoding=encoding)
                    data_source = 'interval'
                    logger.info(f"使用含区间数据文件，编码: {encoding}，形状: {df_monthly.shape}")
                    break
                except UnicodeDecodeError:
                    continue

        # 2. 如果含区间文件不存在或读取失败，尝试原始文件
        if df_monthly is None and os.path.exists(monthly_file_original):
            for encoding in ['utf-8', 'gbk', 'gb2312']:
                try:
                    df_monthly = pd.read_csv(monthly_file_original, encoding=encoding)
                    data_source = 'original'
                    logger.info(f"使用原始数据文件，编码: {encoding}，形状: {df_monthly.shape}")
                    break
                except UnicodeDecodeError:
                    continue

        # 3. 最后尝试合并文件
        if df_monthly is None and os.path.exists(merged_file):
            df_monthly = pd.read_csv(merged_file, encoding='utf-8')
            df_monthly['date'] = pd.to_datetime(df_monthly['date'])
            df_monthly = df_monthly.sort_values('date')
            data_source = 'merged'
            logger.info(f"使用合并数据文件，形状: {df_monthly.shape}")

        if df_monthly is not None and not df_monthly.empty:
            # 查找最新可用月份的数据，而不是最新一行
            target_row = None
            target_date = latest_month_str

            # 根据数据源类型查找最新可用月份数据
            if data_source == 'merged':
                # 对于合并文件，直接按日期查找
                df_monthly['date'] = pd.to_datetime(df_monthly['date'])
                target_month_data = df_monthly[df_monthly['date'].dt.strftime('%Y-%m') == latest_month_str]
                if not target_month_data.empty:
                    target_row = target_month_data.iloc[-1]  # 如果有多行，取最后一行
                    target_date = target_row['date'].strftime('%Y-%m')
                    logger.info(f"找到最新可用月份 {latest_month_str} 的数据")
                else:
                    logger.warning(f"未找到最新可用月份 {latest_month_str} 的数据，使用最新可用数据")
                    target_row = df_monthly.iloc[-1]
                    target_date = target_row['date'].strftime('%Y-%m')
            else:
                # 对于其他文件格式，需要解析第一列的日期
                found_target_month = False
                for idx, row in df_monthly.iterrows():
                    date_raw = row.iloc[0]  # 第一列是日期
                    if isinstance(date_raw, str):
                        try:
                            parsed_date = None
                            if 'M' in date_raw:
                                # 处理 2025M06 格式
                                year, month = date_raw.split('M')
                                parsed_date = f"{year}-{month.zfill(2)}"
                            elif '/' in date_raw:
                                # 处理 2025/6/30 格式
                                parts = date_raw.split('/')
                                if len(parts) >= 2:
                                    parsed_date = f"{parts[0]}-{parts[1].zfill(2)}"
                            else:
                                parsed_date = pd.to_datetime(date_raw).strftime('%Y-%m')

                            if parsed_date == latest_month_str:
                                target_row = row
                                target_date = parsed_date
                                found_target_month = True
                                logger.info(f"找到最新可用月份 {latest_month_str} 的数据")
                                break
                        except:
                            continue

                if not found_target_month:
                    logger.warning(f"未找到最新可用月份 {latest_month_str} 的数据，使用最新可用数据")
                    target_row = df_monthly.iloc[-1]
                    # 解析最新数据的日期
                    latest_date_raw = target_row.iloc[0]
                    if isinstance(latest_date_raw, str):
                        try:
                            if 'M' in latest_date_raw:
                                year, month = latest_date_raw.split('M')
                                target_date = f"{year}-{month.zfill(2)}"
                            elif '/' in latest_date_raw:
                                parts = latest_date_raw.split('/')
                                if len(parts) >= 2:
                                    target_date = f"{parts[0]}-{parts[1].zfill(2)}"
                            else:
                                target_date = pd.to_datetime(latest_date_raw).strftime('%Y-%m')
                        except:
                            target_date = str(latest_date_raw)

            # 如果找到了目标行数据，处理各个指标
            if target_row is not None:
                # 定义关键指标映射
                key_indicators_mapping = [
                    {'column': '中国:社会消费品零售总额:当月同比', 'name': '社会消费品零售总额', 'unit': '%'},
                    {'column': '中国:CPI:当月同比', 'name': 'CPI', 'unit': '%'},
                    {'column': '中国:PPI:全部工业品:当月同比', 'name': 'PPI', 'unit': '%'},
                    {'column': '中国:工业增加值:规模以上工业企业:当月同比', 'name': '工业增加值', 'unit': '%'},
                    {'column': '固定资产投资完成额:累计同比', 'name': '固定资产投资', 'unit': '%'},
                    {'column': '中国:出口金额:当月同比', 'name': '出口金额', 'unit': '%'},
                    {'column': '中国:进口金额:当月同比', 'name': '进口金额', 'unit': '%'},
                    {'column': '房地产开发投资完成额:累计同比', 'name': '房地产投资', 'unit': '%'},
                    {'column': '中国:M2:同比', 'name': 'M2货币供应量', 'unit': '%'},
                    {'column': '中国:社会融资规模:当月值', 'name': '社会融资规模', 'unit': '亿元'}
                ]

                for indicator in key_indicators_mapping:
                    column = indicator['column']
                    if column in df_monthly.columns:
                        value = target_row[column]
                        if pd.notna(value):
                            # 判断是否为预测数据 - 基于目标日期判断
                            if data_source == 'merged':
                                is_predicted = pd.to_datetime(target_date).year >= 2025 and pd.to_datetime(target_date).month >= 6
                            else:
                                # 2025年6月及以后为预测数据
                                year_month = target_date.split('-')
                                if len(year_month) == 2:
                                    year, month = int(year_month[0]), int(year_month[1])
                                    is_predicted = year > 2025 or (year == 2025 and month >= 6)
                                else:
                                    is_predicted = '2025' in str(target_date)

                            # 处理置信区间（仅当使用含区间文件时）
                            confidence_interval = None
                            if data_source == 'interval':
                                variation_column = f"{column}_variation"
                                if variation_column in df_monthly.columns:
                                    variation = target_row[variation_column]
                                    if pd.notna(variation):
                                        confidence_interval = [float(value) - float(variation), float(value) + float(variation)]

                            monthly_indicators.append({
                                'name': indicator['name'],
                                'value': float(value),
                                'date': target_date,
                                'unit': indicator['unit'],
                                'is_predicted': is_predicted,
                                'confidence_interval': confidence_interval
                            })

                            logger.info(f"处理指标 {indicator['name']}: {value} ({target_date}), 预测数据: {is_predicted}")
            else:
                logger.warning("未找到有效的月度数据行")

        # 3. 组合返回数据
        result = {
            'gdp': gdp_data,
            'monthly_indicators': monthly_indicators,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_indicators': len(monthly_indicators) + (1 if gdp_data else 0)
        }

        logger.info(f"关键指标数据获取完成，共 {result['total_indicators']} 个指标")
        return result

    except Exception as e:
        logger.error(f"获取关键指标数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取关键指标数据失败: {str(e)}")

# 添加关键指标时间序列数据端点
@app.get("/api/key-indicators-series")
async def get_key_indicators_series():
    """获取关键经济指标的完整时间序列数据"""
    try:
        logger.info("开始获取关键指标时间序列数据...")

        # 优先使用含区间的月度数据文件
        monthly_file_with_interval = 'update/月度关键数据预测结果含区间.csv'
        
        df_monthly = None
        
        # 尝试读取含区间的文件
        if os.path.exists(monthly_file_with_interval):
            for encoding in ['utf-8', 'gbk', 'gb2312']:
                try:
                    df_monthly = pd.read_csv(monthly_file_with_interval, encoding=encoding)
                    logger.info(f"使用含区间数据文件，编码: {encoding}，形状: {df_monthly.shape}")
                    break
                except UnicodeDecodeError:
                    continue

        if df_monthly is None or df_monthly.empty:
            raise HTTPException(status_code=404, detail="未找到关键指标数据文件")

        # 定义关键指标映射
        key_indicators_mapping = [
            {'column': '中国:社会消费品零售总额:当月同比', 'name': '社会消费品零售总额', 'unit': '%'},
            {'column': '中国:CPI:当月同比', 'name': 'CPI', 'unit': '%'},
            {'column': '中国:PPI:全部工业品:当月同比', 'name': 'PPI', 'unit': '%'},
            {'column': '中国:工业增加值:规模以上工业企业:当月同比', 'name': '工业增加值', 'unit': '%'},
            {'column': '固定资产投资完成额:累计同比', 'name': '固定资产投资', 'unit': '%'},
            {'column': '中国:出口金额:当月同比', 'name': '出口金额', 'unit': '%'},
            {'column': '中国:进口金额:当月同比', 'name': '进口金额', 'unit': '%'},
            {'column': '房地产开发投资完成额:累计同比', 'name': '房地产投资', 'unit': '%'},
            {'column': '固定资产投资完成额:制造业:累计同比', 'name': '制造业投资', 'unit': '%'},
            {'column': '固定资产投资完成额:基础设施建设:累计同比', 'name': '基础设施投资', 'unit': '%'},
            {'column': '中国:M2:同比', 'name': 'M2货币供应量', 'unit': '%'},
            {'column': '中国:社会融资规模:当月值', 'name': '社会融资规模', 'unit': '亿元'}
        ]

        # 处理时间序列数据
        indicators_series = []
        
        for indicator in key_indicators_mapping:
            column = indicator['column']
            if column in df_monthly.columns:
                # 获取该指标的所有数据
                series_data = []
                
                for idx, row in df_monthly.iterrows():
                    timestamp_raw = row.iloc[0]  # 第一列是时间戳
                    value = row[column]
                    
                    if pd.notna(value):
                        # 处理时间格式
                        try:
                            if isinstance(timestamp_raw, str):
                                if '/' in timestamp_raw:
                                    # 处理 2025/6/30 格式
                                    parts = timestamp_raw.split('/')
                                    if len(parts) >= 2:
                                        date_str = f"{parts[0]}-{parts[1].zfill(2)}"
                                elif 'M' in timestamp_raw:
                                    # 处理 2025M06 格式
                                    year, month = timestamp_raw.split('M')
                                    date_str = f"{year}-{month.zfill(2)}"
                                else:
                                    date_str = pd.to_datetime(timestamp_raw).strftime('%Y-%m')
                            else:
                                date_str = pd.to_datetime(timestamp_raw).strftime('%Y-%m')
                        except:
                            date_str = str(timestamp_raw)
                        
                        # 判断是否为预测数据（2025年6月及以后）
                        try:
                            year, month = date_str.split('-')
                            year = int(year)
                            month = int(month)
                            is_predicted = year > 2025 or (year == 2025 and month >= 6)
                        except:
                            is_predicted = '2025' in date_str
                        
                        # 处理置信区间
                        confidence_interval = None
                        variation_column = f"{column}_variation"
                        if variation_column in df_monthly.columns:
                            variation = row[variation_column]
                            if pd.notna(variation):
                                confidence_interval = [
                                    float(value) - float(variation), 
                                    float(value) + float(variation)
                                ]
                        
                        series_data.append({
                            'date': date_str,
                            'value': float(value),
                            'is_predicted': is_predicted,
                            'confidence_interval': confidence_interval
                        })
                
                if series_data:
                    # 按日期排序
                    series_data.sort(key=lambda x: x['date'])
                    
                    indicators_series.append({
                        'name': indicator['name'],
                        'column': column,
                        'unit': indicator['unit'],
                        'data': series_data,
                        'total_points': len(series_data)
                    })

        # 组合返回数据
        result = {
            'indicators': indicators_series,
            'total_indicators': len(indicators_series),
            'data_source': '月度关键数据预测结果含区间.csv',
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        logger.info(f"关键指标时间序列数据获取完成，共 {len(indicators_series)} 个指标")
        return result

    except Exception as e:
        logger.error(f"获取关键指标时间序列数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取关键指标时间序列数据失败: {str(e)}")

# 添加新的路由处理函数
@app.post("/api/gdp-analysis")
async def analyze_gdp(prediction_value: float = Body(...)):
    async def generate_analysis():
        apis = [
            {"name": "GDP数据分析流1", "app_id": "31e13499-bc62-454e-9726-10318869d707"},
            {"name": "GDP数据分析流2", "app_id": "4ce0fe40-954f-4883-bd37-ce9c3e4a326d"},
            {"name": "GDP数据分析流3", "app_id": "72cbf1cd-2dac-479d-8000-3e2c5fe04b3a"},
            {"name": "GDP数据分析流4", "app_id": "01430645-90a5-4032-97e8-b9630e1fc579"}
        ]
        
        async with aiohttp.ClientSession() as session:
            # 先处理第一个API
            first_result = await process_api(session, apis[0]["app_id"], prediction_value, apis[0]["name"])
            yield json.dumps({
                "type": "api_result",
                "index": 1,
                "data": first_result
            }) + "\n"
            
            # 并发处理剩余的API
            remaining_tasks = [
                process_api(session, api["app_id"], prediction_value, api["name"])
                for api in apis[1:]
            ]
            
            # 按顺序获取并返回剩余结果
            for i, result in enumerate(await asyncio.gather(*remaining_tasks), 2):
                yield json.dumps({
                    "type": "api_result",
                    "index": i,
                    "data": result
                }) + "\n"

    return StreamingResponse(
        generate_analysis(),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

# 添加辅助函数
async def get_conversation_id(session, app_id):
    """获取对话ID"""
    url = "https://qianfan.baidubce.com/v2/app/conversation"
    
    payload = {
        "app_id": app_id
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Appbuilder-Authorization": "Bearer bce-v3/ALTAK-YLij17TdPMsg11izg9HAn/3168a0aea58dfbbe24023103d4dec3830d225aca"
    }
    
    async with session.post(url, json=payload, headers=headers) as response:
        return await response.json()

async def get_analysis_result(session, app_id, conversation_id, prediction_value):
    """获取分析结果"""
    url = "https://qianfan.baidubce.com/v2/app/conversation/runs"
    
    payload = {
        "app_id": app_id,
        "query": str(prediction_value),
        "conversation_id": conversation_id,
        "stream": False
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Appbuilder-Authorization": "Bearer bce-v3/ALTAK-YLij17TdPMsg11izg9HAn/3168a0aea58dfbbe24023103d4dec3830d225aca"
    }
    
    async with session.post(url, json=payload, headers=headers) as response:
        return await response.json()

async def process_api(session, app_id, prediction_value, api_name):
    """处理单个API的完整流程"""
    try:
        # 获取conversation_id
        conv_result = await get_conversation_id(session, app_id)
        conversation_id = conv_result.get("conversation_id")
        
        # 获取分析结果
        result = await get_analysis_result(session, app_id, conversation_id, prediction_value)
        return {
            "api_name": api_name,
            "app_id": app_id,
            "result": result
        }
    except Exception as e:
        logger.error(f"处理API {api_name} 时发生错误: {str(e)}")
        return {
            "api_name": api_name,
            "app_id": app_id,
            "error": str(e)
        }

# 添加宏观经济整体分析端点
@app.post("/api/macro-analysis")
async def analyze_macro_economy():
    """获取所有关键经济指标并进行综合宏观分析"""
    try:
        logger.info("开始宏观经济整体分析...")
        
        # 1. 获取所有关键经济指标的最新数据
        key_indicators = await get_key_indicators()
        logger.info(f"获取到的关键指标数据: GDP={key_indicators.get('gdp')}, 月度指标数量={len(key_indicators.get('monthly_indicators', []))}")
        
        # 2. 构建分析输入文本
        analysis_input = "请对以下中国宏观经济指标进行深度综合分析：\n\n"
        
        # 添加GDP数据
        if key_indicators['gdp']:
            gdp = key_indicators['gdp']
            analysis_input += f"GDP增长率({gdp['quarter']}): {gdp['value']}%\n"
        
        # 添加月度指标数据
        for indicator in key_indicators['monthly_indicators']:
            analysis_input += f"{indicator['name']}({indicator['date']}): {indicator['value']}{indicator['unit']}"
            if indicator.get('is_predicted'):
                analysis_input += " [预测值]"
            analysis_input += "\n"
        
        analysis_input += "\n请使用Markdown格式，从以下角度进行深度分析：\n\n"
        analysis_input += "## 1. 宏观经济运行总体评估\n"
        analysis_input += "请综合评价当前经济运行状况，包括增长态势、结构特征、主要亮点等。\n\n"
        analysis_input += "## 2. 经济增长动能分析\n"
        analysis_input += "### GDP增长表现\n"
        analysis_input += "### 三驾马车协调性\n"
        analysis_input += "- 消费：分析社会消费品零售总额数据\n"
        analysis_input += "- 投资：分析固定资产投资、房地产投资、制造业投资等\n"
        analysis_input += "- 出口：分析进出口贸易数据\n\n"
        analysis_input += "## 3. 产业运行特征\n"
        analysis_input += "### 工业生产\n"
        analysis_input += "### 房地产市场\n"
        analysis_input += "### 新兴产业发展\n\n"
        analysis_input += "## 4. 价格走势分析\n"
        analysis_input += "### 通胀形势（CPI/PPI）\n"
        analysis_input += "### 价格传导机制\n\n"
        analysis_input += "## 5. 金融环境评估\n"
        analysis_input += "### 货币供应（M2）\n"
        analysis_input += "### 社会融资规模\n"
        analysis_input += "### 流动性状况\n\n"
        analysis_input += "## 6. 风险因素与挑战\n"
        analysis_input += "请列出主要风险点，每个风险点用###标题。\n\n"
        analysis_input += "## 7. 政策建议\n"
        analysis_input += "请提供具体可行的政策建议，使用有序列表。\n\n"
        analysis_input += "## 8. 展望与结论\n"
        analysis_input += "请对未来经济走势进行预判，并给出结论性观点。\n"
        
        logger.info(f"构建的分析输入文本长度: {len(analysis_input)}")
        
        # 3. 调用AI分析（使用第一个GDP分析API作为宏观分析API）
        app_id = "31e13499-bc62-454e-9726-10318869d707"  # GDP数据分析流1
        
        async with aiohttp.ClientSession() as session:
            # 获取对话ID
            conv_result = await get_conversation_id(session, app_id)
            logger.info(f"创建对话响应: {json.dumps(conv_result, ensure_ascii=False)[:200]}")
            conversation_id = conv_result.get("conversation_id")
            
            if not conversation_id:
                logger.error(f"无法获取conversation_id，响应: {conv_result}")
                raise HTTPException(status_code=500, detail="无法创建分析会话")
            
            # 获取分析结果
            url = "https://qianfan.baidubce.com/v2/app/conversation/runs"
            
            payload = {
                "app_id": app_id,
                "query": analysis_input,
                "conversation_id": conversation_id,
                "stream": False
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-Appbuilder-Authorization": "Bearer bce-v3/ALTAK-YLij17TdPMsg11izg9HAn/3168a0aea58dfbbe24023103d4dec3830d225aca"
            }
            
            logger.info(f"发送分析请求，输入长度: {len(analysis_input)} 字符")
            logger.info(f"请求payload: app_id={app_id}, conversation_id={conversation_id}, stream=False")
            
            async with session.post(url, json=payload, headers=headers) as response:
                result = await response.json()
                
                if response.status != 200:
                    logger.error(f"AI分析API返回错误: {result}")
                    raise HTTPException(status_code=500, detail="AI分析失败")
                
                # 提取分析结果
                logger.info(f"AI分析API响应: {json.dumps(result, ensure_ascii=False)[:500]}")
                # 豆包API返回的分析内容在answer字段中
                analysis_content = result.get("answer", "")

                if not analysis_content:
                    # 如果没有answer字段，尝试其他可能的字段
                    analysis_content = result.get("result", "") or result.get("response", "") or result.get("content", "")
                    logger.warning(f"未在answer字段找到内容，尝试其他字段，最终内容长度: {len(analysis_content)}")
                else:
                    logger.info(f"成功获取分析内容，长度: {len(analysis_content)} 字符")
                
                # 构建返回结果
                return {
                    "status": "success",
                    "data": {
                        "analysis": analysis_content,
                        "indicators_count": len(key_indicators['monthly_indicators']) + (1 if key_indicators['gdp'] else 0),
                        "update_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "data_source": "实时分析"
                    }
                }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"宏观经济分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"宏观经济分析失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("启动服务器")
    uvicorn.run(app, host="0.0.0.0", port=8888)
