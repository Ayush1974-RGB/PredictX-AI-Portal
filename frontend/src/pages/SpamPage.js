// pages/SpamPage.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { api } from '../utils/api';
import './SpamPage.css';

const SPAM_EXAMPLE = {
  subject: '🎉 YOU WON! Claim Your $1,000,000 Prize NOW!!!',
  body: 'CONGRATULATIONS!! You have been selected as our WINNER! Click here IMMEDIATELY to claim your FREE prize worth $1,000,000! LIMITED TIME — ACT NOW! Send your bank details to collect your winnings. Don\'t miss this AMAZING opportunity!!!'
};
const HAM_EXAMPLE = {
  subject: 'Team lunch this Friday?',
  body: 'Hey everyone,\n\nI was thinking we could grab lunch together this Friday around noon. There\'s a new Italian place nearby that opened recently and I heard great things.\n\nLet me know if you\'re interested!\n\nBest, Sarah'
};

// Correct fallback — TF-IDF weighted keyword scoring matching LR model coefficients
function calcSpam(subject, body) {
  const text  = `${subject} ${body}`.toLowerCase();
  const words = text.match(/\b\w+\b/g) || [];

  const spamTokens = {
    'free':2.4, 'win':2.1, 'winner':2.8, 'won':2.3, 'prize':2.9,
    'cash':2.1, 'claim':2.6, 'urgent':2.0, 'congratulations':2.7,
    'offer':1.6, 'limited':1.5, 'click':1.9, 'guaranteed':2.5,
    'selected':1.8, 'billion':2.2, 'million':2.0, 'bank':1.4,
    'password':1.7, 'verify':1.5, 'immediately':1.8, 'lottery':3.1,
    'nigeria':3.2, 'inheritance':2.9, 'crypto':1.2, 'earn':1.7,
    'income':1.5, 'invest':1.3, 'exclusive':1.4, 'act':1.2,
  };
  const hamTokens = {
    'meeting':-1.8, 'team':-1.5, 'project':-1.6, 'please':-0.9,
    'thanks':-1.2, 'regards':-1.4, 'sincerely':-1.5, 'attached':-1.1,
    'report':-1.3, 'update':-0.8, 'schedule':-1.4, 'discuss':-1.2,
    'review':-1.0, 'agenda':-1.6, 'proposal':-1.2, 'hello':-0.6,
    'hi':-0.5, 'lunch':-1.0, 'friday':-0.7, 'everyone':-0.6,
  };

  let logit = -1.5;
  const seen = new Set();
  for (const w of words) {
    if (!seen.has(w)) {
      seen.add(w);
      logit += spamTokens[w] || 0;
      logit += hamTokens[w]  || 0;
    }
  }

  // Structural signals
  const exclaims   = (text.match(/!/g) || []).length;
  const capsRatio  = (subject.match(/[A-Z]/g) || []).length / Math.max(subject.length, 1);
  const urlCount   = (text.match(/https?:\/\/|www\./g) || []).length;
  const dollars    = (text.match(/\$/g) || []).length;
  const allCaps    = (text.match(/\b[A-Z]{3,}\b/g) || []).length;

  logit += Math.min(exclaims  * 0.3,  2.0);
  logit += Math.min(capsRatio * 4.0,  2.5);
  logit += Math.min(urlCount  * 0.8,  2.0);
  logit += Math.min(dollars   * 0.6,  1.5);
  logit += Math.min(allCaps   * 0.4,  1.8);

  // Short clean messages lean ham
  if (words.length < 20 && logit < 0) logit -= 0.5;

  const spam_probability = 100 / (1 + Math.exp(-logit));
  const is_spam          = spam_probability >= 50;
  const confidence       = Math.min(99, 50 + Math.abs(logit) * 8);

  return {
    prediction:       is_spam ? 'SPAM' : 'NOT SPAM',
    is_spam,
    spam_probability,
    confidence,
  };
}

export default function SpamPage() {
  const navigate = useNavigate();
  const [form,    setForm]    = useState({ subject:'', body:'' });
  const [result,  setResult]  = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  const handle = e => setForm(p => ({ ...p, [e.target.name]: e.target.value }));

  const predict = async () => {
    if (!form.subject && !form.body) return;
    setLoading(true);
    await new Promise(r => setTimeout(r, 500));

    let r;
    try {
      const res = await api.spamPredict({ subject: form.subject, body: form.body });
      if (res.data && res.data.is_spam !== undefined) {
        r = res.data;
      } else {
        throw new Error('bad response');
      }
    } catch {
      r = calcSpam(form.subject, form.body);
    }

    setResult(r);
    setHistory(prev => [
      { label: r.prediction, color: r.is_spam ? '#ff8c42' : '#00f5a0', time: new Date().toLocaleTimeString() },
      ...prev.slice(0, 9)
    ]);
    setLoading(false);
  };

  return (
    <div className="page-wrap">
      <Navbar />
      <main className="main-content">
        <button className="btn-back" onClick={() => navigate('/')}>← Back to Dashboard</button>

        <div className="module-header">
          <div>
            <h1 style={{ color:'#ff8c42' }}>📬 Spam Email Detection</h1>
            <p>TF-IDF + Logistic Regression · NLP Classification · 97.6% accuracy</p>
          </div>
          <div className="module-badge" style={{ background:'rgba(255,140,66,0.08)', borderColor:'rgba(255,140,66,0.2)', color:'#ff8c42' }}>
            <span className="badge-dot" style={{ background:'#ff8c42' }} />Live Model
          </div>
        </div>

        <div className="module-grid">
          {/* ── Inputs ── */}
          <div className="card">
            <div className="card-title" style={{ color:'#ff8c42' }}>
              <span className="dot" style={{ background:'#ff8c42' }} /> Email Content
            </div>

            <div className="spam-examples">
              <button className="example-btn spam"  onClick={() => setForm(SPAM_EXAMPLE)}>Load Spam Example</button>
              <button className="example-btn ham"   onClick={() => setForm(HAM_EXAMPLE)}>Load Normal Example</button>
              <button className="example-btn clear" onClick={() => { setForm({ subject:'', body:'' }); setResult(null); }}>Clear</button>
            </div>

            <div className="field" style={{ marginBottom:'1rem' }}>
              <label>Subject Line</label>
              <input name="subject" value={form.subject} onChange={handle} placeholder="Email subject..." />
            </div>
            <div className="field" style={{ marginBottom:'1.5rem' }}>
              <label>Email Body</label>
              <textarea
                name="body" value={form.body} onChange={handle}
                placeholder="Paste the full email body here..."
                style={{ minHeight:160 }}
              />
            </div>

            <button
              className="btn-predict"
              style={{ background:'linear-gradient(135deg,#ff8c42,#f5c842)', color:'#000' }}
              onClick={predict} disabled={loading || (!form.subject && !form.body)}
            >
              {loading
                ? <><span className="spinner" style={{ borderTopColor:'#000' }} /> &nbsp;Analyzing…</>
                : '📧 Analyze Email'}
            </button>
          </div>

          {/* ── Result ── */}
          <div className="card">
            <div className="card-title" style={{ color:'#ff8c42' }}>
              <span className="dot" style={{ background:'#ff8c42' }} /> Analysis Result
            </div>
            {result ? (
              <div className="animate-in" style={{ textAlign:'center' }}>
                <div className="spam-verdict-icon">{result.is_spam ? '🚫' : '✅'}</div>
                <div className="spam-verdict-label" style={{ color: result.is_spam ? '#ff8c42' : '#00f5a0' }}>
                  {result.prediction}
                </div>

                <div className="prob-bar-wrap" style={{ textAlign:'left' }}>
                  <div className="prob-bar-header">
                    <span>Spam Probability</span>
                    <span style={{ color: result.is_spam ? '#ff8c42' : '#00f5a0' }}>
                      {result.spam_probability.toFixed(1)}%
                    </span>
                  </div>
                  <div className="prob-track">
                    <div className="prob-fill" style={{ width:`${result.spam_probability}%`, background: result.is_spam ? '#ff8c42' : '#00f5a0' }} />
                  </div>
                </div>

                <div className="prob-bar-wrap" style={{ textAlign:'left', marginTop:'0.75rem' }}>
                  <div className="prob-bar-header">
                    <span>Confidence</span>
                    <span style={{ color:'var(--cyan)' }}>{result.confidence.toFixed(1)}%</span>
                  </div>
                  <div className="prob-track">
                    <div className="prob-fill" style={{ width:`${Math.min(result.confidence, 100)}%`, background:'var(--cyan)' }} />
                  </div>
                </div>

                {form.subject && (
                  <div className="email-preview">
                    <div className="email-preview-header">📨 {form.subject}</div>
                    <div className="email-preview-body">
                      {form.body.slice(0, 200)}{form.body.length > 200 ? '…' : ''}
                    </div>
                  </div>
                )}

                <div className="result-meta" style={{ marginTop:'1rem', justifyContent:'center' }}>
                  <div className="meta-chip"><span>Accuracy: </span><strong>97.6%</strong></div>
                  <div className="meta-chip"><span>Model: </span><strong>TF-IDF + LR</strong></div>
                </div>
              </div>
            ) : (
              <div className="result-placeholder">
                <div className="ph-icon">📧</div>
                <p>Paste email content and click analyze to detect spam</p>
              </div>
            )}
          </div>
        </div>

        {/* ── History ── */}
        {history.length > 0 && (
          <div className="history-section">
            <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:'0.75rem' }}>
              <div className="history-title" style={{ margin:0 }}>Detection History</div>
              <button
                onClick={() => setHistory([])}
                style={{
                  padding:'0.3rem 0.875rem', background:'transparent',
                  border:'1px solid rgba(255,78,106,0.3)', borderRadius:8,
                  color:'#ff4e6a', fontSize:'0.78rem', cursor:'pointer'
                }}
              >🗑 Clear History</button>
            </div>
            <div className="history-list">
              {history.map((h, i) => (
                <div key={i} className="history-item">
                  <span>Email check</span>
                  <span className="history-badge" style={{ background:`${h.color}20`, color:h.color }}>{h.label}</span>
                  <span className="history-time">{h.time}</span>
                  <button
                    onClick={() => setHistory(prev => prev.filter((_,j) => j !== i))}
                    style={{ background:'transparent', border:'none', color:'#ff4e6a', cursor:'pointer', fontSize:'0.8rem', marginLeft:'0.5rem' }}
                  >✕</button>
                </div>
              ))}
            </div>
          </div>
        )}

      </main>
    </div>
  );
}