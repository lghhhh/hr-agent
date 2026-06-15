import { createRouter, createWebHashHistory } from "vue-router"

const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/Login.vue"),
  },
  {
    path: "/",
    component: () => import("../components/Layout.vue"),
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        name: "Dashboard",
        component: () => import("../views/Dashboard.vue"),
        meta: { title: "数据看板" },
      },
      {
        path: "candidates",
        name: "CandidateList",
        component: () => import("../views/CandidateList.vue"),
        meta: { title: "候选人管理" },
      },
      {
        path: "candidate/:id",
        name: "CandidateDetail",
        component: () => import("../views/CandidateDetail.vue"),
        meta: { title: "候选人详情" },
      },
      {
        path: "interview/:candidateId",
        name: "InterviewProcess",
        component: () => import("../views/InterviewProcess.vue"),
        meta: { title: "面试流程" },
      },
      {
        path: "positions",
        name: "PositionManage",
        component: () => import("../views/PositionManage.vue"),
        meta: { title: "岗位管理" },
      },
      {
        path: "settings",
        name: "Settings",
        component: () => import("../views/Settings.vue"),
        meta: { title: "系统设置" },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token")
  if (to.name !== "Login" && !token) {
    next({ name: "Login" })
  } else {
    next()
  }
})

export default router
