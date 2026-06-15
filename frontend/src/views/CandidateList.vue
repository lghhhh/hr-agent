<template>
  <div>
    <!-- Toolbar -->
    <el-card style="margin-bottom: 16px;">
      <el-form :inline="true" :model="filters" size="small">
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="姓名/电话/邮箱" clearable style="width: 180px;" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable placeholder="全部" style="width: 140px;">
            <el-option label="待初面" value="pending" />
            <el-option label="初面通过" value="pass1" />
            <el-option label="复面通过" value="pass2" />
            <el-option label="已淘汰" value="fail" />
            <el-option label="拟录用" value="offer" />
          </el-select>
        </el-form-item>
        <el-form-item label="岗位">
          <el-select v-model="filters.position_id" clearable placeholder="全部" style="width: 160px;">
            <el-option v-for="p in positions" :key="p.id" :label="p.position_name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <el-button type="primary" size="small" @click="showAddDialog">+ 新增候选人</el-button>
        <el-button size="small" @click="handleExport">导出Excel</el-button>
      </div>
    </el-card>

    <!-- Table -->
    <el-card>
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="姓名" min-width="100" />
        <el-table-column prop="phone" label="联系方式" min-width="130" />
        <el-table-column prop="position_name" label="应聘岗位" min-width="140" />
        <el-table-column prop="work_years" label="工作年限" width="90" align="center" />
        <el-table-column label="当前状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.current_status)" size="small">{{ statusLabel(row.current_status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="面试轮次" width="80" align="center">
          <template #default="{ row }">{{ row.current_round || 0 }}/3</template>
        </el-table-column>
        <el-table-column prop="update_time" label="更新时间" width="170" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">详情</el-button>
            <el-button type="success" link size="small" @click="startInterview(row)">面试</el-button>
            <el-button type="warning" link size="small" @click="showEditDialog(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 16px; display: flex; justify-content: flex-end;">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchList"
        />
      </div>
    </el-card>

    <!-- Add / Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑候选人' : '新增候选人'" width="550px">
      <el-form :model="candidateForm" label-width="100px" ref="formRef" :rules="formRules">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="candidateForm.name" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系方式" prop="phone">
              <el-input v-model="candidateForm.phone" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="candidateForm.email" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="应聘岗位">
          <el-select v-model="candidateForm.position_id" clearable style="width: 100%;">
            <el-option v-for="p in positions" :key="p.id" :label="p.position_name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工作年限">
              <el-input v-model="candidateForm.work_years" placeholder="如：3年" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="期望薪资">
              <el-input v-model="candidateForm.expected_salary" placeholder="如：15K-20K" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="简历链接">
          <el-input v-model="candidateForm.resume_url" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCandidate" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { useRouter } from "vue-router"
import { getCandidateList, addCandidate, updateCandidate, deleteCandidate } from "../api/candidate"
import { getPositionList } from "../api/position"
import { exportCandidateList } from "../api/export"
import { ElMessage, ElMessageBox } from "element-plus"

const router = useRouter()
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const positions = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const editId = ref(null)
const formRef = ref(null)

const filters = reactive({ keyword: "", status: "", position_id: 0 })
const candidateForm = reactive({
  name: "", phone: "", email: "", position_id: null,
  work_years: "", expected_salary: "", resume_url: "",
})
const formRules = { name: [{ required: true, message: "请输入姓名", trigger: "blur" }] }

const statusMap = {
  pending: "待初面", pass1: "初面通过", pass2: "复面通过",
  fail: "已淘汰", offer: "拟录用", pending_review: "待定",
}
const statusTag = (s) => ({ pending: "info", pass1: "primary", pass2: "warning", fail: "danger", offer: "success", pending_review: "warning" }[s] || "info")
const statusLabel = (s) => statusMap[s] || s

function loadPositions() {
  getPositionList().then((resp) => {
    if (resp.data.code === 200) positions.value = resp.data.data
  }).catch(() => {})
}

async function fetchList() {
  loading.value = true
  try {
    const resp = await getCandidateList({ page: page.value, page_size: pageSize.value, ...filters })
    if (resp.data.code === 200) {
      list.value = resp.data.data.items
      total.value = resp.data.data.total
    }
  } catch {}
  loading.value = false
}

function search() { page.value = 1; fetchList() }
function resetFilters() {
  filters.keyword = ""; filters.status = ""; filters.position_id = 0
  page.value = 1; fetchList()
}

function showAddDialog() {
  isEdit.value = false; editId.value = null
  Object.assign(candidateForm, { name: "", phone: "", email: "", position_id: null, work_years: "", expected_salary: "", resume_url: "" })
  dialogVisible.value = true
}

function showEditDialog(row) {
  isEdit.value = true; editId.value = row.id
  Object.assign(candidateForm, {
    name: row.name, phone: row.phone, email: row.email,
    position_id: row.position_id, work_years: row.work_years,
    expected_salary: row.expected_salary, resume_url: row.resume_url,
  })
  dialogVisible.value = true
}

async function saveCandidate() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    let resp
    if (isEdit.value) {
      resp = await updateCandidate(editId.value, candidateForm)
    } else {
      resp = await addCandidate(candidateForm)
    }
    if (resp.data.code === 200) {
      ElMessage.success(isEdit.value ? "更新成功" : "添加成功")
      dialogVisible.value = false
      fetchList()
    } else {
      ElMessage.error(resp.data.msg)
    }
  } catch { ElMessage.error("操作失败") }
  saving.value = false
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除候选人「${row.name}」吗？`, "提示", { type: "warning" })
    const resp = await deleteCandidate(row.id)
    if (resp.data.code === 200) {
      ElMessage.success("删除成功")
      fetchList()
    }
  } catch {}
}

function viewDetail(row) {
  router.push(`/candidate/${row.id}`)
}

function startInterview(row) {
  router.push(`/interview/${row.id}`)
}

async function handleExport() {
  try {
    const resp = await exportCandidateList(filters)
    const url = URL.createObjectURL(new Blob([resp.data]))
    const a = document.createElement("a")
    a.href = url; a.download = "候选人列表.csv"; a.click()
    URL.revokeObjectURL(url)
    ElMessage.success("导出成功")
  } catch { ElMessage.error("导出失败") }
}

onMounted(() => { loadPositions(); fetchList() })
</script>
