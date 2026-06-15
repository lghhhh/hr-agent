<template>
  <div>
    <!-- LLM Config -->
    <el-card style="margin-bottom: 16px;">
      <template #header><span style="font-weight: bold;">大模型配置</span></template>
      <el-form label-width="140px" label-position="left">
        <el-form-item label="API 接口地址">
          <el-input v-model="llmConfig.api_base" placeholder="https://api.openai.com/v1" />
          <div style="font-size: 12px; color: #909399; margin-top: 4px;">支持 OpenAI / 豆包 / 通义千问等兼容接口</div>
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="llmConfig.api_key" type="password" show-password placeholder="sk-..." />
        </el-form-item>
        <el-form-item label="模型名称">
          <el-input v-model="llmConfig.model" placeholder="gpt-4o-mini / deepseek-chat" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveLLMConfig" :loading="savingLLM">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- AI Prompt -->
    <el-card style="margin-bottom: 16px;">
      <template #header><span style="font-weight: bold;">AI 面试总结 Prompt</span></template>
      <el-form label-position="top">
        <el-form-item label="自定义Prompt（修改后将影响AI生成面试总结的格式和内容）">
          <el-input v-model="aiPrompt" type="textarea" :rows="12" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="savePrompt" :loading="savingPrompt">保存Prompt</el-button>
          <el-button @click="resetPrompt" style="margin-left: 12px;">恢复默认</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Account Management -->
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold;">账号管理</span>
          <el-button type="primary" size="small" @click="showAddUser">+ 新增账号</el-button>
        </div>
      </template>
      <el-table :data="users" stripe>
        <el-table-column prop="username" label="登录账号" width="140" />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
              {{ row.role === 'admin' ? '管理员' : '面试官' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="170" />
      </el-table>

      <el-dialog v-model="userDialog" title="新增账号" width="400px">
        <el-form :model="userForm" label-width="80px" ref="userFormRef" :rules="userRules">
          <el-form-item label="账号" prop="username">
            <el-input v-model="userForm.username" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="userForm.password" type="password" show-password />
          </el-form-item>
          <el-form-item label="姓名" prop="real_name">
            <el-input v-model="userForm.real_name" />
          </el-form-item>
          <el-form-item label="角色">
            <el-select v-model="userForm.role">
              <el-option label="面试官" value="interviewer" />
              <el-option label="管理员" value="admin" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="userDialog = false">取消</el-button>
          <el-button type="primary" @click="saveUser" :loading="savingUser">保存</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { getConfig, updateConfig } from "../api/config"
import { getUsers, createUser } from "../api/auth"
import { ElMessage } from "element-plus"

// LLM Config
const llmConfig = reactive({ api_base: "", api_key: "", model: "" })
const savingLLM = ref(false)

// AI Prompt
const aiPrompt = ref("")
const savingPrompt = ref(false)

// Users
const users = ref([])
const userDialog = ref(false)
const savingUser = ref(false)
const userFormRef = ref(null)
const userForm = reactive({ username: "", password: "", real_name: "", role: "interviewer" })
const userRules = {
  username: [{ required: true, message: "请输入账号", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
  real_name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
}

const DEFAULT_PROMPT = `你是一位专业的AI招聘面试分析师。请根据提供的面试对话全文，生成一份结构化的面试总结报告。

请严格按以下JSON格式输出，不要包含markdown标记：
{
    "candidate_name": "候选人姓名（从对话中提取）",
    "position": "应聘岗位",
    "work_years": "工作年限",
    "expected_salary": "期望薪资",
    "skill_match": "核心技能匹配度分析（2-3句话）",
    "project_highlights": "项目经验亮点与疑点（2-3点）",
    "qa_summary": "面试核心问答摘要（2-3个关键问答）",
    "strengths": "候选人优势（2-3点）",
    "weaknesses": "候选人不足/待确认项（2-3点）",
    "overall_assessment": "综合初评建议（2-3句话）"
}
如果对话中没有提到某些信息，请填写"未提及"。`

async function loadConfigs() {
  try {
    const resp1 = await getConfig("llm_api_base")
    if (resp1.data.code === 200) llmConfig.api_base = resp1.data.data.config_value
    const resp2 = await getConfig("llm_api_key")
    if (resp2.data.code === 200) llmConfig.api_key = resp2.data.data.config_value
    const resp3 = await getConfig("llm_model")
    if (resp3.data.code === 200) llmConfig.model = resp3.data.data.config_value
    const resp4 = await getConfig("ai_prompt")
    if (resp4.data.code === 200) aiPrompt.value = resp4.data.data.config_value
  } catch {}
}

async function saveLLMConfig() {
  savingLLM.value = true
  try {
    await updateConfig("llm_api_base", { config_value: llmConfig.api_base })
    await updateConfig("llm_api_key", { config_value: llmConfig.api_key })
    await updateConfig("llm_model", { config_value: llmConfig.model })
    ElMessage.success("大模型配置已保存（重启后端生效）")
  } catch { ElMessage.error("保存失败") }
  savingLLM.value = false
}

async function savePrompt() {
  savingPrompt.value = true
  try {
    await updateConfig("ai_prompt", { config_value: aiPrompt.value })
    ElMessage.success("Prompt已更新")
  } catch { ElMessage.error("保存失败") }
  savingPrompt.value = false
}

function resetPrompt() {
  aiPrompt.value = DEFAULT_PROMPT
}

async function loadUsers() {
  try {
    const resp = await getUsers()
    if (resp.data.code === 200) users.value = resp.data.data
  } catch {}
}

function showAddUser() {
  Object.assign(userForm, { username: "", password: "", real_name: "", role: "interviewer" })
  userDialog.value = true
}

async function saveUser() {
  const valid = await userFormRef.value.validate().catch(() => false)
  if (!valid) return
  savingUser.value = true
  try {
    const resp = await createUser(userForm)
    if (resp.data.code === 200) {
      ElMessage.success("创建成功")
      userDialog.value = false
      loadUsers()
    } else {
      ElMessage.error(resp.data.msg)
    }
  } catch { ElMessage.error("创建失败") }
  savingUser.value = false
}

onMounted(() => { loadConfigs(); loadUsers() })
</script>
