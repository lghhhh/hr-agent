import { defineStore } from "pinia"
import axios from "axios"

export const useAppStore = defineStore("app", {
  state: () => ({
    user: JSON.parse(localStorage.getItem("user") || "null"),
    token: localStorage.getItem("token") || "",
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === "admin",
    userName: (state) => state.user?.real_name || "",
  },
  actions: {
    setUser(user) {
      this.user = user
      localStorage.setItem("user", JSON.stringify(user))
    },
    setToken(token) {
      this.token = token
      localStorage.setItem("token", token)
    },
    logout() {
      this.user = null
      this.token = ""
      localStorage.removeItem("token")
      localStorage.removeItem("user")
    },
    async fetchUserInfo() {
      try {
        const resp = await axios.get("/api/auth/userinfo")
        if (resp.data.code === 200) {
          this.setUser(resp.data.data)
        }
      } catch {
        this.logout()
      }
    },
  },
})
