import axios from "./index"

export function getCandidateList(params) {
  return axios.get("/api/candidate/list", { params })
}

export function addCandidate(data) {
  return axios.post("/api/candidate/add", data)
}

export function updateCandidate(cand_id, data) {
  return axios.put("/api/candidate/update", data, { params: { cand_id } })
}

export function deleteCandidate(cand_id) {
  return axios.delete("/api/candidate/delete", { params: { cand_id } })
}

export function getCandidateDetail(cand_id) {
  return axios.get(`/api/candidate/detail/${cand_id}`)
}
