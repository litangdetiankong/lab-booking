<script setup>
// <script setup> 是组合式 API 的语法糖：
// 这里顶层声明的变量和函数，模板里直接能用
import { useRoute, useRouter} from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()          // 当前路由对象：高亮菜单、显示标题
const router = useRouter()
const userStore = useUserStore()  // 全局用户状态：控制管理菜单显隐

function logout() {
  localStorage.removeItem('token')
  userStore.reset()          // 步骤 1 store 里自己写的 reset()
  router.push('/login')
}

</script>

<template>
  <el-container class="layout">
    <el-aside width="220px">
      <el-menu router :default-active="route.path">
        <el-menu-item index="/home">首页</el-menu-item>
        <el-menu-item index="/labs">检测室列表</el-menu-item>
        <el-menu-item index="/my-reservations">我的预约</el-menu-item>
        <!-- 管理菜单：三个菜单项共用一个 v-if，必须用 <template> 包起来——
             el-menu 的直接孩子要能当"菜单"解析，条件就挂不住 -->
        <template v-if="userStore.role === 'admin'">
          <el-menu-item index="/admin/users">用户管理</el-menu-item>
          <el-menu-item index="/admin/labs">检测室管理</el-menu-item>
          <el-menu-item index="/admin/reviews">预约审核</el-menu-item>
        </template>
        <el-menu-item index="/ai">检验助手</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="topbar">
        <span class="title">{{ route.meta.title }}</span>
        <el-dropdown trigger="click">
          <span class="user">{{ userStore.nickname }}</span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/profile')">个人中心</el-dropdown-item>
              <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main>
        <router-view />   <!-- 子页面渲染在这里 -->
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout { height: 100vh; }
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #ebeef5;
  background: #fff;
}
.title { font-size: 16px; color: #303133; }
.user { cursor: pointer; color: #303133; outline: none; }
</style>