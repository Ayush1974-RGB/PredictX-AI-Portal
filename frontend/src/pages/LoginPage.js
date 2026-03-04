// pages/LoginPage.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './LoginPage.css';

export default function LoginPage() {
  const { login, signup } = useAuth();
  const navigate = useNavigate();

  const [tab, setTab]   = useState('login');   // 'login' | 'signup'
  const [form, setForm] = useState({ username:'', email:'', password:'' });
  const [showPw, setShowPw] = useState(false);
  const [error, setError]   = useState('');
  const [loading, setLoading] = useState(false);

  const handle = (e) => setForm(p => ({ ...p, [e.target.name]: e.target.value }));

  const submit = async () => {
    setError(''); setLoading(true);
    try {
      if (tab === 'login') {
        await login(form.email, form.password);
      } else {
        if (!form.username) return setError('Name is required');
        await signup(form.username, form.email, form.password);
      }
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const onKey = (e) => { if (e.key === 'Enter') submit(); };

  return (
    <div className="auth-page">
      <div className="auth-orbs"><span /><span /></div>
      <div className="auth-container">

        <div className="auth-logo">
          <div className="logo-icon">🧠</div>
          <h1>PredictX</h1>
          <p>AI PREDICTION PORTAL</p>
        </div>

        <div className="auth-card">
          {/* Tabs */}
          <div className="auth-tabs">
            <button className={`auth-tab ${tab==='login'?'active':''}`}  onClick={()=>{setTab('login'); setError('');}}>Sign In</button>
            <button className={`auth-tab ${tab==='signup'?'active':''}`} onClick={()=>{setTab('signup');setError('');}}>Create Account</button>
          </div>

          {/* Name (signup only) */}
          {tab === 'signup' && (
            <div className="form-group">
              <label>Full Name</label>
              <input name="username" value={form.username}
                onChange={handle} onKeyDown={onKey}
                placeholder="Your name" autoFocus />
            </div>
          )}

          {/* Email */}
          <div className="form-group">
            <label>Email Address</label>
            <input type="email" name="email" value={form.email}
              onChange={handle} onKeyDown={onKey}
              placeholder="you@example.com" />
          </div>

          {/* Password with eye toggle */}
          <div className="form-group">
            <label>Password</label>
            <div className="pw-wrap">
              <input
                type={showPw ? 'text' : 'password'}
                name="password" value={form.password}
                onChange={handle} onKeyDown={onKey}
                placeholder={tab==='signup' ? 'Min. 6 characters' : '••••••••'}
              />
              <button type="button" className="pw-eye"
                onClick={() => setShowPw(p => !p)} tabIndex={-1}>
                {showPw ? (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/>
                    <path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                )}
              </button>
            </div>
          </div>

          {/* Error */}
          {error && <div className="auth-error">{error}</div>}

          {/* Submit */}
          <button className="btn-primary" onClick={submit} disabled={loading}
            style={{marginTop:'1rem'}}>
            {loading
              ? <><span className="spinner" style={{borderTopColor:'#000'}} /> &nbsp;Please wait…</>
              : tab === 'login' ? 'Sign In to PredictX' : 'Create Account'
            }
          </button>

          <p style={{textAlign:'center',marginTop:'1.5rem',fontSize:'0.8rem',color:'var(--text-muted)'}}>
            💡 New here? Switch to Create Account above
          </p>
        </div>
      </div>
    </div>
  );
}
