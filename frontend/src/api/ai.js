import axios from "./index"

export function generateSummary(data) {
  return axios.post("/api/ai/generate-summary", data)
}
