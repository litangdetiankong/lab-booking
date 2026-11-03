<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const route = useRoute()
const formRef = ref()
const form = reactive({
  username: route.query.username || '',   // 从登录页"去注册"跳来时自动填
  nickname: '',
  password: '',
  confirmPassword: '',
})
const loading = ref(false)

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 32, message: '密码长度 6-32 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: (rule, value, callback) => {
        // 自定义校验器：callback() = 通过；callback(new Error(msg)) = 失败
        // 它只拿到本字段的 value——但闭包里的 form 能拿到全部字段，所以能对比
        value !== form.password ? callback(new Error('两次输入的密码不一致')) : callback()
      }, trigger: 'blur' },
  ],
}

async function onSubmit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await request.post('/auth/register', {
      username: form.username, password: form.password, nickname: form.nickname,
    })
    ElMessage.success('注册成功，请登录')
    router.push({ path: '/login', query: { username: form.username } })
  } finally { loading.value = false }
}
</script>

<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2 class="title">注册账号</h2>
      <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="onSubmit">
        <el-form-item prop="username"><el-input v-model="form.username" placeholder="用户名" /></el-form-item>
        <el-form-item prop="nickname"><el-input v-model="form.nickname" placeholder="昵称" /></el-form-item>
        <el-form-item prop="password"><el-input v-model="form.password" type="password" show-password placeholder="密码" /></el-form-item>
        <el-form-item prop="confirmPassword"><el-input v-model="form.confirmPassword" type="password" show-password placeholder="确认密码" /></el-form-item>
        <el-button type="primary" :loading="loading" class="btn" @click="onSubmit">注 册</el-button>
        <div class="tip">已有账号？<router-link to="/login">去登录</router-link></div>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
/* 样式与 Login.vue 相同——顺手练一下：抽成公共 css 文件 */
.login-page { height: 100vh; display: flex; align-items: center; justify-content: center; background: #f5f7fa; }
.login-card { width: 380px; padding: 8px 12px; }
.title { text-align: center; margin: 4px 0 24px; }
.btn { width: 100%; }
.tip { text-align: right; margin-top: 12px; font-size: 13px; }
</style>