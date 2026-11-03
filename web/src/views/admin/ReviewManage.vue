<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const list = ref([])
const loading = ref(true)

async function load() {
  loading.value = true
  try { list.value = await request.get('/reservations/pending') }
  finally { loading.value = false }
}

async function review(row, action) {
  let comment = ''
  if (action === 'rejected') {
    const { value } = await ElMessageBox.prompt('请填写驳回原因', '驳回', {
      inputValidator: (v) => (v && v.trim() ? true : '驳回必须填写原因'),
    })
    comment = value
  } else {
    await ElMessageBox.confirm(`确定通过「${row.lab_name}」的预约？`, '提示', { type: 'success' })
  }
  await request.put(`/reservations/${row.id}/review`, { action, comment })
  ElMessage.success('已处理')
  load()
}

onMounted(load)
</script>

<template>
  <div>
    <el-table :data="list" v-loading="loading">
      <el-table-column type="index" label="id" width="70" />
      <el-table-column prop="lab_name" label="实验室" />
      <el-table-column prop="date" label="日期" width="110" />
      <el-table-column label="时段" width="130">
        <template #default="{ row }">{{ row.start_time.slice(0, 5) }} - {{ row.end_time.slice(0, 5) }}</template>
      </el-table-column>
      <el-table-column prop="purpose" label="用途" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="review(row, 'approved')">通过</el-button>
          <el-button size="small" type="danger" @click="review(row, 'rejected')">驳回</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-if="!loading && !list.length" description="没有待审核的预约" />
  </div>
</template>