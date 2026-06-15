import axios from "./index"

export function getConfigList() {
  return axios.get("/api/config/list")
}

export function getConfig(config_key) {
  return axios.get(`/api/config/get/${config_key}`)
}

export function updateConfig(config_key, data) {
  return axios.put(`/api/config/update/${config_key}`, data)
}
