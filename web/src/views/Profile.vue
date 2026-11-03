<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

/* 刷新后 store 是空的（内存态）：用 /me 恢复，5.5 的"刷新后头像仍在"靠它 */
onMounted(async () => {
  const res = await request.get('/auth/me')
  userStore.setUser(res)
  profileForm.nickname = res.nickname
})

/* ---------- 头像：必须自定义上传，走 request.js 才带 token ---------- */
async function doUpload({ file }) {
  const fd = new FormData()                               // 浏览器提供的 multipart 组装器
  fd.append('file', file)
  const res = await request.post('/users/me/avatar', fd)  // 解包后 res = { avatar: '/static/avatars/x.png' }
  userStore.setAvatar(res.avatar)                         // 注意取 .avatar——教程片段这里有个 bug，已修文档
}

/* ---------- 改资料 ---------- */
const profileRef = ref()
const profileForm = reactive({ nickname: userStore.nickname })
const profileRules = {
  nickname: [{ required: true, message: '昵称不能为空', trigger: 'blur' }],
}
async function onSaveProfile() {
  await profileRef.value.validate()
  const res = await request.put('/users/me', { nickname: profileForm.nickname })
  userStore.nickname = res.nickname    // 直接写 store：顶栏立刻更新（Pinia 响应式）
  ElMessage.success('资料已保存')
}

/* ---------- 改密码 ---------- */
const pwdRef = ref()
const pwdForm = reactive({ old_password: '', new_password: '', confirm_password: '' })
const pwdRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 32, message: '密码长度 6-32 位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: (r, v, cb) => v !== pwdForm.new_password ? cb(new Error('两次输入不一致')) : cb(), trigger: 'blur' },
  ],
}
async function onChangePassword() {
  await pwdRef.value.validate()
  await request.put('/users/me/password', {
    old_password: pwdForm.old_password, new_password: pwdForm.new_password,
  })
  ElMessage.success('密码已修改，请重新登录')
  localStorage.removeItem('token')   // JWT 无状态、旧 token 仍有效——前端清掉，双保险（5.3）
  userStore.reset()
  router.push('/login')
}
</script>

<template>
  <div class="profile-page">
    <el-card header="头像">
      <el-upload :show-file-list="false" :http-request="doUpload" accept="image/*">
        <el-avatar :size="72" :src="userStore.avatar" />
      </el-upload>
      <p class="tip">点击头像更换，支持 jpg/png/webp，不超过 2MB</p>
    </el-card>

    <el-card header="基本资料">
      <el-form ref="profileRef" :model="profileForm" :rules="profileRules" label-width="80px">
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="profileForm.nickname" style="max-width: 300px" />
        </el-form-item>
        <el-form-item><el-button type="primary" @click="onSaveProfile">保存资料</el-button></el-form-item>
      </el-form>
    </el-card>

    <el-card header="修改密码">
      <el-form ref="pwdRef" :model="pwdForm" :rules="pwdRules" label-width="80px">
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password style="max-width: 300px" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password style="max-width: 300px" />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input v-model="pwdForm.confirm_password" type="password" show-password style="max-width: 300px" />
        </el-form-item>
        <el-form-item><el-button type="primary" @click="onChangePassword">修改密码</el-button></el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.profile-page { max-width: 640px; margin: 24px auto; display: flex; flex-direction: column; gap: 16px; }
.tip { color: #909399; font-size: 12px; margin-top: 8px; }
</style>