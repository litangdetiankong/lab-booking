<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

/* ---------- 实验室列表 ---------- */
const list = ref([])
const loading = ref(false)
const keyword = ref('')

async function load() {
  loading.value = true
  try {
    list.value = await request.get('/labs', { params: { keyword: keyword.value } })
  } finally { loading.value = false }
}
onMounted(load)

/* ---------- 实验室新增/编辑弹窗 ---------- */
const labDialogVisible = ref(false)
const isEditLab = ref(false)
const labFormRef = ref()
const labForm = reactive({ id: null, name: '', description: '', location: '',
                           capacity: 10, open_time_start: '09:00', open_time_end: '21:00', status: '开放中' })
const labRules = {
  name: [{ required: true, message: '请输入检测室名称', trigger: 'blur' }],
  open_time_start: [{ required: true, message: '请选择开放开始时间', trigger: 'change' }],
  open_time_end: [{ required: true, message: '请选择开放结束时间', trigger: 'change' }],
}

function openAdd() {
  isEditLab.value = false
  Object.assign(labForm, { id: null, name: '', description: '', location: '',
                           capacity: 10, open_time_start: '09:00', open_time_end: '21:00', status: '开放中' })
  labDialogVisible.value = true
}

async function openEdit(row) {
  const detail = await request.get(`/labs/${row.id}`)   // 列表只回摘要：编辑前先取详情，防 description 被清空
  isEditLab.value = true
  Object.assign(labForm, { id: row.id, ...detail })
  labDialogVisible.value = true
}

async function saveLab() {
  await labFormRef.value.validate()
  const payload = { name: labForm.name, description: labForm.description, location: labForm.location,
                    capacity: labForm.capacity, open_time_start: labForm.open_time_start,
                    open_time_end: labForm.open_time_end, status: labForm.status }
  if (isEditLab.value) await request.put(`/labs/${labForm.id}`, payload)
  else await request.post('/labs', payload)
  ElMessage.success('已保存')
  labDialogVisible.value = false
  load()
}

async function removeLab(row) {
  await ElMessageBox.confirm(`确定删除「${row.name}」？其名下设备将一并删除。`, '提示', { type: 'warning' })
  await request.delete(`/labs/${row.id}`)
  ElMessage.success('已删除')
  load()
}

/* ---------- 设备弹窗（挂在实验室行上） ---------- */
const eqDialogVisible = ref(false)
const currentLab = reactive({ id: null, name: '' })
const eqList = ref([])
const eqLoading = ref(false)
const isEditEq = ref(false)
const editingEqId = ref(null)
const eqFormRef = ref()
const eqForm = reactive({ name: '', model: '', total: 1, available: 1 })
const eqRules = { name: [{ required: true, message: '请输入设备名', trigger: 'blur' }] }

async function openEquip(row) {
  currentLab.id = row.id
  currentLab.name = row.name
  eqDialogVisible.value = true
  await loadEquip()
}

async function loadEquip() {
  eqLoading.value = true
  try { eqList.value = await request.get(`/labs/${currentLab.id}/equipment`) }
  finally { eqLoading.value = false }
}

function resetEqForm() {
  isEditEq.value = false
  editingEqId.value = null
  Object.assign(eqForm, { name: '', model: '', total: 1, available: 1 })
}

function openEditEq(eq) {
  isEditEq.value = true
  editingEqId.value = eq.id
  Object.assign(eqForm, { name: eq.name, model: eq.model, total: eq.total, available: eq.available })
}

async function saveEq() {
  await eqFormRef.value.validate()
  if (isEditEq.value) await request.put(`/labs/equipment/${editingEqId.value}`, eqForm)
  else await request.post(`/labs/${currentLab.id}/equipment`, eqForm)
  ElMessage.success('已保存')
  resetEqForm()
  loadEquip()
}

async function removeEq(eq) {
  await ElMessageBox.confirm(`确定删除设备「${eq.name}」？`, '提示', { type: 'warning' })
  await request.delete(`/labs/equipment/${eq.id}`)
  ElMessage.success('已删除')
  loadEquip()
}
</script>

<template>
  <div>
    <el-input v-model="keyword" placeholder="名称/位置/描述" style="width: 220px" clearable @keyup.enter="load" />
    <el-button type="primary" @click="load">搜索</el-button>
    <el-button type="success" @click="openAdd">新增检测室</el-button>

    <el-table :data="list" v-loading="loading" style="margin-top: 12px">
      <el-table-column type="index" label="id" width="70" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="location" label="位置" width="110" />
      <el-table-column prop="capacity" label="容量" width="70" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === '开放中' ? 'success' : 'warning'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="210">
        <template #default="{ row }">
          <el-button size="small" type="primary" plain @click="openEquip(row)">设备</el-button>
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="removeLab(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="labDialogVisible" :title="isEditLab ? '编辑检测室' : '新增检测室'" width="520px">
      <el-form ref="labFormRef" :model="labForm" :rules="labRules" label-width="90px">
        <el-form-item label="名称" prop="name"><el-input v-model="labForm.name" /></el-form-item>
        <el-form-item label="位置"><el-input v-model="labForm.location" /></el-form-item>
        <el-form-item label="容量"><el-input-number v-model="labForm.capacity" :min="0" /></el-form-item>
        <el-form-item label="开放时段">
          <el-time-picker v-model="labForm.open_time_start" value-format="HH:mm" format="HH:mm" style="width: 110px" />
          <span style="margin: 0 8px">至</span>
          <el-time-picker v-model="labForm.open_time_end" value-format="HH:mm" format="HH:mm" style="width: 110px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="labForm.status" style="width: 140px">
            <el-option label="开放中" value="开放中" />
            <el-option label="维护中" value="维护中" />
          </el-select>
        </el-form-item>
        <el-form-item label="介绍"><el-input v-model="labForm.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="labDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveLab">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="eqDialogVisible" :title="`设备管理 · ${currentLab.name}`" width="660px">
      <el-table :data="eqList" v-loading="eqLoading" size="small">
        <el-table-column prop="name" label="设备名" />
        <el-table-column prop="model" label="型号" />
        <el-table-column prop="total" label="总数" width="70" />
        <el-table-column prop="available" label="可用" width="70" />
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button size="small" @click="openEditEq(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="removeEq(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-divider content-position="left">{{ isEditEq ? '编辑设备' : '新增设备' }}</el-divider>
      <el-form ref="eqFormRef" :model="eqForm" :rules="eqRules" inline>
        <el-form-item prop="name"><el-input v-model="eqForm.name" placeholder="设备名" style="width: 130px" /></el-form-item>
        <el-form-item><el-input v-model="eqForm.model" placeholder="型号" style="width: 140px" /></el-form-item>
        <el-form-item><el-input-number v-model="eqForm.total" :min="0" style="width: 110px" /></el-form-item>
        <el-form-item><el-input-number v-model="eqForm.available" :min="0" style="width: 110px" /></el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveEq">{{ isEditEq ? '更新' : '添加' }}</el-button>
          <el-button v-if="isEditEq" @click="resetEqForm">取消编辑</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>