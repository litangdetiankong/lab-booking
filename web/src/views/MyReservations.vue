<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const list = ref([])
const loading = ref(true)

const STATUS_MAP = {
  pending:   { text: '待审核', type: 'warning' },
  approved:  { text: '已通过', type: 'success' },
  rejected:  { text: '已驳回', type: 'danger' },
  cancelled: { text: '已取消', type: 'info' },
}
const canCancel = (row) => ['pending', 'approved'].includes(row.status)

async function load() {
  loading.value = true
  try { list.value = await request.get('/reservations/mine') }
  finally { loading.value = false }
}

async function cancel(row) {
  await ElMessageBox.confirm('确定取消该预约？', '提示', { type: 'warning' })
  await request.put(`/reservations/${row.id}/cancel`)
  ElMessage.success('已取消')
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
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="STATUS_MAP[row.status].type">{{ STATUS_MAP[row.status].text }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="review_comment" label="驳回原因" />
      <el-table-column label="操作" width="110">
        <template #default="{ row }">
          <el-button v-if="canCancel(row)" size="small" type="danger" @click="cancel(row)">取消预约</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-if="!loading && !list.length" description="还没有预约记录，去实验室列表逛逛" />
  </div>
</template>