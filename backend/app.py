import os
import logging
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Body, BackgroundTasks, Depends
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
                
                logger.info(f"成功获取 TOKEN: {result['access_token']}; 过期时间(秒): {result['expires_in']}")
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时运行
    asyncio.create_task(save_responses_worker())
    yield
    # 关闭时运行
    # 这里可以添加清理代码，如果需要的话

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

            # 处理数据块以累积完整响应
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




# 在处理 /asr 路由的函数中
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
            response.raise_for_status()  # 如果响应状态码不是2xx，将引发异常
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
    
if __name__ == "__main__":
    import uvicorn
    logger.info("启动服务器")
    uvicorn.run(app, host="0.0.0.0", port=8000)
