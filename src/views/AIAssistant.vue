<template>
  <div class="min-h-screen bg-gray-50">
    <TheHeader />
    
    <main class="bg-background min-h-screen pt-12 pb-12">
      <!-- 左右两栏布局容器 -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex gap-8">
        <!-- 左侧历史消息栏 -->
        <div class="w-80 bg-white rounded-lg shadow">
          <h2 class="font-medium text-lg mb-4 bg-gray-50 p-3 text-left">历史消息</h2>
          <div class="space-y-2 px-2">
            <!-- 新会话按钮 -->
            <div 
              @click="createNewConversation" 
              class="flex items-center text-black cursor-pointer hover:bg-blue-50 p-4 rounded"
            >
              <div class="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center mr-2">
                <i class="fas fa-plus text-sm"></i>
              </div>
              <span>新会话</span>
            </div>

            <!-- 历史消息列表 -->
            <div class="space-y-4 mt-4">
              <div v-if="conversations.length > 0" class="space-y-2">
                <div 
                  v-for="conv in conversations" 
                  :key="conv.conversation_id"
                  class="flex items-center justify-between p-2 hover:bg-blue-50 rounded cursor-pointer group"
                  :class="{ 'bg-blue-50': currentConversationId === conv.conversation_id }"
                  @click="() => {
                    currentConversationId = conv.conversation_id;
                    fetchConversationMessages(conv.conversation_id);
                  }"
                >
                  <div class="flex items-center flex-1">
                    <div class="w-6 h-6 flex-shrink-0 mr-3">
                      <i class="far fa-comment-dots" :class="currentConversationId === conv.conversation_id ? 'text-blue-500' : 'text-gray-400'"></i>
                    </div>
                    <span class="text-sm text-gray-600 truncate">{{ conv.title || '新对话' }}</span>
                  </div>
                  <button 
                    @click.stop="deleteConversation(conv.conversation_id)"
                    class="p-1 hover:bg-red-100 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <i class="fas fa-trash text-red-500 text-sm"></i>
                  </button>
                </div>
              </div>
              <div v-else class="text-center text-gray-500 py-4">
                暂无历史对话
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧主要对话区域 -->
        <div class="flex-1">
          <div class="bg-white rounded-lg shadow-sm p-6 flex flex-col h-[calc(100vh-8rem)]">
            <!-- 标题区域 -->
            <div class="flex items-center mb-8">
              <img src="@/assets/logo.svg" alt="logo" class="h-12 w-12 mr-3">
              <div>
                <h1 class="text-xl font-medium text-gray-900 text-left">社科数智</h1>
                <p class="text-gray-500 text-sm">Social Science Data Artificial Intelligence (SSDAI)</p>
              </div>
            </div>

            <!-- 对话区域 -->
            <div class="flex-1 overflow-y-auto mb-6 space-y-6">
              <template v-if="messages.length > 0">
                <div v-for="(message, index) in messages" :key="index" class="flex items-start space-x-3" :class="{ 'justify-end': message.role === 'user' }">
                  

                  
                  <!-- AI消息 -->
                  <template v-if="message.role === 'assistant'">
                    <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center flex-shrink-0">
                      <i class="fas fa-robot text-white text-lg"></i>
                    </div>
                    <div class="max-w-[80%]">
                      <div class="bg-blue-50 rounded-lg p-4 inline-block">
                        <p class="text-gray-700 whitespace-pre-wrap break-words text-left">{{ message.content }}</p>
                      </div>
                    </div>
                  </template>
    
                  <!-- 用户消息 -->
                  <template v-else>
                    <div class="max-w-[80%] ml-auto">
                      <div class="bg-blue-500 text-white rounded-lg p-4 inline-block">
                        <p class="whitespace-pre-wrap break-words text-left">{{ message.content }}</p>
                      </div>
                    </div>
                    <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                      <i class="fas fa-user text-gray-500"></i>
                    </div>
                  </template>
                </div>

                                                                  <!-- 加载动画 -->
                <div v-if="isLoading" class="flex items-start space-x-3">
                  <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center flex-shrink-0">
                    <i class="fas fa-robot text-white text-lg"></i>
                  </div>
                  <div class="max-w-[80%]">
                    <div class="bg-blue-50 rounded-lg p-4 inline-block">
                      <div class="flex space-x-2">
                        <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                        <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                        <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                      </div>
                    </div>
                  </div>
                </div>

              </template>


              
              <template v-else>
                <!-- 欢迎消息 -->
                <div class="flex items-start space-x-3">
                  <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center flex-shrink-0">
                    <i class="fas fa-robot text-white text-lg"></i>
                  </div>
                  <div class="flex-1">
                    <div class="bg-blue-50 rounded-lg p-4">
                      <p class="text-gray-700">您好，我是您的经济数据分析助手！我可以帮您找到某一年的某个行业经济趋势，与另一年的数据进行对比，并预测未来的经济形势。无论是投资规划、行业研究还是市场分析，我都能为您提供精准洞察。</p>
                      <p class="text-gray-600 mt-4 mb-2">您可以这样提问：</p>
                      <div class="space-y-2">
                        <div 
                          v-for="(example, i) in ['2020年与2023年的新能源行业趋势对比如何？', '未来三年科技行业的发展前景如何？']" 
                          :key="i"
                          @click="inputMessage = example"
                          class="bg-white p-3 rounded-lg cursor-pointer hover:bg-gray-50"
                        >
                          <p class="text-blue-500 text-left">{{ example }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </template>




            </div>

            <!-- 输入区域 -->
            <div class="border-t pt-4">
              <div class="relative">
                <textarea
                  v-model="inputMessage"
                  @keydown.enter.prevent="sendMessage"
                  rows="3"
                  class="w-full px-4 py-2 text-gray-700 bg-white rounded-lg border focus:outline-none focus:border-blue-500"
                  placeholder="输入您的问题..."
                ></textarea>
                <div class="absolute right-2 bottom-2 flex space-x-2">
                  <button
                    @click="sendMessage"
                    :disabled="!inputMessage.trim() || isLoading"
                    class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <i class="fas fa-paper-plane mr-1"></i>
                    发送
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <TheFooter />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TheHeader from '@/components/TheHeader.vue'
import axios from 'axios'

// API配置
const API_BASE_URL = 'http://127.0.0.1:8888'
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 状态变量
const conversations = ref([])
const currentConversationId = ref(null)
const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)  // 添加加载状态

// 获取所有对话历史
const fetchConversations = async () => {
  try {
    const response = await axiosInstance.get('/conversations')
    conversations.value = response.data
  } catch (error) {
    console.error('获取对话历史失败:', error)
  }
}

// 创建新对话
const createNewConversation = async () => {
  try {
    const response = await axiosInstance.post('/conversation')
    currentConversationId.value = response.data.conversation_id
    messages.value = []
    await fetchConversations()
  } catch (error) {
    console.error('创建新对话失败:', error)
  }
}

// 获取特定对话的消息
const fetchConversationMessages = async (conversationId) => {
  try {
    const response = await axiosInstance.get(`/conversation/${conversationId}/messages`)
    messages.value = response.data
  } catch (error) {
    console.error('获取对话消息失败:', error)
  }
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  
  const userMessage = inputMessage.value
  inputMessage.value = '' // 清空输入框
  
  messages.value.push({
    role: 'user',
    content: userMessage
  })
  
  isLoading.value = true // 开始加载
  
  try {
    // 如果没有当前会话ID，先创建一个新会话
    if (!currentConversationId.value) {
      const convResponse = await axiosInstance.post('/conversation')
      currentConversationId.value = convResponse.data.conversation_id
    }

    // 创建一个临时的助手消息用于显示流式响应
    messages.value.push({
      role: 'assistant',
      content: ''
    })

    // 发送流式请求
    const response = await fetch(`${API_BASE_URL}/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        conversation_id: currentConversationId.value,
        query: userMessage
      })
    })

    if (!response.ok) throw new Error('Network response was not ok')

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      const chunk = decoder.decode(value)
      // 处理 SSE 格式的数据
      const lines = chunk.split('\n')
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.answer) {
              // 更新最后一条消息的内容
              messages.value[messages.value.length - 1].content += data.answer
            }
          } catch (e) {
            console.error('解析响应数据失败:', e)
          }
        }
      }
    }

  } catch (error) {
    console.error('发送消息失败:', error)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，发生了一些错误。请稍后重试。'
    })
  } finally {
    isLoading.value = false // 结束加载
  }
}

// 删除对话
const deleteConversation = async (conversationId) => {
  try {
    const response = await axiosInstance.delete(`/conversation/${conversationId}`)
    if (response.data.status === 'success') {
      await fetchConversations()
      if (currentConversationId.value === conversationId) {
        currentConversationId.value = null
        messages.value = []
      }
    } else {
      console.error('删除对话失败:', response.data)
    }
  } catch (error) {
    console.error('删除对话失败:', error)
  }
}

// 初始化
onMounted(async () => {
  try {
    await fetchConversations()
    if (!currentConversationId.value) {
      if (conversations.value.length > 0) {
        // 使用最新的对话
        const latestConversation = conversations.value[0]
        currentConversationId.value = latestConversation.conversation_id
        await fetchConversationMessages(currentConversationId.value)
      } else {
        // 如果没有现有对话，创建一个新对话
        await createNewConversation()
      }
    }
  } catch (error) {
    console.error('初始化失败:', error)
  }
})
</script>