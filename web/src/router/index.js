import { createRouter, createWebHistory } from 'vue-router'
import request from '@/utils/request'
import { useUserStore } from '@/stores/user'

const routes = [
  { path: '/login', component: () => import('@/views/Login.vue') },
  { path: '/register', component: () => import('@/views/Register.vue') },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),  // 外壳
    redirect: '/home',                              // 访问 / 自动跳 /home
    children: [
      { path: 'home',            component: () => import('@/views/Home.vue'),             meta: { title: '首页',       requiresAuth: true } },
      { path: 'labs',            component: () => import('@/views/LabList.vue'),          meta: { title: '实验室列表', requiresAuth: true } },
      { path: 'labs/:id',        component: () => import('@/views/LabDetail.vue'),        meta: { title: '实验室详情', requiresAuth: true } },
      { path: 'my-reservations', component: () => import('@/views/MyReservations.vue'),   meta: { title: '我的预约',   requiresAuth: true } },
      { path: 'profile',         component: () => import('@/views/Profile.vue'),          meta: { title: '个人中心',   requiresAuth: true } },
      { path: 'ai',              component: () => import('@/views/AiChat.vue'),           meta: { title: 'AI 助手',    requiresAuth: true } },
      { path: 'admin/users',     component: () => import('@/views/admin/UserManage.vue'),  meta: { title: '用户管理',   requiresAuth: true, requiresAdmin: true } },
      { path: 'admin/labs',      component: () => import('@/views/admin/LabManage.vue'),   meta: { title: '实验室管理', requiresAuth: true, requiresAdmin: true } },
      { path: 'admin/reviews',   component: () => import('@/views/admin/ReviewManage.vue'), meta: { title: '预约审核', requiresAuth: true, requiresAdmin: true } },
    ],
  },
]

const router = createRouter({ history: createWebHistory(), routes })
export default router


router.beforeEach(async (to) => {                    
  const token = localStorage.getItem('token')
  const userStore = useUserStore()

  // 0) 有 token 但 store 失忆（刚整页刷新过）→ 先用 /me 恢复登录态再放行
  if (token && !userStore.loaded) {
    try {
      userStore.setUser(await request.get('/auth/me'))
    } catch {
      localStorage.removeItem('token')   // token 过期/伪造：清掉，下面的规则自然踢去登录
    }
  }

  // 1) 要登录却没 token → 去登录页，记住来路（登录成功后原路返回）
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  // 2) 已登录还去 /login → 直接送回首页
  if (localStorage.getItem('token') && to.path === '/login') return '/home'
  // 3) 管理页非管理员 → 拦回首页（真正的防线是后端 require_admin）
  if (to.meta.requiresAdmin) {
    if (userStore.role !== 'admin') return '/home'
  }
  return true
})