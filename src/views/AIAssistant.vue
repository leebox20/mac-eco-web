<template>
  <div class="min-h-screen bg-gray-50">
    <TheHeader />
    
    <main class="bg-background min-h-screen pt-12 pb-12">
      <!-- 左右两栏布局容器 -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- 使用 grid 布局实现响应式 -->
        <div class="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-8">
          <!-- 左侧历史消息栏 -->
          <div class="bg-white rounded-lg shadow lg:block">
            <div class="flex items-center justify-between p-3 bg-gray-50 border-b border-t border-gray-200 rounded-t-lg">
              <h2 class="font-medium text-lg">历史消息</h2>
              <!-- 添加一个在移动端显示的关闭按钮 -->
              <button class="lg:hidden p-2 hover:bg-gray-100 rounded-lg">
                <XIcon class="w-5 h-5" />
              </button>
            </div>
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
            <div class="bg-white rounded-lg shadow flex flex-col h-[calc(100vh-8rem)]">
              <!-- 标题区域添加一个显示历史消息的按钮 -->
              <div class="flex items-center justify-between mb-8 bg-gray-50 p-3 rounded-t-lg border-b border-t border-gray-200">
                <div class="flex items-center">
                  <button class="lg:hidden p-2 mr-2 hover:bg-gray-100 rounded-lg">
                    <i class="fas fa-bars"></i>
                  </button>
                  <img src="@/assets/logo.svg" alt="logo" class="h-12 w-12 mr-3">
                  <div>
                    <h1 class="text-xl font-medium text-gray-900 text-left">社科数智</h1>
                    <p class="text-gray-500 text-sm">Social Science Data Artificial Intelligence (SSDAI)</p>
                  </div>
                </div>
              </div>

              <!-- 对话区域 -->
              <div class="flex-1 overflow-y-auto mb-6 space-y-6 p-6">
                <template v-if="messages.length > 0">
                  <div v-for="(message, index) in messages" :key="index" class="flex items-start space-x-3" :class="{ 'justify-end': message.role === 'user' }">
                    

                    
                    <!-- AI消息 -->
                    <template v-if="message.role === 'assistant'">
                      <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center flex-shrink-0">
                        <i class="fas fa-robot text-white text-lg"></i>
                      </div>
                      <div class="max-w-[80%]">
                        <div class="bg-blue-50 rounded-lg p-4 inline-block">
                          <template v-if="message.content || !isLoading">
                            <div class="text-gray-700 whitespace-pre-wrap break-words text-left prose prose-sm max-w-none prose-p:my-1 prose-li:my-1" v-html="renderMarkdown(message.content)"></div>
                          </template>
                          <template v-else>
                            <div class="flex space-x-2">
                              <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                              <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                              <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                            </div>
                          </template>
                        </div>
                      </div>
                    </template>
          
                    <!-- 用户消息 -->
                    <template v-else>
                      <div class="max-w-[80%] ml-auto">
                        <div class="bg-blue-500 text-white rounded-lg p-4 inline-block">
                          <p class="whitespace-pre-wrap break-words text-left text-sm">{{ message.content }}</p>
                        </div>
                      </div>
                      <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                        <i class="fas fa-user text-gray-500"></i>
                      </div>
                    </template>
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
              <div class="border-t p-6">
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
      </div>
    </main>

    <TheFooter />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TheHeader from '@/components/TheHeader.vue'
import TheFooter from '@/components/TheFooter.vue'
import MarkdownIt from 'markdown-it'
import { API_BASE_URL } from '../config'

import { 
  HomeIcon, 
  ArrowDownWideNarrow, 
  UserIcon, 
  SearchIcon, 
  ChevronDownIcon,
  BarChartIcon,
  XIcon
} from 'lucide-vue-next'


// 初始化markdown解析器
const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true
})

// 自定义渲染规则，减少空行
md.renderer.rules.paragraph_open = () => '<p class="mb-1">'
md.renderer.rules.list_item_open = () => '<li class="mb-1">'

// 解析markdown内容
const renderMarkdown = (content) => {
  if (!content) return ''
  return md.render(content)
}

// 状态变量
const conversations = ref([])
const currentConversationId = ref(null)
const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)

// 从localStorage获取所有对话历史
const fetchConversations = () => {
  const savedConversations = localStorage.getItem('conversations')
  conversations.value = savedConversations ? JSON.parse(savedConversations) : []
}

// 创建新对话
const createNewConversation = async () => {
  try {
    // 调用后端创建会话
    const response = await fetch(`${API_BASE_URL}/conversation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) throw new Error('创建会话失败')
    const data = await response.json()
    
    // 在本地保存会话信息
    const newConversation = {
      conversation_id: data.conversation_id,
      title: '新对话',
      created_at: new Date().toISOString()
    }
    conversations.value.unshift(newConversation)
    currentConversationId.value = data.conversation_id
    messages.value = []
    localStorage.setItem('conversations', JSON.stringify(conversations.value))
    localStorage.setItem(`messages_${data.conversation_id}`, JSON.stringify([]))
    
    return data.conversation_id
  } catch (error) {
    console.error('创建新对话失败:', error)
    throw error
  }
}

// 获取特定对话的消息
const fetchConversationMessages = (conversationId) => {
  const savedMessages = localStorage.getItem(`messages_${conversationId}`)
  messages.value = savedMessages ? JSON.parse(savedMessages) : []
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  
  const userMessage = inputMessage.value
  inputMessage.value = '' // 清空输入框
  
  try {
    // 如果没有当前会话ID，先创建一个新会话
    if (!currentConversationId.value) {
      await createNewConversation()
    }
    
    // 添加用户消息并保存到localStorage
    const newMessages = [...messages.value, {
      role: 'user',
      content: userMessage
    }]
    messages.value = newMessages
    localStorage.setItem(`messages_${currentConversationId.value}`, JSON.stringify(newMessages))
    
    isLoading.value = true
    
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
    
    // 保存完整对话到localStorage
    localStorage.setItem(`messages_${currentConversationId.value}`, JSON.stringify(messages.value))
    
    // 更新会话标题（使用第一条用户消息作为标题）
    if (messages.value.length === 2) {
      const conversation = conversations.value.find(c => c.conversation_id === currentConversationId.value)
      if (conversation) {
        conversation.title = userMessage.slice(0, 20) + (userMessage.length > 20 ? '...' : '')
        localStorage.setItem('conversations', JSON.stringify(conversations.value))
      }
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，发生了一些错误。请稍后重试。'
    })
    localStorage.setItem(`messages_${currentConversationId.value}`, JSON.stringify(messages.value))
  } finally {
    isLoading.value = false
  }
}

// 删除对话
const deleteConversation = (conversationId) => {
  // 从本地存储中删除会话
  conversations.value = conversations.value.filter(conv => conv.conversation_id !== conversationId)
  localStorage.setItem('conversations', JSON.stringify(conversations.value))
  localStorage.removeItem(`messages_${conversationId}`)
  
  if (currentConversationId.value === conversationId) {
    currentConversationId.value = null
    messages.value = []
  }
}

// 初始化
onMounted(() => {
  fetchConversations()
  // 如果有对话历史，加载最新的对话
  if (conversations.value.length > 0) {
    currentConversationId.value = conversations.value[0].conversation_id
    fetchConversationMessages(currentConversationId.value)
  }
})
</script>