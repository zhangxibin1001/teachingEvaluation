import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'

const app = createApp(App)
app.use(ElementPlus)
// 配置Axios默认请求地址
axios.defaults.baseURL = 'http://localhost:5000/api'
// 挂载到全局
app.config.globalProperties.$axios = axios

app.mount('#app')