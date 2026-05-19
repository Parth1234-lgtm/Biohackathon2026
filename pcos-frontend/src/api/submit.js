import axios from "axios";

const API_URL = "http://127.0.0.1:8000/submit";

export async function submitDiagnosis(payload) {
  const { data } = await axios.post(API_URL, payload, {
    headers: { "Content-Type": "application/json" },
  });
  return data;
}
