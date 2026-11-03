import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const nickname = ref('')
  const role = ref('employee')       // 'employee' | 'admin'
  const avatar = ref('')
  const loaded = ref(false)         // 登录态是否已恢复（防重复调 /me）

  function setUser(info) {          // 登录成功后调用：后端给什么就存什么
    nickname.value = info.nickname ?? ''
    role.value = info.role ?? 'employee'
    if (info.avatar !== undefined) avatar.value = info.avatar
    loaded.value = true
  }

  function setAvatar(url) {         // 步骤 5 改头像时用
    avatar.value = url
  }

  function reset() {                // 退出登录时用（setup store 不支持 $reset，原因见步骤 4）
    nickname.value = ''
    role.value = 'employee'
    avatar.value = ''
    loaded.value = false
  }

  return { nickname, role, avatar, loaded, setUser, setAvatar, reset }
})