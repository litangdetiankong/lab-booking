<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()
const lab = ref(null)
const equipment = ref([])
const loading = ref(true)
const submitting = ref(false)
const form = reactive({ date: '', start_time: '', end_time: '', purpose: '' })

onMounted(async () => {
  try {
    lab.value = await request.get(`/labs/${route.params.id}`)
    equipment.value = await request.get(`/labs/${route.params.id}/equipment`)
  } finally {
    loading.value = false
  }
})

async function submit() {
  if (!form.date || !form.start_time || !form.end_time || !form.purpose.trim()) {
    ElMessage.warning('请把日期、时段和用途填完整')
    return
  }
  submitting.value = true
  try {
    await request.post('/reservations', {
      lab_id: Number(route.params.id),
      date: form.date,
      start_time: form.start_time,
      end_time: form.end_time,
      purpose: form.purpose.trim(),
    })
    ElMessage.success('预约已提交，等待审核')
    router.push('/my-reservations')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div v-loading="loading">
    <el-page-header content="实验室详情" @back="router.push('/labs')" />

    <template v-if="lab">
      <el-card style="margin-top: 16px">
        <template #header>
          <div class="lab-head">
            <span>{{ lab.name }}</span>
            <el-tag :type="lab.status === '开放中' ? 'success' : 'warning'">{{ lab.status }}</el-tag>
          </div>
        </template>
        <p class="meta">{{ lab.location }} · 容纳 {{ lab.capacity }} 人 · 开放 {{ lab.open_time_start }} - {{ lab.open_time_end }}</p>
        <p class="desc">{{ lab.description || '暂无介绍' }}</p>
      </el-card>

      <el-card style="margin-top: 16px">
        <h4>预约该实验室</h4>
        <el-alert
          v-if="lab.status !== '开放中'"
          type="warning"
          show-icon
          :closable="false"
          title="实验室维护中，暂不开放预约"
          style="margin-bottom: 12px"
        />
        <el-form :model="form" label-width="70px" :disabled="lab.status !== '开放中'">
          <el-form-item label="日期">
            <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
          </el-form-item>
          <el-form-item label="开始">
            <el-time-picker v-model="form.start_time" format="HH:mm" value-format="HH:mm" style="width: 100%" />
          </el-form-item>
          <el-form-item label="结束">
            <el-time-picker v-model="form.end_time" format="HH:mm" value-format="HH:mm" style="width: 100%" />
          </el-form-item>
          <el-form-item label="用途">
            <el-input v-model="form.purpose" placeholder="例如：课程设计调试" />
          </el-form-item>
          <el-button type="primary" :loading="submitting" @click="submit">提交预约</el-button>
        </el-form>
      </el-card>

      <el-card style="margin-top: 16px">
        <h4>设备清单</h4>
        <el-table :data="equipment">
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="model" label="型号" />
          <el-table-column prop="total" label="总数" width="80" />
          <el-table-column prop="available" label="可用" width="80" />
        </el-table>
        <el-empty v-if="!equipment.length" description="该实验室暂无设备" />
      </el-card>
    </template>
  </div>
</template>

<style scoped>
.lab-head { display: flex; justify-content: space-between; align-items: center; }
.meta { margin: 0 0 8px; color: #606266; }
.desc { margin: 0; white-space: pre-wrap; color: #303133; }
h4 { margin: 0 0 12px; }
</style>
