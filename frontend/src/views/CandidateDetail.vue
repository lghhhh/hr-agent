<template>
  <div v-loading="loading">
    <el-button text @click="$router.back()" style="margin-bottom: 12px;">
      <el-icon><ArrowLeft /></el-icon> 返回
    </el-button>

    <!-- Candidate Info -->
    <el-card style="margin-bottom: 16px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold;">{{ candidate?.name }} — 基础信息</span>
          <el-tag :type="statusTag(candidate?.current_status)" size="small">
            {{ statusLabel(candidate?.current_status) }}
          </el-tag>
        </div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="姓名">{{ candidate?.name }}</el-descriptions-item>
        <el-descriptions-item label="联系方式">{{ candidate?.phone }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ candidate?.email }}</el-descriptions-item>
        <el-descriptions-item label="应聘岗位">{{ candidate?.position_name }}</el-descriptions-item>
        <el-descriptions-item label="工作年限">{{ candidate?.work_years }}</el-descriptions-item>
        <el-descriptions-item label="期望薪资">{{ candidate?.expected_salary }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ candidate?.create_time }}</el-descriptions-item>
        <el-descriptions-item label="简历链接">
          <el-link v-if="candidate?.resume_url" :href="candidate.resume_url" target="_blank" type="primary">查看简历</el-link>
          <span v-else>—</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- Interview Timeline -->
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold;">面试记录</span>
          <el-button type="primary" size="small" @click="goInterview">安排面试</el-button>
        </div>
      </template>

      <el-timeline v-if="interviews.length > 0">
        <el-timeline-item
          v-for="iv in interviews"
          :key="iv.id"
          :timestamp="iv.create_time || ''"
          :color="iv.is_pass === 1 ? '#67c23a' : iv.is_pass === 0 ? '#f56c6c' : iv.is_pass === 2 ? '#e6a23c' : '#909399'"
        >
          <div style="font-weight: bold;">{{ iv.round_name }}</div>
          <div v-if="iv.interviewer_name">面试官：{{ iv.interviewer_name }}</div>
          <div>结果：
            <el-tag v-if="iv.is_pass === 1" type="success" size="small">通过</el-tag>
            <el-tag v-else-if="iv.is_pass === 0" type="danger" size="small">不通过</el-tag>
            <el-tag v-else-if="iv.is_pass === 2" type="warning" size="small">待定</el-tag>
            <el-tag v-else type="info" size="small">待评价</el-tag>
            <span v-if="iv.fail_reason" style="margin-left: 8px; color: #f56c6c;">原因：{{ iv.fail_reason }}</span>
          </div>
          <el-collapse style="margin-top: 8px;">
            <!-- 干净报告文字 -->
            <el-collapse-item v-if="iv.ai_summary_text" title="面试总结报告" name="text">
              <div style="white-space: pre-wrap; font-size: 13px; line-height: 1.7;">
                {{ iv.ai_summary_text }}
              </div>
            </el-collapse-item>
            <!-- 结构化 JSON 数据 -->
            <el-collapse-item v-if="iv.ai_summary" title="结构化数据" name="json">
              <div v-if="parsedSummary(iv.ai_summary)" style="font-size: 13px;">
                <el-descriptions v-for="(val, key) in parsedSummary(iv.ai_summary)" :key="key" :column="1" border style="margin-bottom: 12px;">
                  <template #title>
                    <span style="font-weight: bold;">{{ summaryLabel(key) }}</span>
                  </template>
                  <el-descriptions-item>
                    <span v-if="typeof val === 'object'">{{ JSON.stringify(val, null, 2) }}</span>
                    <span v-else>{{ val }}</span>
                  </el-descriptions-item>
                </el-descriptions>
              </div>
              <div v-else style="white-space: pre-wrap; font-size: 13px;">{{ iv.ai_summary }}</div>
            </el-collapse-item>
            <el-collapse-item v-if="iv.interviewer_comment" title="面试官评价" name="comment">
              <div style="font-size: 13px;">{{ iv.interviewer_comment }}</div>
            </el-collapse-item>
          </el-collapse>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无面试记录" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { getCandidateDetail } from "../api/candidate"
import { ArrowLeft } from "@element-plus/icons-vue"

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const candidate = ref(null)
const interviews = ref([])

const summaryLabels = {
  candidate_name: "姓名",
  position: "应聘岗位",
  work_years: "工作年限",
  expected_salary: "期望薪资",
  skill_match: "核心技能匹配度",
  core_skills_match: "核心技能匹配度",
  project_highlights: "项目经验亮点",
  project_doubts: "项目存疑点",
  interview_qna_summary: "面试问答摘要",
  qa_summary: "面试问答摘要",
  strengths: "候选人优势",
  weaknesses: "候选人不足/待考察",
  overall_assessment: "综合评估",
  ability_level: "能力评级",
  evaluation_detail: "综合评价",
  recommend_next_round: "下一轮推荐",
  name: "姓名",
  apply_position: "应聘岗位",
}

const statusMap = {
  pending: "待初面", pass1: "初面通过", pass2: "复面通过",
  fail: "已淘汰", offer: "拟录用", pending_review: "待定",
}
const statusTag = (s) => ({ pending: "info", pass1: "primary", pass2: "warning", fail: "danger", offer: "success", pending_review: "warning" }[s] || "info")
const statusLabel = (s) => statusMap[s] || s

function parsedSummary(jsonStr) {
  try {
    const obj = JSON.parse(jsonStr)
    // 去掉 summary_text 避免重复
    const { summary_text, ...rest } = obj
    // 展开嵌套对象（candidate_basic、comprehensive_evaluation）到顶层
    const flat = {}
    for (const [key, val] of Object.entries(rest)) {
      if (val && typeof val === 'object' && !Array.isArray(val)) {
        for (const [subKey, subVal] of Object.entries(val)) {
          const combinedKey = `${key}.${subKey}`
          flat[combinedKey] = typeof subVal === 'string' ? subVal : JSON.stringify(subVal, null, 2)
        }
      } else {
        flat[key] = val
      }
    }
    return flat
  } catch {
    return null
  }
}

function summaryLabel(key) {
  // 处理 nested.key 格式
  const label = summaryLabels[key] || summaryLabels[key.split('.').pop()] || key
  return label
}

function goInterview() {
  router.push(`/interview/${route.params.id}`)
}

async function fetchDetail() {
  loading.value = true
  try {
    const resp = await getCandidateDetail(route.params.id)
    if (resp.data.code === 200) {
      candidate.value = resp.data.data.candidate
      // 只保留已提交的面试记录（is_pass !== null）
      const all = resp.data.data.interviews || []
      interviews.value = all.filter(iv => iv.is_pass !== null)
    }
  } catch {}
  loading.value = false
}

onMounted(() => fetchDetail())
</script>