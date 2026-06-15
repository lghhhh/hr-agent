<template>
  <div v-loading="loading">
    <el-button text @click="$router.back()" style="margin-bottom: 12px;">
      <el-icon><ArrowLeft /></el-icon> 返回候选人列表
    </el-button>

    <el-row :gutter="20">
      <!-- Left: Candidate Info -->
      <el-col :span="7">
        <el-card>
          <template #header><span style="font-weight: bold;">候选人信息</span></template>
          <div v-if="candidate">
            <p><strong>姓名：</strong>{{ candidate.name }}</p>
            <p><strong>岗位：</strong>{{ candidate.position_name }}</p>
            <p><strong>当前状态：</strong>
              <el-tag :type="statusTag(candidate.current_status)" size="small">
                {{ statusLabel(candidate.current_status) }}
              </el-tag>
            </p>
            <p><strong>电话：</strong>{{ candidate.phone }}</p>
            <p><strong>邮箱：</strong>{{ candidate.email }}</p>
          </div>
          <el-empty v-else description="加载中..." />
        </el-card>
      </el-col>

      <!-- Right: Tabs for each round -->
      <el-col :span="17">
        <el-card>
          <el-tabs v-model="activeTab" type="border-card">
            <el-tab-pane
              v-for="(tab, idx) in roundTabs"
              :key="tab.num"
              :label="tab.label"
              :name="String(tab.num)"
              :disabled="tab.disabled"
            >
              <!-- Round not started yet -->
              <template v-if="!tab.interview">
                <el-empty :description="`${tab.label}尚未开始`">
                  <el-button
                    v-if="tab.canStart"
                    type="primary"
                    @click="startRound(tab.num)"
                  >
                    开始{{ tab.label }}
                  </el-button>
                  <div v-else style="color: #909399; font-size: 13px;">
                    请先完成上一轮面试
                  </div>
                </el-empty>
              </template>

              <!-- Round exists — locked -->
              <template v-else-if="tab.locked">
                <el-alert
                  :title="tab.lockReason"
                  type="warning"
                  :closable="false"
                  show-icon
                  style="margin-bottom: 16px;"
                />
                <div style="font-size: 14px; line-height: 1.8;">
                  <p><strong>面试官评价：</strong><br>{{ tab.interview.interviewer_comment || '（无）' }}</p>
                  <p><strong>面试结果：</strong>
                    <el-tag v-if="tab.interview.is_pass === 1" type="success" size="small">通过</el-tag>
                    <el-tag v-else-if="tab.interview.is_pass === 0" type="danger" size="small">不通过</el-tag>
                    <el-tag v-else-if="tab.interview.is_pass === 2" type="warning" size="small">待定</el-tag>
                    <el-tag v-else type="info" size="small">未评价</el-tag>
                  </p>
                  <p v-if="tab.interview.fail_reason"><strong>淘汰原因：</strong>{{ tab.interview.fail_reason }}</p>
                  <el-collapse style="margin-top: 8px;">
                    <el-collapse-item title="查看面试对话" name="dialog">
                      <pre style="white-space: pre-wrap; font-size: 13px;">{{ tab.interview.dialogue_raw || '（无）' }}</pre>
                    </el-collapse-item>
                    <el-collapse-item v-if="tab.interview.ai_summary_text" title="AI 面试总结报告" name="summary">
                      <div style="white-space: pre-wrap; font-size: 13px; line-height: 1.7;">{{ tab.interview.ai_summary_text }}</div>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </template>

              <!-- Round exists — editable -->
              <template v-else>
                <el-form label-position="top">
                  <el-form-item label="面试对话文本">
                    <el-input
                      v-model="tab.form.dialogueRaw"
                      type="textarea"
                      :rows="5"
                      placeholder="粘贴面试对话全文…"
                    />
                  </el-form-item>

                  <el-form-item>
                    <el-button type="success" @click="handleGenerateSummary(tab)" :loading="tab.form.generating">
                      <el-icon><MagicStick /></el-icon> AI生成总结
                    </el-button>
                  </el-form-item>

                  <el-form-item v-if="tab.form.aiSummary" label="面试总结报告（可编辑）">
                    <el-input
                      v-model="tab.form.summaryText"
                      type="textarea"
                      :rows="10"
                      placeholder="AI生成的面试总结报告将显示在这里…"
                    />
                    <div style="font-size: 12px; color: #909399; margin-top: 4px;">
                      此文本将展示在候选人详情页。结构化 JSON 数据在下方单独保存。
                    </div>
                  </el-form-item>

                  <el-collapse v-if="tab.form.aiSummary" style="margin-bottom: 16px;">
                    <el-collapse-item title="查看结构化数据（仅作数据存储）" name="json-data">
                      <el-input v-model="tab.form.aiSummaryJson" type="textarea" :rows="6" />
                    </el-collapse-item>
                  </el-collapse>

                  <el-form-item label="面试官评价">
                    <el-input
                      v-model="tab.form.interviewerComment"
                      type="textarea"
                      :rows="3"
                      placeholder="请给出您的综合评价…"
                    />
                  </el-form-item>

                  <el-form-item label="面试结果">
                    <el-radio-group v-model="tab.form.isPass">
                      <el-radio :value="1" border>通过</el-radio>
                      <el-radio :value="2" border>待定</el-radio>
                      <el-radio :value="0" border>不通过</el-radio>
                    </el-radio-group>
                  </el-form-item>

                  <el-form-item v-if="tab.form.isPass === 0" label="淘汰原因">
                    <el-input v-model="tab.form.failReason" placeholder="请说明淘汰原因…" />
                  </el-form-item>

                  <el-form-item>
                    <el-button type="primary" size="large" @click="handleSubmit(tab)" :loading="tab.form.submitting">
                      {{ tab.interview.is_pass !== null ? '更新面试结果' : '提交面试结果' }}
                    </el-button>
                  </el-form-item>

                  <!-- Show current result if already submitted -->
                  <div
                    v-if="tab.interview.is_pass !== null"
                    style="background: #f0f9eb; padding: 12px; border-radius: 4px; margin-top: 8px;"
                  >
                    <el-icon color="#67c23a" :size="18"><CircleCheck /></el-icon>
                    <span style="margin-left: 6px; font-weight: bold;">
                      当前结果：{{ tab.interview.is_pass === 1 ? '已通过' : tab.interview.is_pass === 2 ? '待定' : '已淘汰' }}
                    </span>
                    <span style="margin-left: 12px; font-size: 13px; color: #909399;">（修改后点"更新面试结果"保存）</span>
                  </div>
                </el-form>
              </template>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue"
import { useRoute } from "vue-router"
import { getCandidateDetail } from "../api/candidate"
import { createInterview, updateSummary, submitInterview } from "../api/interview"
import { generateSummary } from "../api/ai"
import { ElMessage } from "element-plus"
import { ArrowLeft, MagicStick, CircleCheck } from "@element-plus/icons-vue"

const route = useRoute()
const candidateId = computed(() => Number(route.params.candidateId))
const loading = ref(false)
const candidate = ref(null)
const interviews = ref([])        // all interviews from API
const activeTab = ref("1")

const roundNames = { 1: "初面", 2: "复面", 3: "终面" }

const statusMap = {
  pending: "待初面", pass1: "初面通过", pass2: "复面通过",
  fail: "已淘汰", offer: "拟录用", pending_review: "待定",
}
const statusTag = (s) => ({
  pending: "info", pass1: "primary", pass2: "warning",
  fail: "danger", offer: "success", pending_review: "warning",
}[s] || "info")
const statusLabel = (s) => statusMap[s] || s

// Build tab data from interviews — 取每个轮次最新的记录（id 最大）
const roundTabs = computed(() => {
  const tabs = []
  // Group by round_num, pick max id
  const latestByRound = {}
  for (const iv of interviews.value) {
    const prev = latestByRound[iv.round_num]
    if (!prev || iv.id > prev.id) latestByRound[iv.round_num] = iv
  }
  // 只有已提交结果的轮次才算"已开始"（用于锁定判断）
  const submittedRounds = Object.values(latestByRound).filter(iv => iv.is_pass !== null)
  const maxCreated = submittedRounds.length > 0 ? Math.max(...submittedRounds.map(iv => iv.round_num)) : 0

  for (let num = 1; num <= 3; num++) {
    const iv = latestByRound[num] || null
    const prevIv = num > 1 ? latestByRound[num - 1] : null

    // 只有上一轮"通过"才能开始下一轮
    let canStart = false
    if (!iv) {
      if (num === 1) canStart = true
      else if (prevIv && prevIv.is_pass === 1) canStart = true
    }

    // 锁定条件
    let locked = false
    if (iv) {
      // 1. 前面有任意一轮"不通过" → 流程终止，后续全部锁定
      for (let p = 1; p < num; p++) {
        const pIv = latestByRound[p]
        if (pIv && pIv.is_pass === 0) { locked = true; break }
      }
      // 2. 上一轮已提交但结果不是"通过"（待定/不通过）→ 阻塞
      if (!locked && prevIv && prevIv.is_pass !== null && prevIv.is_pass !== 1) {
        locked = true
      }
      // 3. 下一轮已开始 → 当前轮锁定
      if (!locked && maxCreated > num) locked = true
    }

    // 锁定原因
    let lockReason = ""
    if (locked && iv) {
      if (maxCreated > num) lockReason = "下一轮面试已开始，当前轮结果锁定（如需修改请先完成后续流程）"
      else if (prevIv && prevIv.is_pass === 0) lockReason = "上一轮面试结果为「不通过」，流程已终止，无法修改"
      else if (prevIv && prevIv.is_pass === 2) lockReason = "上一轮面试结果为「待定」，请先调整上一轮结果为「通过」"
      else if (prevIv && prevIv.is_pass === null) lockReason = "上一轮面试尚未提交结果，请先完成上一轮"
      else lockReason = "当前轮已锁定，无法修改"
    }

    tabs.push({
      num,
      label: roundNames[num],
      interview: iv,
      locked,
      lockReason,
      canStart,
      disabled: !iv && !canStart,
      form: initForm(iv),
    })
  }
  return tabs
})

function initForm(iv) {
  return reactive({
    dialogueRaw: iv?.dialogue_raw || "",
    aiSummary: !!(iv?.ai_summary_text || iv?.ai_summary),
    summaryText: iv?.ai_summary_text || "",
    aiSummaryJson: iv?.ai_summary || "",
    interviewerComment: iv?.interviewer_comment || "",
    isPass: iv?.is_pass ?? null,
    failReason: iv?.fail_reason || "",
    generating: false,
    submitting: false,
  })
}

async function fetchAll() {
  try {
    const resp = await getCandidateDetail(candidateId.value)
    if (resp.data.code === 200) {
      candidate.value = resp.data.data.candidate
      interviews.value = resp.data.data.interviews || []
    }
  } catch {}
}

async function startRound(num) {
  const name = roundNames[num]
  try {
    const resp = await createInterview({
      candidate_id: candidateId.value,
      round_num: num,
      round_name: name,
    })
    if (resp.data.code === 200) {
      ElMessage.success(`${name}已创建`)
      await fetchAll()  // reload to show the new interview
      activeTab.value = String(num)
    }
  } catch { ElMessage.error("创建失败") }
}

function buildSummaryText(data) {
  if (data.summary_text) return data.summary_text
  const parts = []
  const basic = data.candidate_basic
  if (basic) {
    parts.push(`候选人${basic.name || '（待提取）'}，应聘${basic.apply_position || '（待提取）'}，工作${basic.work_years || '（待提取）'}。`)
  } else if (data.candidate_name) {
    parts.push(`候选人${data.candidate_name}，应聘${data.position || '（待提取）'}。`)
  }
  const fieldLabels = {
    core_skills_match: '【核心技能匹配】',
    skill_match: '【核心技能匹配】',
    project_highlights: '【项目经验核心亮点】',
    project_doubts: '【项目疑点】',
    interview_qna_summary: '【面试问答摘要】',
    qa_summary: '【面试问答摘要】',
    strengths: '【候选人优势】',
    weaknesses: '【候选人不足】',
    overall_assessment: '【综合评估】',
  }
  for (const [key, label] of Object.entries(fieldLabels)) {
    const val = data[key]
    if (val && typeof val === 'string') parts.push(`${label}\n${val}`)
  }
  const ce = data.comprehensive_evaluation
  if (ce && typeof ce === 'object') {
    let detail = ce.evaluation_detail || ''
    if (ce.ability_level) detail = `能力评级：${ce.ability_level}\n` + detail
    if (ce.recommend_next_round) detail += `\n推荐进入下一轮：${ce.recommend_next_round}`
    if (detail) parts.push(`【综合评估】\n${detail}`)
  }
  return parts.join('\n\n') || JSON.stringify(data, null, 2)
}

async function handleGenerateSummary(tab) {
  const form = tab.form
  if (!form.dialogueRaw || form.dialogueRaw.trim().length < 10) {
    ElMessage.warning("请先输入面试对话文本（至少10个字符）")
    return
  }
  form.generating = true
  try {
    const resp = await generateSummary({
      dialogue_text: form.dialogueRaw,
      candidate_name: candidate.value?.name || "",
      position_id: candidate.value?.position_id,
    })
    if (resp.data.code === 200) {
      const data = resp.data.data
      form.aiSummary = true
      form.summaryText = buildSummaryText(data)
      form.aiSummaryJson = JSON.stringify(data, null, 2)
    } else {
      ElMessage.error(resp.data.msg || "AI解析失败")
    }
  } catch { ElMessage.error("AI调用失败") }
  form.generating = false
}

async function handleSubmit(tab) {
  const form = tab.form
  if (!tab.interview) return
  if (form.isPass === null) {
    ElMessage.warning("请选择面试结果")
    return
  }
  if (form.isPass === 0 && !form.failReason) {
    ElMessage.warning("请填写淘汰原因")
    return
  }

  if (form.aiSummaryJson || form.summaryText) {
    try {
      await updateSummary({
        interview_id: tab.interview.id,
        ai_summary: form.aiSummaryJson,
        ai_summary_text: form.summaryText,
      })
    } catch {}
  }

  form.submitting = true
  try {
    const resp = await submitInterview({
      interview_id: tab.interview.id,
      interviewer_comment: form.interviewerComment,
      is_pass: form.isPass,
      fail_reason: form.failReason,
      dialogue_raw: form.dialogueRaw,
    })
    if (resp.data.code === 200) {
      ElMessage.success(tab.interview.is_pass !== null ? "面试结果已更新" : "面试结果已提交")
      await fetchAll()  // refresh all data
    } else {
      ElMessage.error(resp.data.msg)
    }
  } catch { ElMessage.error("提交失败") }
  form.submitting = false
}

onMounted(async () => {
  loading.value = true
  await fetchAll()
  // Switch to the first unstarted or editable round
  const tabs = roundTabs.value
  const firstActive = tabs.find(t => !t.locked && (t.interview || t.canStart))
  if (firstActive) activeTab.value = String(firstActive.num)
  loading.value = false
})
</script>