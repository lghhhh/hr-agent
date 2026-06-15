<template>
  <div>
    <!-- Stats Cards -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="4" v-for="card in cards" :key="card.label">
        <el-card shadow="hover" :body-style="{ padding: '16px' }">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <div style="font-size: 12px; color: #909399;">{{ card.label }}</div>
              <div style="font-size: 28px; font-weight: bold; margin-top: 6px;">{{ card.value }}</div>
            </div>
            <el-icon :size="36" :color="card.color">
              <component :is="card.icon" />
            </el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="20">
      <el-col :span="14">
        <el-card>
          <template #header><span style="font-weight: bold;">面试趋势</span></template>
          <div ref="trendChart" style="height: 320px;"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card>
          <template #header><span style="font-weight: bold;">岗位招聘进度</span></template>
          <div ref="positionChart" style="height: 320px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue"
import { getOverview, getTrend, getPositionStats } from "../api/stats"
import * as echarts from "echarts"
import { User, Edit, CircleCheck, CircleClose, DataBoard } from "@element-plus/icons-vue"

const cards = ref([
  { label: "总候选人", value: 0, icon: User, color: "#409eff" },
  { label: "待面试", value: 0, icon: Edit, color: "#e6a23c" },
  { label: "面试通过", value: 0, icon: CircleCheck, color: "#67c23a" },
  { label: "已淘汰", value: 0, icon: CircleClose, color: "#f56c6c" },
  { label: "拟录用", value: 0, icon: DataBoard, color: "#909399" },
])

const trendChart = ref(null)
const positionChart = ref(null)
let trendInstance = null
let positionInstance = null

async function loadStats() {
  try {
    const ov = await getOverview()
    if (ov.data.code === 200) {
      const d = ov.data.data
      cards.value[0].value = d.total_candidates
      cards.value[1].value = d.pending_interview
      cards.value[2].value = (d.pass1 || 0) + (d.pass2 || 0)
      cards.value[3].value = d.eliminated
      cards.value[4].value = d.offered
    }
  } catch {}

  try {
    const tr = await getTrend()
    if (tr.data.code === 200) renderTrend(tr.data.data)
  } catch {}

  try {
    const ps = await getPositionStats()
    if (ps.data.code === 200) renderPosition(ps.data.data)
  } catch {}
}

function renderTrend(data) {
  nextTick(() => {
    if (trendInstance) trendInstance.dispose()
    const el = trendChart.value
    if (!el) return
    trendInstance = echarts.init(el)
    const dates = (data.daily_new || []).map((d) => d.date)
    const newCounts = (data.daily_new || []).map((d) => d.count)
    const interviewCounts = (data.daily_interviews || []).map((d) => d.count)
    trendInstance.setOption({
      tooltip: { trigger: "axis" },
      legend: { data: ["新增候选人", "面试完成数"] },
      grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
      xAxis: { type: "category", data: dates },
      yAxis: { type: "value", minInterval: 1 },
      series: [
        { name: "新增候选人", type: "line", data: newCounts, smooth: true, itemStyle: { color: "#409eff" } },
        { name: "面试完成数", type: "line", data: interviewCounts, smooth: true, itemStyle: { color: "#67c23a" } },
      ],
    })
  })
}

function renderPosition(data) {
  nextTick(() => {
    if (positionInstance) positionInstance.dispose()
    const el = positionChart.value
    if (!el) return
    positionInstance = echarts.init(el)
    const names = (data || []).map((p) => p.position_name)
    const totals = (data || []).map((p) => p.total)
    positionInstance.setOption({
      tooltip: { trigger: "axis" },
      grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
      xAxis: { type: "category", data: names },
      yAxis: { type: "value", minInterval: 1 },
      series: [
        { type: "bar", data: totals, itemStyle: { color: "#409eff" }, barWidth: "40%" },
      ],
    })
  })
}

onMounted(() => loadStats())
onUnmounted(() => {
  if (trendInstance) trendInstance.dispose()
  if (positionInstance) positionInstance.dispose()
})
</script>
