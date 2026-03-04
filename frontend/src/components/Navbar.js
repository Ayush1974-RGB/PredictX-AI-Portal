// components/Navbar.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Navbar.css';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [light, setLight] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const toggleTheme = () => {
    setLight(p => !p);
    document.body.classList.toggle('light-mode');
  };

  return (
    <nav className="nav">
      <div className="nav-brand" onClick={() => navigate('/')} style={{cursor:'pointer'}}>
        <div className="brand-icon">📡</div>
        <span>PredictX</span>
      </div>
      <div className="nav-right">
        <div
          className={`dark-toggle ${light ? 'light' : ''}`}
          onClick={toggleTheme}
          title="Toggle theme"
        />
        {user && (
          <>
            <div className="nav-user">
              <div className="nav-avatar">{user.username?.[0]?.toUpperCase()}</div>
              <span className="nav-username">{user.username}</span>
            </div>
            <button className="btn-logout" onClick={handleLogout}>Logout</button>
          </>
        )}
      </div>
    </nav>
  );
}
