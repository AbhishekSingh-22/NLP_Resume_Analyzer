import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, CheckCircle, AlertTriangle, Lightbulb, FileText } from 'lucide-react';

const UserPortal = () => {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer?.files[0] || e.target.files[0];
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile);
    } else {
      setError('Please upload a valid PDF file.');
    }
  };

  const handleAnalyze = async () => {
    if (!file || !jd.trim()) {
      setError('Please provide both a PDF resume and a Job Description.');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('resume', file);
    formData.append('job_description', jd);

    try {
      // Allow fallback between ports
      const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8080';
      const response = await axios.post(`${API_URL}/api/user/analyze`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to connect to the analysis engine. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} 
      animate={{ opacity: 1, y: 0 }} 
      className="portal-container"
      style={{ width: '100%', maxWidth: '900px', display: 'flex', flexDirection: 'column', gap: '2rem' }}
    >
      <div className="glass-panel" style={{ padding: '2rem' }}>
        <h2 style={{ marginBottom: '1.5rem', color: 'var(--text-main)' }}>Candidate Analysis</h2>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div 
            className={`dropzone ${file ? 'active' : ''}`}
            onDrop={handleFileDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => document.getElementById('file-upload').click()}
          >
            <input 
              id="file-upload" 
              type="file" 
              accept=".pdf" 
              hidden 
              onChange={handleFileDrop} 
            />
            <UploadCloud size={48} color={file ? 'var(--accent-primary)' : 'var(--text-muted)'} />
            <p style={{ fontWeight: file ? 600 : 400, color: file ? 'var(--accent-primary)' : 'inherit' }}>
              {file ? file.name : "Drag & drop your PDF resume here, or click to select"}
            </p>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Target Job Description</label>
            <textarea 
              className="input-field" 
              placeholder="Paste the requirements and description of the role you are targeting..."
              value={jd}
              onChange={(e) => setJd(e.target.value)}
            />
          </div>

          {error && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ color: 'var(--error)', padding: '1rem', background: 'rgba(239,68,68,0.1)', borderRadius: '8px', border: '1px solid var(--error)' }}>
              {error}
            </motion.div>
          )}

          <button 
            className="btn btn-primary" 
            onClick={handleAnalyze}
            disabled={loading || !file || !jd.trim()}
            style={{ alignSelf: 'flex-start' }}
          >
            {loading ? (
              <><div className="spinner" /> Analyzing Document...</>
            ) : (
              <><FileText size={18} /> Run AI Analysis</>
            )}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {result && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }} 
            animate={{ opacity: 1, height: 'auto' }} 
            exit={{ opacity: 0, height: 0 }}
            className="glass-panel result-panel"
            style={{ padding: '2rem', overflow: 'hidden' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', borderBottom: '1px solid var(--panel-border)', paddingBottom: '1rem' }}>
              <div>
                <h3 style={{ fontSize: '1.5rem', color: 'var(--accent-primary)' }}>{result.candidate_name}</h3>
                <p style={{ color: 'var(--text-muted)', marginTop: '0.25rem' }}>{result.feedback?.summary}</p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '2.5rem', fontWeight: 800, color: result.fit_score >= 75 ? 'var(--success)' : result.fit_score >= 50 ? 'var(--accent-teal)' : 'var(--error)' }}>
                  {result.fit_score}%
                </div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Fit Score</div>
              </div>
            </div>

            {/* Matched / Missing Skills */}
            {(result.jd_match?.matched?.length > 0 || result.jd_match?.missing?.length > 0) && (
              <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '1.5rem', marginBottom: '1.5rem' }}>
                <div style={{ background: 'rgba(20,184,166,0.05)', border: '1px solid rgba(20,184,166,0.2)', padding: '1.25rem', borderRadius: '12px' }}>
                  <h4 style={{ color: '#14b8a6', marginBottom: '0.75rem', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px' }}>✓ Matched JD Skills ({result.jd_match?.matched?.length || 0})</h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {result.jd_match?.matched?.map((s, i) => (
                      <span key={i} style={{ background: 'rgba(20,184,166,0.15)', color: '#14b8a6', padding: '0.25rem 0.75rem', borderRadius: '999px', fontSize: '0.85rem', fontWeight: 500 }}>{s}</span>
                    ))}
                  </div>
                </div>
                <div style={{ background: 'rgba(251,146,60,0.05)', border: '1px solid rgba(251,146,60,0.2)', padding: '1.25rem', borderRadius: '12px' }}>
                  <h4 style={{ color: '#fb923c', marginBottom: '0.75rem', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px' }}>✗ Missing JD Skills ({result.jd_match?.missing?.length || 0})</h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {result.jd_match?.missing?.map((s, i) => (
                      <span key={i} style={{ background: 'rgba(251,146,60,0.15)', color: '#fb923c', padding: '0.25rem 0.75rem', borderRadius: '999px', fontSize: '0.85rem', fontWeight: 500 }}>{s}</span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* AI Feedback Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '1.5rem' }}>
              
              <div style={{ background: 'rgba(34,197,94,0.05)', border: '1px solid rgba(34,197,94,0.2)', padding: '1.5rem', borderRadius: '12px' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#22c55e', marginBottom: '1rem' }}>
                  <CheckCircle size={20} /> Key Strengths
                </h4>
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {result.feedback?.strengths?.map((s, i) => (
                    <li key={i} style={{ display: 'flex', alignItems: 'start', gap: '0.5rem' }}>
                      <span style={{ color: '#22c55e', marginTop: '2px' }}>•</span>
                      <span style={{ lineHeight: 1.5, color: 'var(--text-main)' }}>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div style={{ background: 'rgba(239,68,68,0.05)', border: '1px solid rgba(239,68,68,0.2)', padding: '1.5rem', borderRadius: '12px' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#ef4444', marginBottom: '1rem' }}>
                  <AlertTriangle size={20} /> Identified Gaps
                </h4>
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {result.feedback?.gaps?.map((s, i) => (
                    <li key={i} style={{ display: 'flex', alignItems: 'start', gap: '0.5rem' }}>
                      <span style={{ color: '#ef4444', marginTop: '2px' }}>•</span>
                      <span style={{ lineHeight: 1.5, color: 'var(--text-main)' }}>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>

            </div>

            {/* Suggestions */ }
            <div style={{ background: 'rgba(59,130,246,0.05)', border: '1px solid rgba(59,130,246,0.2)', padding: '1.5rem', borderRadius: '12px', marginTop: '1.5rem' }}>
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#3b82f6', marginBottom: '1rem' }}>
                  <Lightbulb size={20} /> Actionable Suggestions
                </h4>
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {result.feedback?.suggestions?.map((s, i) => (
                    <li key={i} style={{ display: 'flex', alignItems: 'start', gap: '0.5rem' }}>
                      <span style={{ color: '#3b82f6', marginTop: '2px' }}>→</span>
                      <span style={{ lineHeight: 1.5, color: 'var(--text-main)' }}>{s}</span>
                    </li>
                  ))}
                </ul>
            </div>

          </motion.div>
        )}
      </AnimatePresence>

    </motion.div>
  );
};

export default UserPortal;
