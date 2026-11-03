<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

// ---------- 状态（五个） ----------
const list = ref([])              // 当前页数据
const total = ref(0)              // 总条数（分页器用）
const loading = ref(false)
const query = reactive({ page: 1, page_size: 10, keyword: '' })
const dialogVisible = ref(false)
const isEdit = ref(false)         // true=编辑 false=新增（同一个弹窗两种用途）
const formRef = ref()
const form = reactive({ id: null, username: '', nickname: '', role: 'employee' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  role: [{ required: true }],
}

// ---------- 核心函数：本质是"改状态 → 调接口 → 刷新列表"循环 ----------
async function load() {
  loading.value = true
  try {
    const data = await request.get('/users', { params: query })   // query 自动拼成 ?page=...&keyword=...
    list.value = data.list
    total.value = data.total
  } finally { loading.value = false }
}

function openAdd() {
  isEdit.value = false
  Object.assign(form, { id: null, username: '', nickname: '', role: 'employee' })
  dialogVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  Object.assign(form, row)   // 展开拷贝：弹窗里改的是 form，不会实时污染表格行
  dialogVisible.value = true
}

async function save() {
  await formRef.value.validate()
  if (isEdit.value) await request.put(`/users/${form.id}`, form)
  else await request.post('/users', form)
  ElMessage.success('已保存')
  dialogVisible.value = false
  load()
}

async function remove(row) {
  await ElMessageBox.confirm(`确定删除用户「${row.username}」？`, '提示', { type: 'warning' })
  await request.delete(`/users/${row.id}`)
  ElMessage.success('已删除')
  load()
}

async function resetPassword(row) {
  await ElMessageBox.confirm(`确定将「${row.username}」的密码重置为 123456？`, '提示', { type: 'warning' })
  await request.put(`/users/${row.id}/reset-password`)
  ElMessage.success('已重置为 123456')
}

function rowNo(index) {
  return (query.page - 1) * query.page_size + index + 1
}

onMounted(load)
</script>

<template>
  <div>
    <!-- 搜索区 -->
    <el-input v-model="query.keyword" placeholder="用户名/昵称" style="width: 220px"
              clearable @keyup.enter="query.page = 1; load()" />
    <el-button type="primary" @click="query.page = 1; load()">搜索</el-button>
    <el-button type="success" @click="openAdd">新增用户</el-button>

    <!-- 表格区 -->
    <el-table :data="list" v-loading="loading" style="margin-top: 12px">
      <el-table-column type="index" label="id" width="70" :index="rowNo" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="nickname" label="昵称" />
      <el-table-column label="角色" width="100">
        <template #default="{ row }">{{ row.role === 'admin' ? '管理员' : '检测员' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" @click="resetPassword(row)">重置密码</el-button>
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页器 -->
    <el-pagination style="margin-top: 12px" layout="total, prev, pager, next"
      :total="total" :page-size="query.page_size"
      v-model:current-page="query.page" @current-change="load" />

    <!-- 弹窗表单 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="420px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname"><el-input v-model="form.nickname" /></el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role">
            <el-option label="检测员" value="employee" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>