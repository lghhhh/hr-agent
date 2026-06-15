<template>
  <div class="login-container">
    <div class="login-card">
      <h2 style="text-align: center; margin-bottom: 30px; color: #303133;">AI 智能招聘面试管理系统</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="0">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="请输入账号" size="large" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width: 100%" @click="handleLogin" :loading="loading">登 录</el-button>
        </el-form-item>
      </el-form>
      <div style="text-align: center; color: #909399; font-size: 13px;">
        默认管理员：admin / admin123
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue"
import { useRouter } from "vue-router"
import { useAppStore } from "../store"
import { login } from "../api/auth"
import { ElMessage } from "element-plus"

const router = useRouter()
const store = useAppStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: "",
  password: "",
})

const rules = {
  username: [{ required: true, message: "请输入账号", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const resp = await login(form)
    if (resp.data.code === 200) {
      store.setToken(resp.data.data.token)
      store.setUser(resp.data.data.user)
      ElMessage.success("登录成功")
      router.push("/dashboard")
    } else {
      ElMessage.error(resp.data.msg || "登录失败")
    }
  } catch {
    ElMessage.error("登录失败，请检查网络")
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}
</style>
