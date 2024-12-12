# 对话 API 前端集成文档

## 1. 概述

本文档描述了对话 API 的主要功能和使用方法。该 API 提供了创建对话、发送消息和接收流式响应的能力，适用于构建实时对话应用。

## 2. API 端点

### 2.1 创建新对话

- **端点**: `/conversation`
- **方法**: POST
- **描述**: 创建一个新的对话会话
- **响应**: 返回一个包含 `conversation_id` 的 JSON 对象

### 2.2 发送消息和接收流式响应

- **端点**: `/stream`
- **方法**: POST
- **描述**: 发送用户消息并接收流式 AI 响应
- **请求体**:
  ```json
  {
    "conversation_id": "string",
    "query": "string",
    "file_ids": ["string"] // 可选
  }
  ```
- **响应**: 返回一个 text/event-stream 流

### 2.3 获取对话历史

- **端点**: `/conversation/{conversation_id}/messages`
- **方法**: GET
- **描述**: 获取特定对话的所有消息历史
- **响应**: 返回一个消息数组

## 3. 使用流程

1. 创建新对话：调用 `/conversation` 端点获取 `conversation_id`
2. 发送消息：使用获得的 `conversation_id` 调用 `/stream` 端点
3. 处理流式响应：解析从 `/stream` 返回的事件流
4. （可选）获取历史：使用 `/conversation/{conversation_id}/messages` 获取对话历史

## 4. 流式响应处理

前端应该准备好处理来自 `/stream` 端点的服务器发送事件（SSE）。每个事件都包含 AI 响应的一部分。

示例代码（JavaScript）:

```javascript
const eventSource = new EventSource('/stream');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // 处理接收到的数据片段
  console.log(data.text);
};

eventSource.onerror = (error) => {
  console.error('EventSource failed:', error);
  eventSource.close();
};
```

## 5. 注意事项

- 处理流式响应时，确保有适当的错误处理机制
- 大型对话可能会产生大量数据，请考虑如何在客户端有效管理这些数据

## 6. 错误处理

API 使用标准的 HTTP 状态码。在处理响应时，请检查状态码并相应地处理错误。

