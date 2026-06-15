<template>
  <el-container style="min-height: 100vh">
    <!-- Sidebar -->
    <el-aside :width="isCollapse ? '64px' : '220px'" style="background: #304156; transition: width 0.3s">
      <div class="logo" style="height: 60px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 18px; font-weight: bold; border-bottom: 1px solid rgba(255,255,255,0.1)">
        <el-icon v-if="isCollapse" :size="24"><Monitor /></el-icon>
        <span v-else>AI 招聘系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <template #title>数据看板</template>
        </el-menu-item>
        <el-menu-item index="/candidates">
          <el-icon><User /></el-icon>
          <template #title>候选人管理</template>
        </el-menu-item>
        <el-menu-item index="/positions">
          <el-icon><Briefcase /></el-icon>
          <template #title>岗位管理</template>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- Header -->
      <el-header style="background: #fff; border-bottom: 1px solid #e6e6e6; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; height: 50px;">
        <div style="display: flex; align-items: center;">
          <el-button :icon="isCollapse ? Expand : Fold" text @click="isCollapse = !isCollapse" />
          <span style="margin-left: 12px; font-size: 15px; color: #333;">{{ pageTitle }}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
          <el-tag type="success" v-if="store.isAdmin">管理员</el-tag>
          <el-tag type="info" v-else>面试官</el-tag>
          <span>{{ store.userName }}</span>
          <el-button type="danger" text @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>

      <!-- Main Content -->
      <el-main style="background: #f0f2f5; padding: 20px;">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useAppStore } from "../store"
import { Monitor, DataBoard, User, Briefcase, Setting } from "@element-plus/icons-vue"

const route = useRoute()
const router = useRouter()
const store = useAppStore()

const isCollapse = ref(false)
const pageTitle = computed(() => route.meta?.title || "")

// Only redirect on init, don't watch
const activeMenu = computed(() => {
  // For detail pages, keep parent menu highlighted
  if (route.path.startsWith("/candidate/") || route.path.startsWith("/interview/")) {
    return "/candidates"
  }
  return route.path
})

function handleLogout() {
  store.logout()
  router.push("/login")
}
</script>
