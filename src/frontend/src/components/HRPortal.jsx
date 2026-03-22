import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, Users, ChevronDown, ChevronUp, Star, FileArchive } from 'lucide-react';

const HRPortal = () => {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState('');
  const [loading, setLoading] = useState(false);
  const [leaderboard, setLeaderboard] = useState([]);
  const [error, setError] = useState(null);
  const [expandedId, setExpandedId] = useState(null);

  const handleFileDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer?.files[0] || e.target.files[0];
    if (droppedFile && (droppedFile.type === 'application/zip' || droppedFile.name.endsWith('.zip'))) {
      setFile(droppedFile);
    } else {
      setError('Please upload a valid ZIP file containing PDF resumes.');
    }
  };

  const handleAnalyze = async () => {
    if (!file || !jd.trim()) {
      setError('Please provide both a ZIP file and a Job Description.');
      return;
    }
    setLoading(true);
    setError(null);
    setLeaderboard([]);

    const formData = new FormData();
    formData.append('zip_file', file);
    formData.append('job_description', jd);

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8080';
      const response = await axios.post(`${API_URL}/api/hr/bulk-analyze`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setLeaderboard(response.data.leaderboard || []);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to connect to the bulk analysis engine.');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (filename) => {
    if (expandedId === filename) setExpandedId(null);
    else setExpandedId(filename);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} 
      animate={{ opacity: 1, y: 0 }} 
      className="portal-container"
      style={{ width: '100%', maxWidth: '1000px', display: 'flex', flexDirection: 'column', gap: '2rem' }}
    >
      <div className="glass-panel" style={{ padding: '2rem' }}>
        <h2 style={{ marginBottom: '1.5rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Users size={24} /> Bulk Candidate Filtering
        </h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '1.5rem' }}>
          <div 
            className={`dropzone ${file ? 'active' : ''}`}
            onDrop={handleFileDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => document.getElementById('zip-upload').click()}
            style={{ height: '100%', justifyContent: 'center' }}
          >
            <input 
              id="zip-upload" 
              type="file" 
              accept=".zip" 
              hidden 
              onChange={handleFileDrop} 
            />
            <FileArchive size={48} color={file ? 'var(--accent-primary)' : 'var(--text-muted)'} />
            <p style={{ fontWeight: file ? 600 : 400, color: file ? 'var(--accent-primary)' : 'inherit' }}>
              {file ? file.name : "Drop ZIP of resumes here"}
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <textarea 
              className="input-field" 
              style={{ flex: 1, height: '100%' }}
              placeholder="Paste the Job Description to rank candidates against..."
              value={jd}
              onChange={(e) => setJd(e.target.value)}
            />
          </div>
        </div>

        {error && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ color: 'var(--error)', padding: '1rem', background: 'rgba(239,68,68,0.1)', borderRadius: '8px', border: '1px solid var(--error)', marginTop: '1.5rem' }}>
            {error}
          </motion.div>
        )}

        <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'flex-end' }}>
          <button 
            className="btn btn-primary" 
            onClick={handleAnalyze}
            disabled={loading || !file || !jd.trim()}
          >
            {loading ? (
              <><div className="spinner" /> Processing Batch...</>
            ) : (
              <><Star size={18} /> Rank Candidates</>
            )}
          </button>
        </div>
      </div>

      {leaderboard.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <h3 style={{ color: 'var(--text-main)', marginBottom: '0.5rem' }}>Leaderboard ({leaderboard.length} candidates)</h3>
          
          {leaderboard.map((candidate, index) => (
            <motion.div 
              key={candidate.filename}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass-panel"
              style={{ overflow: 'hidden' }}
            >
              <div 
                onClick={() => toggleExpand(candidate.filename)}
                style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', background: expandedId === candidate.filename ? 'rgba(255,255,255,0.02)' : 'transparent' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                  <div style={{ background: index === 0 ? 'rgba(250, 204, 21, 0.2)' : 'rgba(59, 130, 246, 0.1)', color: index === 0 ? '#facc15' : 'var(--accent-primary)', width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                    #{index + 1}
                  </div>
                  <div>
                    <h4 style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>{candidate.candidate_name}</h4>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{candidate.feedback?.roles?.[0] || 'Unknown Role'}</p>
                  </div>
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ fontSize: '1.5rem', fontWeight: 700, color: candidate.fit_score >= 75 ? 'var(--success)' : candidate.fit_score >= 50 ? 'var(--accent-teal)' : 'var(--text-main)' }}>
                      {candidate.fit_score}%
                    </span>
                  </div>
                  {expandedId === candidate.filename ? <ChevronUp color="var(--text-muted)"/> : <ChevronDown color="var(--text-muted)"/>}
                </div>
              </div>

              <AnimatePresence>
                {expandedId === candidate.filename && (
                  <motion.div 
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    style={{ borderTop: '1px solid var(--panel-border)', padding: '1.5rem', background: 'rgba(0,0,0,0.2)' }}
                  >
                    <p style={{ color: 'var(--text-main)', marginBottom: '1.5rem', lineHeight: 1.6 }}>{candidate.feedback?.summary}</p>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '1.5rem' }}>
                      <div>
                        <h5 style={{ color: '#22c55e', marginBottom: '0.75rem' }}>Strengths</h5>
                        <ul style={{ paddingLeft: '1.25rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                          {candidate.feedback?.strengths?.map((s, i) => <li key={i}>{s}</li>)}
                        </ul>
                      </div>
                      <div>
                        <h5 style={{ color: '#ef4444', marginBottom: '0.75rem' }}>Gaps</h5>
                        <ul style={{ paddingLeft: '1.25rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                          {candidate.feedback?.gaps?.map((s, i) => <li key={i}>{s}</li>)}
                        </ul>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
};

export default HRPortal;
