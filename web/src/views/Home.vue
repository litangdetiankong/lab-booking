<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const isAdmin = userStore.role === 'admin'
const stats = ref({ my_total: 0, upcoming: 0, lab_total: 0, pending: null })

onMounted(async () => {
  try { stats.value = await request.get('/stats') } catch { /* 401 由拦截器统一处理 */ }
})

const cards = [
  { key: 'my_total',  label: '我的预约总数',   path: '/my-reservations' },
  { key: 'upcoming',  label: '即将开始的预约', path: '/my-reservations' },
  { key: 'lab_total', label: '实验室总数',     path: '/labs' },
]
const entries = [
  { label: '去预约',   desc: '浏览开放中的实验室', path: '/labs' },
  { label: '我的预约', desc: '查看与取消我的预约', path: '/my-reservations' },
  ...(isAdmin ? [{ label: '预约审核', desc: '处理待审核预约单', path: '/admin/reviews' }] : []),
  { label: 'AI 助手',  desc: '一句话预约实验室',   path: '/ai' },
]
</script>

<template>
  <div class="home">
    <div class="hero">
      <h2>你好，{{ userStore.nickname || userStore.username }}</h2>
      <p v-if="isAdmin">今日有 {{ stats.pending ?? 0 }} 单待审核</p>
      <p v-else>祝你实验顺利！</p>
    </div>

    <el-row :gutter="16" class="cards">
      <el-col v-for="c in cards" :key="c.key" :span="isAdmin ? 6 : 8">
        <el-card shadow="hover" class="stat" @click="router.push(c.path)">
          <div class="num">{{ stats[c.key] ?? 0 }}</div>
          <div class="label">{{ c.label }}</div>
        </el-card>
      </el-col>
      <el-col v-if="isAdmin" :span="6">
        <el-card shadow="hover" class="stat warn" @click="router.push('/admin/reviews')">
          <div class="num">{{ stats.pending ?? 0 }}</div>
          <div class="label">待审核预约</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="entries">
      <el-col v-for="e in entries" :key="e.label" :span="6">
        <el-card shadow="hover" class="entry" @click="router.push(e.path)">
          <h3>{{ e.label }}</h3>
          <p>{{ e.desc }}</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.home { padding: 8px; }
.hero { margin-bottom: 16px; }
.hero h2 { margin: 0 0 4px; }
.hero p { margin: 0; color: #909399; }
.cards { margin-bottom: 16px; }
.stat { text-align: center; cursor: pointer; }
.stat .num { font-size: 28px; font-weight: 600; }
.stat .label { color: #909399; font-size: 13px; }
.stat.warn .num { color: #e6a23c; }
.entry { cursor: pointer; }
.entry h3 { margin: 0 0 4px; }
.entry p { margin: 0; color: #909399; font-size: 13px; }
</style>