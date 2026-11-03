<script setup>
import { reactive, ref, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { streamChat } from '@/utils/sse'

const STORE_KEY = 'ai_chat_history'
const messages = ref(JSON.parse(localStorage.getItem(STORE_KEY) || '[]'))
const input = ref('')
const streaming = ref(false)
const boxRef = ref()

watch(messages, (val) => localStorage.setItem(STORE_KEY, JSON.stringify(val)), { deep: true })

async function clearChat() {
  messages.value = []
  localStorage.removeItem(STORE_KEY)
  try {
    await request.post('/ai/chat/reset')
  } catch {
    ElMessage.warning('本地对话已清空，服务端预约上下文可能还在，请稍后重试')
  }
}

function scrollBottom() {
  nextTick(() => { const el = boxRef.value?.$el; if (el) el.scrollTop = el.scrollHeight })
}

const NODE_TEXT = {
  classify: '正在判断你的需求',
  answer_qa: '正在查阅资料',
  extract_info: '正在理解需求',
  ask_clarify: '正在向你确认信息',
  revise: '正在按新需求调整',
  search_labs: '正在查询实验室',
  propose: '正在生成推荐方案',
  cancel_booking: '正在取消本次预约',
  create_reservation: '正在创建预约',
}

async function send() {
  const text = input.value.trim()
  if (!text || streaming.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''

  const reply = reactive({ role: 'assistant', content: '', steps: [] })   // 占位消息：事件都改写它
  messages.value.push(reply)
  streaming.value = true
  scrollBottom()

  try {
    await streamChat(messages.value.slice(0, -1), (ev) => {   // 不含占位消息的历史
      if (ev.type === 'node')       reply.steps.push(NODE_TEXT[ev.name] || ev.name)
      else if (ev.type === 'token') { reply.content += ev.content; scrollBottom() }
      else if (ev.type === 'error') ElMessage.error(ev.message || '出错了')
    })
  } catch {
    ElMessage.error('连接中断，请重试')
  } finally {
    streaming.value = false
  }
}
</script>

<template>
  <div class="ai-chat">
    <div class="toolbar">
      <el-button size="small" @click="clearChat">清空对话</el-button>
    </div>
    <div class="box" ref="boxRef">
      <el-empty v-if="!messages.length" description="试试：帮我预约明天下午的实验室" />
      <div v-for="(m, i) in messages" :key="i" class="row" :class="m.role">
        <div class="msg">
          <div v-for="(step, si) in m.steps || []" :key="si" class="step-tag">⚡ {{ step }}</div>
          <div class="bubble">{{ m.content }}<span v-if="streaming && m.role === 'assistant' && i === messages.length - 1" class="cursor">▌</span></div>
        </div>
      </div>
    </div>
    <div class="input-bar">
      <el-input v-model="input" placeholder="试试：帮我预约明天下午的实验室" @keyup.enter="send" :disabled="streaming" />
      <el-button type="primary" :loading="streaming" @click="send">发送</el-button>
    </div>
  </div>
</template>

<style scoped>
.ai-chat { display: flex; flex-direction: column; height: calc(100vh - 140px); }
.toolbar { margin-bottom: 8px; }
.box { flex: 1; overflow-y: auto; padding: 12px; background: #f5f7fa; border-radius: 6px; }
.row { display: flex; margin-bottom: 10px; }
.row.user { justify-content: flex-end; }
.row.assistant { justify-content: flex-start; }
.msg { max-width: 80%; }
.step-tag { font-size: 12px; color: #909399; margin-bottom: 2px; }
.bubble { padding: 8px 12px; border-radius: 8px; background: #fff;
          box-shadow: 0 1px 2px rgba(0, 0, 0, .06); white-space: pre-wrap; }
.row.user .bubble { background: #409eff; color: #fff; }
.cursor { animation: blink 1s infinite; }
@keyframes blink { 50% { opacity: 0; } }
.input-bar { display: flex; gap: 8px; margin-top: 10px; }
</style>