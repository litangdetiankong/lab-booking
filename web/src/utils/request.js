import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({ baseURL: '/api', timeout: 15000 })

// 请求拦截器：出门前自动别上工牌
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截器：回来后统一拆信封
request.interceptors.response.use(
  (res) => {
    const { code, message, data } = res.data
    if (code === 0) return data              // ← 业务代码拿到的直接就是 data！
    if (code === 1041) {                     // 约定：1041 = 未登录/过期
      localStorage.removeItem('token')
      router.push('/login')
    }
    ElMessage.error(message)
    return Promise.reject(new Error(message))
  },
  (err) => {                                 // HTTP 层错误（超时/500/422…）
    if (err.response?.status === 401) {      // token 无效/过期：后端发的是 HTTP 401
      localStorage.removeItem('token')
      router.push('/login')
    }
    ElMessage.error(err.response?.data?.detail || err.message || '网络异常')
    return Promise.reject(err)
  },
)
export default request