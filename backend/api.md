# 后端API文档

## 基础信息
- 基础URL: `http://127.0.0.1:8888`
- 所有POST请求的Content-Type应该设置为 `application/json`，除非特别说明
- 文件上传接口需要使用 `multipart/form-data`

## API 列表

### 1. 对话管理

#### 1.1 创建新对话
- **接口**: `POST /conversation`
- **请求参数**: 无
- **响应示例**:
```json
{
    "conversation_id": "conv_123456789",
    "created_at": "2024-01-20T10:00:00"
}
```

#### 1.2 获取所有对话
- **接口**: `GET /conversations`
- **请求参数**: 无
- **响应示例**:
```json
[
    {
        "conversation_id": "conv_123456789",
        "created_at": "2024-01-20T10:00:00"
    },
    {
        "conversation_id": "conv_987654321",
        "created_at": "2024-01-20T11:00:00"
    }
]
```

#### 1.3 获取对话消息历史
- **接口**: `GET /conversation/{conversation_id}/messages`
- **请求参数**: conversation_id (路径参数)
- **响应示例**:
```json
[
    {
        "role": "user",
        "content": "你好",
        "created_at": "2024-01-20T10:00:00"
    },
    {
        "role": "assistant",
        "content": "你好！有什么我可以帮你的吗？",
        "created_at": "2024-01-20T10:00:01"
    }
]
```

### 2. 聊天功能

#### 2.1 发送聊天消息（普通模式）
- **接口**: `POST /chat`
- **请求参数**:
```json
{
    "query": "你好",
    "conversation_id": "conv_123456789",
    "stream": false,
    "file_ids": ["file_1", "file_2"]  // 可选
}
```
- **响应示例**:
```json
{
    "response": "你好！有什么我可以帮你的吗？",
    "conversation_id": "conv_123456789"
}
```

#### 2.2 发送聊天消息（流式响应）
- **接口**: `POST /stream`
- **请求参数**:
```json
{
    "conversation_id": "conv_123456789",
    "query": "你好",
    "file_ids": ["file_1", "file_2"]  // 可选
}
```
- **响应**: 
  - Content-Type: text/event-stream
  - 每个事件包含部分响应文本
  - 示例：
```
data: {"text": "你"}
data: {"text": "好"}
data: {"text": "！"}
data: [DONE]
```

### 3. 文件处理

#### 3.1 上传文件
- **接口**: `POST /upload`
- **请求格式**: multipart/form-data
- **请求参数**:
  - file: 文件数据
  - app_id: 应用ID
  - conversation_id: 对话ID
- **响应示例**:
```json
{
    "file_id": "file_123456789",
    "filename": "example.txt",
    "status": "success"
}
```

### 4. 语音功能

#### 4.1 语音识别（ASR）
- **接口**: `POST /asr`
- **请求格式**: multipart/form-data
- **请求参数**:
  - file: 音频文件（支持格式：wav, pcm, amr）
- **响应示例**:
```json
{
    "text": "识别出的文本内容"
}
```

#### 4.2 文本转语音（TTS）
- **接口**: `POST /tts`
- **请求参数**:
```json
{
    "text": "需要转换为语音的文本"
}
```
- **响应**: 
  - Content-Type: audio/mp3
  - 响应体为音频文件数据流

## 错误响应
所有接口在发生错误时会返回以下格式：
```json
{
    "detail": "错误信息描述"
}
```

## 注意事项
1. 文件上传大小限制为10MB
2. 语音识别支持的音频格式：wav、pcm、amr
3. 流式响应需要客户端支持 EventSource 或类似机制
4. 所有时间戳采用 ISO 8601 格式
