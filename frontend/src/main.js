import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'

const app = createApp(App)
app.use(router)
app.use(ElementPlus)

axios.defaults.baseURL = 'http://your-api-domain.com'
app.config.globalProperties.$http = axios

app.mount('#app')