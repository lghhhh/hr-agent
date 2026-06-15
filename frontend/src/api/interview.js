import axios from "./index"

export function createInterview(data) {
  return axios.post("/api/interview/create", data)
}

export function updateSummary(data) {
  return axios.put("/api/interview/update-summary", data)
}

export function submitInterview(data) {
  return axios.post("/api/interview/submit", data)
}

export function getInterviewDetail(interview_id) {
  return axios.get(`/api/interview/detail/${interview_id}`)
}
