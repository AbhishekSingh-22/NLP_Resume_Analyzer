import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { Brain, FileText, Users } from 'lucide-react';
import UserPortal from './components/UserPortal';
import HRPortal from './components/HRPortal';

function App() {
  return (
    <Router>
      <header className="app-header">
        <div className="app-logo">
          <Brain size={28} color="#60a5fa" />
          <span>Resume NLP Analyzer</span>
        </div>
        <nav className="nav-links">
          <NavLink 
            to="/candidate" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <FileText size={18} /> Candidate Portal
            </div>
          </NavLink>
          <NavLink 
            to="/hr" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <Users size={18} /> HR Dashboard
            </div>
          </NavLink>
        </nav>
      </header>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Navigate to="/candidate" />} />
          <Route path="/candidate" element={<UserPortal />} />
          <Route path="/hr" element={<HRPortal />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;
