// utils/api.js — Centralized API calls for all 4 ML modules
import axios from 'axios';

// All requests proxy through CRA → http://localhost:5000
// (set via "proxy" in package.json)

export const api = {
  // ── Auth ──────────────────────────────────────────
  login:  (email, password)            => axios.post('/api/auth/login',  { email, password }),
  signup: (username, email, password)  => axios.post('/api/auth/signup', { username, email, password }),
  verify: ()                           => axios.get('/api/auth/verify'),

  // ── Gold (India) ──────────────────────────────────
  goldPredict: (data) => axios.post('/api/gold/predict',    data),
  goldHistory: ()     => axios.get('/api/gold/history'),

  // ── Fraud ─────────────────────────────────────────
  fraudPredict: (data) => axios.post('/api/fraud/predict',  data),

  // ── Spam ──────────────────────────────────────────
  spamPredict:  (data) => axios.post('/api/spam/predict',   data),

  // ── Rainfall ──────────────────────────────────────
  rainPredict:  (data) => axios.post('/api/rainfall/predict', data),
};

// Format ₹ in Indian lakh/crore style
export function inrFmt(n) {
  if (n >= 10000000) return '₹' + (n / 10000000).toFixed(2) + ' Cr';
  if (n >= 100000)   return '₹' + (n / 100000).toFixed(2)   + ' L';
  return '₹' + Math.round(n).toLocaleString('en-IN');
}
