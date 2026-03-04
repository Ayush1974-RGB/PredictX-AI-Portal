import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

const API = process.env.REACT_APP_API_URL
  ? process.env.REACT_APP_API_URL.replace('/api', '')
  : 'http://localhost:5000';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('px_token');
    if (token) {
      axios.get(`${API}/api/auth/verify`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => setUser(res.data.user))
      .catch(() => localStorage.removeItem('px_token'))
      .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await axios.post(`${API}/api/auth/login`, { email, password });
    localStorage.setItem('px_token', res.data.token);
    setUser(res.data.user);
    return res.data;
  };

  const signup = async (username, email, password) => {
    const res = await axios.post(`${API}/api/auth/signup`, { username, email, password });
    localStorage.setItem('px_token', res.data.token);
    setUser(res.data.user);
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('px_token');
    setUser(null);
  };

  axios.interceptors.request.use(cfg => {
    const token = localStorage.getItem('px_token');
    if (token) cfg.headers.Authorization = `Bearer ${token}`;
    return cfg;
  });

  if (loading) return (
    <div style={{
      display:'flex', height:'100vh', alignItems:'center',
      justifyContent:'center', background:'#070810',
      color:'#00e5ff', fontFamily:'Syne,sans-serif', fontSize:'1.2rem'
    }}>
      Loading PredictX…
    </div>
  );

  return (
    <AuthContext.Provider value={{ user, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}