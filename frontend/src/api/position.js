import axios from "./index"

export function getPositionList() {
  return axios.get("/api/position/list")
}

export function addPosition(data) {
  return axios.post("/api/position/add", data)
}

export function updatePosition(pos_id, data) {
  return axios.put("/api/position/update", data, { params: { pos_id } })
}

export function deletePosition(pos_id) {
  return axios.delete("/api/position/delete", { params: { pos_id } })
}
