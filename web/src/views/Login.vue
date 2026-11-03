<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()                       // 守卫踢过来时会带 redirect 参数
const userStore = useUserStore()
const formRef = ref()                          // 表单实例：用来触发校验
const form = reactive({ username: route.query.username || '', password: '' })
const loading = ref(false)

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 32, message: '密码长度 6-32 位', trigger: 'blur' },
  ],
}

async function onSubmit() {
  await formRef.value.validate()               // 校验不过会抛异常，后面代码不执行
  loading.value = true
  try {
    const data = await request.post('/auth/login', form)   // data = { token, nickname, role }
    localStorage.setItem('token', data.token)
    userStore.setUser(data)
    router.push(route.query.redirect || '/')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2 class="title">智能实验室预约系统</h2>
      <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="onSubmit">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="密码" />
        </el-form-item>
        <el-button type="primary" :loading="loading" class="btn" @click="onSubmit">
          登 录
        </el-button>
        <div class="tip">没有账号？<router-link to="/register">去注册</router-link></div>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.login-page { height: 100vh; display: flex; align-items: center; justify-content: center; background: #f5f7fa; }
.login-card { width: 380px; padding: 8px 12px; }
.title { text-align: center; margin: 4px 0 24px; }
.btn { width: 100%; }
.tip { text-align: right; margin-top: 12px; font-size: 13px; }
</style>