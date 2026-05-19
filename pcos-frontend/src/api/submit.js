import axios from "axios";

// Automatically detects if you are running 'npm run dev' vs live on Vercel
const BASE_URL = import.meta.env.DEV 
  ? "http://127.0.0.1:8000" 
  : "https://biohackathon2026-1.onrender.com";

const API_URL = `${BASE_URL}/submit`;

export async function submitDiagnosis(payload) {
    const { data } = await axios.post(API_URL, payload, {
        headers: { "Content-Type": "application/json" },
    });
    return data;
}
