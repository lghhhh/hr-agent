import axios from "./index"

export function getOverview() {
  return axios.get("/api/stats/overview")
}

export function getTrend(days = 30) {
  return axios.get("/api/stats/trend", { params: { days } })
}

export function getPositionStats() {
  return axios.get("/api/stats/position")
}
