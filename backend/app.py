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
            
            # 清理数��：移除逗号，转换为数值类型，处理无效值
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
        # 排除已经缓��的优先页面
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
    # 启动时处理所有数据
    await process_all_data()
    # 启动优先页面预缓存
    await precache_priority_pages()
    # 启动后台缓存任务
    asyncio.create_task(background_cache_task())
    # 启动保存响应的worker
    asyncio.create_task(save_responses_worker())
    yield
    # 关闭时的清理代码
    processed_data.clear()

app = FastAPI(lifespan=lifespan)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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

            # 处理数据块��累积完整响应
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

# 定义据文件映射
DATA_FILES = {
    'cy': 'DATACY20241103 - month.csv',
    'dwl': 'DATADWL-241103 - 月度 (1).csv',
    'dm_quarter': 'DATADM-20241103 - 季度.csv',
    'dm_month': 'DATADM-20241103 - 月度.csv',
    'lf': 'DATALF-20241103 - DAY.csv'
}

# PKL文件缓存路径
CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(exist_ok=True)

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

if __name__ == "__main__":
    import uvicorn
    logger.info("启动服务器")
    uvicorn.run(app, host="0.0.0.0", port=8888)
