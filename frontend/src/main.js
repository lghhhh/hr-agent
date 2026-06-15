import { createApp } from "vue"
import ElementPlus from "element-plus"
import "element-plus/dist/index.css"
import * as ElementPlusIconsVue from "@element-plus/icons-vue"
import App from "./App.vue"
import router from "./router"
import { createPinia } from "pinia"
import axios from "axios"

// Axios defaults
axios.defaults.baseURL = import.meta.env.VITE_API_BASE || ""
axios.defaults.timeout = 30000

// Request interceptor — attach token
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor — handle 401
axios.interceptors.response.use(
  (resp) => resp,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token")
      localStorage.removeItem("user")
      window.location.hash = "#/login"
    }
    return Promise.reject(error)
  }
)

const app = createApp(App)
app.use(ElementPlus)
app.use(createPinia())
app.use(router)

// Register all Element Plus icons globally
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount("#app")
