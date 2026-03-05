// utils/api.js — Centralized API calls for all ML modules
import axios from "axios";

// Backend URL from Vercel environment variable
const BASE_URL =
  process.env.REACT_APP_API_URL ||
  "https://predictx-ai-portal-production-8a85.up.railway.app/api";

// Create axios instance
const instance = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach JWT token to every request
instance.interceptors.request.use((config) => {
  const token = localStorage.getItem("px_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// ───────────────── API FUNCTIONS ─────────────────

export const api = {
  // Auth
  login: (email, password) =>
    instance.post("/auth/login", { email, password }),

  signup: (username, email, password) =>
    instance.post("/auth/signup", { username, email, password }),

  verify: () => instance.get("/auth/verify"),

  // Gold Prediction
  goldPredict: (data) => instance.post("/gold/predict", data),
  goldHistory: () => instance.get("/gold/history"),

  // Fraud Detection
  fraudPredict: (data) => instance.post("/fraud/predict", data),

  // Spam Detection
  spamPredict: (data) => instance.post("/spam/predict", data),

  // Rainfall Prediction
  rainPredict: (data) => instance.post("/rainfall/predict", data),
};

// ───────────── Indian Rupee Formatter ─────────────

export function inrFmt(n) {
  if (n >= 10000000) return "₹" + (n / 10000000).toFixed(2) + " Cr";
  if (n >= 100000) return "₹" + (n / 100000).toFixed(2) + " L";
  return "₹" + Math.round(n).toLocaleString("en-IN");
}