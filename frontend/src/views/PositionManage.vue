<template>
  <div>
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold;">岗位管理</span>
          <el-button type="primary" size="small" @click="showAddDialog">+ 新增岗位</el-button>
        </div>
      </template>

      <el-table :data="list" stripe v-loading="loading">
        <el-table-column prop="position_name" label="岗位名称" min-width="160" />
        <el-table-column prop="department" label="所属部门" min-width="140" />
        <el-table-column prop="description" label="岗位描述" min-width="240" show-overflow-tooltip />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
              {{ row.status === 1 ? '开启' : '关闭' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="warning" link size="small" @click="showEditDialog(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleToggle(row)">
              {{ row.status === 1 ? '禁用' : '启用' }}
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Add / Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑岗位' : '新增岗位'" width="500px">
      <el-form :model="form" label-width="100px" ref="formRef" :rules="formRules">
        <el-form-item label="岗位名称" prop="position_name">
          <el-input v-model="form.position_name" />
        </el-form-item>
        <el-form-item label="所属部门">
          <el-input v-model="form.department" />
        </el-form-item>
        <el-form-item label="岗位描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { getPositionList, addPosition, updatePosition, deletePosition } from "../api/position"
import { ElMessage, ElMessageBox } from "element-plus"

const list = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const editId = ref(null)
const formRef = ref(null)

const form = reactive({ position_name: "", department: "", description: "" })
const formRules = { position_name: [{ required: true, message: "请输入岗位名称", trigger: "blur" }] }

async function fetchList() {
  loading.value = true
  try {
    const resp = await getPositionList()
    if (resp.data.code === 200) list.value = resp.data.data
  } catch {}
  loading.value = false
}

function showAddDialog() {
  isEdit.value = false; editId.value = null
  Object.assign(form, { position_name: "", department: "", description: "" })
  dialogVisible.value = true
}

function showEditDialog(row) {
  isEdit.value = true; editId.value = row.id
  Object.assign(form, { position_name: row.position_name, department: row.department, description: row.description })
  dialogVisible.value = true
}

async function save() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    let resp
    if (isEdit.value) {
      resp = await updatePosition(editId.value, form)
    } else {
      resp = await addPosition(form)
    }
    if (resp.data.code === 200) {
      ElMessage.success("保存成功")
      dialogVisible.value = false
      fetchList()
    }
  } catch { ElMessage.error("保存失败") }
  saving.value = false
}

async function handleToggle(row) {
  const newStatus = row.status === 1 ? 0 : 1
  try {
    await updatePosition(row.id, { status: newStatus })
    ElMessage.success(newStatus === 1 ? "已启用" : "已禁用")
    fetchList()
  } catch { ElMessage.error("操作失败") }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除岗位「${row.position_name}」吗？`, "提示", { type: "warning" })
    await deletePosition(row.id)
    ElMessage.success("删除成功")
    fetchList()
  } catch {}
}

onMounted(() => fetchList())
</script>
