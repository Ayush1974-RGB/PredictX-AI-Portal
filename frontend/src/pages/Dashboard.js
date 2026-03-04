// pages/Dashboard.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';
import './Dashboard.css';

const MODULES = [
  {
    id: 'gold', icon: '🪙', tag: 'Regression · India',
    title: 'Gold Price Prediction',
    desc:  'Predict gold price in ₹ per 10g using MCX market inputs — USD/INR rate, opening price, volatility and festival season.',
    accuracy: 'R² 99.96%', color: '#f5c842', dim: 'rgba(245,200,66,0.12)'
  },
  {
    id: 'fraud', icon: '💳', tag: 'Binary Classification',
    title: 'Credit Card Fraud Detection',
    desc:  'Detect fraudulent transactions with high precision using behavioral patterns and location analysis.',
    accuracy: '99.8%', color: '#ff4e6a', dim: 'rgba(255,78,106,0.12)'
  },
  {
    id: 'spam', icon: '📬', tag: 'NLP Classification',
    title: 'Spam Email Detection',
    desc:  'Classify emails as spam or legitimate using TF-IDF vectorization and logistic regression.',
    accuracy: '97.6%', color: '#ff8c42', dim: 'rgba(255,140,66,0.12)'
  },
  {
    id: 'rainfall', icon: '🌧️', tag: 'Classification',
    title: 'Rainfall Prediction',
    desc:  'Predict whether it will rain based on atmospheric conditions — humidity, pressure, cloud cover and wind.',
    accuracy: '100%', color: '#4ea8ff', dim: 'rgba(78,168,255,0.12)'
  },
];

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="page-wrap">
      <Navbar />
      <main className="main-content">
        <div className="dashboard-header animate-in">
          <div className="greeting">Welcome back, {user?.username} 👋</div>
          <h1>Predictive Intelligence ⭐</h1>
          <p>Select a module to run real-time machine learning predictions</p>
        </div>

        <div className="modules-grid">
          {MODULES.map(m => (
            <div
              key={m.id}
              className="module-card animate-in"
              style={{ '--card-color': m.color, '--card-dim': m.dim }}
              onClick={() => navigate(`/${m.id}`)}
            >
              <div className="module-icon-wrap">{m.icon}</div>
              <div className="module-tag">{m.tag}</div>
              <h2>{m.title}</h2>
              <p>{m.desc}</p>
              <div className="module-footer">
                <div className="module-accuracy">
                  Accuracy <strong>{m.accuracy}</strong>
                </div>
                <div className="module-arrow">→</div>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
