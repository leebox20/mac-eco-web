## Backend API Documentation

### Base URL
```
http://http://120.48.150.254:8888
```

### 完整对话流程

1. **创建新对话**
```bash
# Step 1: 创建对话，获取conversation_id
curl -X POST http://http://120.48.150.254:8888/conversation

# 返回示例:
{
    "conversation_id": "conv_12345"
}
```

2. **上传文件（可选）**
```bash
# Step 2: 如果需要上传文件进行分析
curl -X POST http://http://120.48.150.254:8888/upload_file \
  -F "file=@/path/to/your/file" \
  -F "app_id=2e7137fb-9a22-4246-8593-f0a9b4fc9695" \
  -F "conversation_id=conv_12345"

# 返回示例:
{
    "file_id": "file_67890"
}
```

3. **发送消息并获取回复**
```bash
# Step 3a: 发送普通消息
curl -X POST http://http://120.48.150.254:8888/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "分析这个文件的内容",
    "conversation_id": "conv_12345",
    "file_ids": ["file_67890"],  # 可选，如果有上传文件
    "stream": false
  }'

# Step 3b: 或使用流式响应（实时返回）
curl -X POST http://http://120.48.150.254:8888/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "分析这个文件的内容",
    "conversation_id": "conv_12345",
    "file_ids": ["file_67890"],
    "stream": true
  }'
```

4. **查看对话历史**
```bash
# Step 4: 获取当前对话的所有消息
curl -X GET http://http://120.48.150.254:8888/conversation/conv_12345/messages

# 返回示例:
{
    "messages": [
        {
            "role": "user",
            "content": "分析这个文件的内容"
        },
        {
            "role": "assistant",
            "content": "根据文件内容分析..."
        }
    ]
}
```

5. **语音交互（可选）**
```bash
# Step 5a: 语音转文字
curl -X POST http://http://120.48.150.254:8888/asr \
  -F "file=@/path/to/your/voice.wav"

# Step 5b: 文字转语音
curl -X POST http://http://120.48.150.254:8888/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "AI助手的回复内容"
  }'
```

6. **结束对话**
```bash
# Step 6: 删除对话（可选）
curl -X DELETE http://http://120.48.150.254:8888/conversation/conv_12345
```

### Endpoints

#### 1. Create Conversation
Creates a new conversation session.

```bash
curl -X POST http://http://120.48.150.254:8888/conversation
```

Response:
```json
{
    "conversation_id": "string"
}
```

#### 2. Upload File
Upload a file to the conversation.

```bash
curl -X POST http://http://120.48.150.254:8888/upload_file \
  -F "file=@/path/to/your/file" \
  -F "app_id=2e7137fb-9a22-4246-8593-f0a9b4fc9695" \
  -F "conversation_id=your_conversation_id"
```

#### 3. Chat
Send a message to the chat.

```bash
# Regular chat
curl -X POST http://http://120.48.150.254:8888/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "your message",
    "conversation_id": "your_conversation_id",
    "stream": false
  }'

# Streaming chat
curl -X POST http://http://120.48.150.254:8888/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "your message",
    "conversation_id": "your_conversation_id",
    "stream": true
  }'
```

#### 4. Get Conversations
Retrieve all conversations.

```bash
curl -X GET http://http://120.48.150.254:8888/conversations
```

#### 5. Get Conversation Messages
Retrieve messages from a specific conversation.

```bash
curl -X GET http://http://120.48.150.254:8888/conversation/{conversation_id}/messages
```

#### 6. Delete Conversation
Delete a specific conversation.

```bash
curl -X DELETE http://http://120.48.150.254:8888/conversation/{conversation_id}
```

#### 7. Delete All Conversations
Clear all conversations.

```bash
curl -X DELETE http://http://120.48.150.254:8888/conversations
```

#### 8. Speech to Text (ASR)
Convert audio to text.

```bash
curl -X POST http://http://120.48.150.254:8888/asr \
  -F "file=@/path/to/your/audio.wav"
```

#### 9. Text to Speech
Convert text to speech.

```bash
curl -X POST http://http://120.48.150.254:8888/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "要转换的文本"
  }'
```

### Notes
- All endpoints return JSON responses unless specified otherwise
- File uploads support common audio and document formats
- Streaming responses use Server-Sent Events (SSE) format
- Error responses include appropriate HTTP status codes and error messages
