import axios from "./index"

export function exportCandidateList(params) {
  return axios.get("/api/export/candidate-list", { params, responseType: "blob" })
}

export function exportInterviewReport(candidate_id) {
  return axios.get(`/api/export/interview-report/${candidate_id}`, { responseType: "blob" })
}
