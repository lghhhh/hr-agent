import axios from "./index"

export function login(data) {
  return axios.post("/api/auth/login", data)
}

export function getUserInfo() {
  return axios.get("/api/auth/userinfo")
}

export function getUsers() {
  return axios.get("/api/auth/users")
}

export function createUser(data) {
  return axios.post("/api/auth/users", data)
}
