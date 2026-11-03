import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import { pinia } from './stores'

const app = createApp(App)
app.use(pinia)        // 状态管理
app.use(router)       // 路由
app.use(ElementPlus)  // UI 组件库
app.mount('#app')
