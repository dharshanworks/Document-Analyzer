import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, clearAuthToken, getAuthHeaders } from '../api';
import { useToast } from './Toast';

const FILE_LIMIT = 10 * 1024 * 1024;
const ALLOWED_TYPES = ['pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png'];

function Analyze() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(() => {
    try {
      const saved = localStorage.getItem('lastAnalysisResult');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [copiedState, setCopiedState] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const { addToast } = useToast();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (analysisResult) {
      localStorage.setItem('lastAnalysisResult', JSON.stringify(analysisResult));
    } else {
      localStorage.removeItem('lastAnalysisResult');
    }
  }, [analysisResult]);

  const resetUpload = () => {
    setSelectedFile(null);
    setAnalysisResult(null);
    setError('');
    setActiveTab('overview');
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUnauthorized = useCallback(() => {
    clearAuthToken();
    navigate('/login', { replace: true });
  }, [navigate]);

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFileTypeLabel = (filename) => {
    const ext = filename.split('.').pop()?.toUpperCase() || '';
    return ext;
  };

  const handleFile = useCallback((file) => {
    if (!file) return;

    const extension = file.name.includes('.')
      ? file.name.split('.').pop().toLowerCase()
      : '';

    if (!ALLOWED_TYPES.includes(extension)) {
      setError('Supported formats: PDF, DOCX, TXT, JPG, PNG.');
      addToast('Unsupported file format.', 'error');
      return;
    }

    if (file.size > FILE_LIMIT) {
      setError('File size must be 10MB or smaller.');
      addToast('File too large. Maximum size is 10MB.', 'error');
      return;
    }

    setSelectedFile(file);
    setError('');
    addToast(`"${file.name}" selected.`, 'info');
  }, [addToast]);

  const onDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragActive(false);
    if (event.dataTransfer.files?.[0]) {
      handleFile(event.dataTransfer.files[0]);
    }
  };

  const onDrag = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragActive(event.type === 'dragenter' || event.type === 'dragover');
  };

  const simulateProgress = () => {
    setUploadProgress(0);
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) {
          clearInterval(interval);
          return 90;
        }
        return prev + Math.random() * 15;
      });
    }, 200);
    return interval;
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Choose a file before starting analysis.');
      return;
    }

    setLoading(true);
    setError('');
    const progressInterval = simulateProgress();

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await api.post('/upload', formData, {
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'multipart/form-data',
        },
      });

      clearInterval(progressInterval);
      setUploadProgress(100);
      setAnalysisResult(response.data);
      setActiveTab('overview');
      addToast('Analysis complete!', 'success');

      const savedReports = JSON.parse(localStorage.getItem('analysisReports') || '[]');
      savedReports.unshift({
        id: Date.now(),
        filename: response.data.filename || selectedFile.name,
        timestamp: response.data.timestamp || new Date().toISOString(),
        analysis: response.data.analysis,
        report: response.data.report,
        textPreview: response.data.text_preview || '',
        metadata: response.data.metadata || {},
      });
      if (savedReports.length > 50) savedReports.length = 50;
      localStorage.setItem('analysisReports', JSON.stringify(savedReports));
    } catch (uploadError) {
      clearInterval(progressInterval);
      setUploadProgress(0);
      if (uploadError.response?.status === 401) {
        handleUnauthorized();
        return;
      }
      const msg = uploadError.response?.data?.error || 'Unable to analyze file right now.';
      setError(msg);
      addToast(msg, 'error');
    } finally {
      setLoading(false);
    }
  };

  const exportReport = () => {
    if (!analysisResult?.report) {
      addToast('No report available for export.', 'warning');
      return;
    }

    const blob = new Blob([analysisResult.report], { type: 'text/plain' });
    const fileUrl = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = fileUrl;
    const safeName = (analysisResult.filename || 'analysis').toString().replace(/[^a-z0-9\-_]+/gi, '_');
    anchor.download = `analysis_${safeName}_${Date.now()}.txt`;
    anchor.click();
    URL.revokeObjectURL(fileUrl);
    addToast('Report exported successfully.', 'success');
  };

  const exportJsonReport = () => {
    if (!analysisResult) {
      addToast('No analysis data available for export.', 'warning');
      return;
    }

    const blob = new Blob([JSON.stringify(analysisResult, null, 2)], { type: 'application/json' });
    const fileUrl = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = fileUrl;
    const safeName = (analysisResult.filename || 'analysis').toString().replace(/[^a-z0-9\-_]+/gi, '_');
    anchor.download = `analysis_${safeName}_${Date.now()}.json`;
    anchor.click();
    URL.revokeObjectURL(fileUrl);
    addToast('JSON report exported successfully.', 'success');
  };

  const copyText = useCallback((value, key) => {
    navigator.clipboard.writeText(value).then(() => {
      setCopiedState(key);
      addToast('Copied to clipboard!', 'success');
      setTimeout(() => setCopiedState(''), 1800);
    });
  }, [addToast]);

  const analysis = analysisResult?.analysis || {};
  const entities = analysis.entities || {};
  const summary = analysis.summary || '';
  const detailedSummary = analysis.detailed_summary || summary;
  const statistics = analysis.statistics || {};
  const readability = analysis.readability || {};
  const keywords = analysis.keywords || [];
  const keyPhrases = analysis.key_phrases || [];
  const deep = analysis.deep_analysis || {};
  const sentimentData = analysis.sentiment_detail || analysis.sentiment || {};
  const sentimentLabel = typeof sentimentData === 'string' ? sentimentData : (sentimentData.classification || 'Neutral');
  const topics = analysis.topics || [];
  const themes = analysis.themes || {};
  const style = analysis.style || {};
  const structure = analysis.structure || {};
  const tone = analysis.tone || {};
  const contentQuality = analysis.content_quality || {};
  const audienceFit = analysis.audience_fit || {};
  const metadata = analysis.metadata || analysisResult?.metadata || {};

  const tabs = useMemo(
    () => [
      { id: 'overview', label: 'Overview' },
      { id: 'quality', label: 'Quality' },
      { id: 'deep', label: 'Deep Analysis' },
      { id: 'topics', label: 'Topics' },
      { id: 'entities', label: 'Entities' },
      { id: 'summary', label: 'Summary' },
      { id: 'signals', label: 'Signals' },
      { id: 'report', label: 'Report' },
    ],
    []
  );

  const sentimentColor = (sentiment) => {
    const s = (sentiment || '').toLowerCase();
    if (s.includes('positive')) return 'var(--success)';
    if (s.includes('negative')) return 'var(--danger)';
    return 'var(--text-muted)';
  };

  const qualityGradeColor = (grade) => {
    const colors = { A: 'var(--success)', B: '#22c55e', C: '#eab308', D: '#f97316', F: 'var(--danger)' };
    return colors[grade] || 'var(--text-muted)';
  };

  if (!analysisResult) {
    return (
      <section className="da-page da-fade-in">
        <header className="da-page-header">
          <div>
            <p className="da-overline">Document Lab</p>
            <h1>Analyze a document</h1>
            <p className="da-muted">
              Upload PDF, DOCX, TXT, JPG, or PNG and get statistics, sentiment, readability, entity extraction, and summary insights.
            </p>
          </div>
        </header>

        <div className="da-upload-hero da-slide-up">
          <div
            className={`da-dropzone ${dragActive ? 'is-active' : ''}`}
            onDragEnter={onDrag}
            onDragLeave={onDrag}
            onDragOver={onDrag}
            onDrop={onDrop}
          >
            <div className="da-dropzone-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            <p className="da-dropzone-title">Drop your file here</p>
            <p className="da-muted">or browse from local storage</p>

            <label className="da-button da-button-secondary da-upload-label">
              Select file
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt,.jpg,.jpeg,.png"
                onChange={(event) => handleFile(event.target.files?.[0])}
                hidden
              />
            </label>

            <p className="da-muted da-upload-hint">Accepted formats: PDF, DOCX, TXT, JPG, PNG | Max file size: 10MB</p>

            {selectedFile && (
              <div className="da-file-pill da-fade-in">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
                <span>{selectedFile.name}</span>
                <span className="da-file-size">{formatFileSize(selectedFile.size)}</span>
                <button type="button" onClick={() => { setSelectedFile(null); setUploadProgress(0); }} className="da-mini-action">
                  Remove
                </button>
              </div>
            )}
          </div>

          {loading && (
            <div className="da-progress-bar-container">
              <div className="da-progress-bar">
                <div className="da-progress-bar-fill" style={{ width: `${uploadProgress}%` }} />
              </div>
              <p className="da-muted" style={{ fontSize: '0.82rem', marginTop: '0.3rem' }}>
                Analyzing... {Math.round(uploadProgress)}%
              </p>
            </div>
          )}

          {error && <p className="da-alert da-alert-error">{error}</p>}

          <button
            type="button"
            className="da-button"
            disabled={loading || !selectedFile}
            onClick={handleUpload}
          >
            {loading ? (
              <>
                <span className="da-spinner" />
                Analyzing...
              </>
            ) : 'Run analysis'}
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="da-page da-fade-in">
      <header className="da-page-header da-page-header-row">
        <div>
          <p className="da-overline">Analysis Result</p>
          <h1>{analysisResult.filename || 'Analysis'}</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginTop: '0.3rem', flexWrap: 'wrap' }}>
            <span className="da-file-type-badge">{getFileTypeLabel(analysisResult.filename)}</span>
            {metadata.page_count && <span className="da-file-type-badge" style={{ background: 'rgba(34,197,94,0.1)', color: '#22c55e', borderColor: 'rgba(34,197,94,0.2)' }}>{metadata.page_count} pages</span>}
            {metadata.author && <span className="da-file-type-badge" style={{ background: 'rgba(59,130,246,0.1)', color: '#3b82f6', borderColor: 'rgba(59,130,246,0.2)' }}>{metadata.author}</span>}
            <p className="da-muted" style={{ fontSize: '0.82rem' }}>Deep document intelligence with enriched retrieval, readability, and action-oriented insights.</p>
          </div>
        </div>

        <div className="da-row-actions">
          <button type="button" className="da-button da-button-secondary" onClick={exportReport}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            TXT report
          </button>
          <button type="button" className="da-button da-button-secondary" onClick={exportJsonReport}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="16 18 22 12 16 6" />
              <polyline points="8 6 2 12 8 18" />
            </svg>
            JSON
          </button>
          <button type="button" className="da-button da-button-ghost" onClick={resetUpload}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            New analysis
          </button>
        </div>
      </header>

      <div className="da-stats-grid da-stats-grid-wide da-slide-up">
        <article className="da-card da-stat-card" style={{ animationDelay: '0ms' }}>
          <p className="da-card-kicker">Content Quality</p>
          <p className="da-stat-value" style={{ color: qualityGradeColor(contentQuality.grade) }}>
            {contentQuality.grade || 'N/A'}
          </p>
          <p className="da-muted" style={{ fontSize: '0.8rem', marginTop: '0.2rem' }}>
            {contentQuality.overall_score || 0}/{contentQuality.max_score || 100}
          </p>
        </article>
        <article className="da-card da-stat-card" style={{ animationDelay: '50ms' }}>
          <p className="da-card-kicker">Sentiment</p>
          <p className="da-stat-value" style={{ color: sentimentColor(sentimentLabel) }}>{sentimentLabel}</p>
          {typeof sentimentData === 'object' && sentimentData.polarity !== undefined && (
            <p className="da-muted" style={{ fontSize: '0.8rem', marginTop: '0.2rem' }}>
              Polarity: {sentimentData.polarity}
            </p>
          )}
        </article>
        <article className="da-card da-stat-card" style={{ animationDelay: '100ms' }}>
          <p className="da-card-kicker">Entities</p>
          <p className="da-stat-value">{(entities.names?.length || 0) + (entities.dates?.length || 0) + (entities.organizations?.length || 0) + (entities.amounts?.length || 0)}</p>
          <p className="da-muted" style={{ fontSize: '0.8rem', marginTop: '0.2rem' }}>
            {topics.length} topics, {Object.keys(themes).length} themes
          </p>
        </article>
        <article className="da-card da-stat-card" style={{ animationDelay: '150ms' }}>
          <p className="da-card-kicker">Word Count</p>
          <p className="da-stat-value">{Number(statistics.word_count || 0).toLocaleString()}</p>
          <p className="da-muted" style={{ fontSize: '0.8rem', marginTop: '0.2rem' }}>
            {readability.reading_level || ''}
          </p>
        </article>
      </div>

      <div className="da-tabs" role="tablist" aria-label="Analysis tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`da-tab ${activeTab === tab.id ? 'is-active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <article className="da-card da-tab-panel da-fade-in">
        {activeTab === 'overview' && (
          <div className="da-stack-large">
            <div className="da-deep-grid">
              <div className="da-deep-card">
                <p className="da-card-kicker">Document Type</p>
                <h3>{(deep.document_type?.primary || deep.document_type_guess || 'general').charAt(0).toUpperCase() + (deep.document_type?.primary || deep.document_type_guess || 'general').slice(1)}</h3>
                {deep.document_type?.secondary && (
                  <p className="da-muted">Secondary: {deep.document_type.secondary.charAt(0).toUpperCase() + deep.document_type.secondary.slice(1)}</p>
                )}
                <p className="da-muted">Confidence: {(deep.confidence || 'medium').charAt(0).toUpperCase() + (deep.confidence || 'medium').slice(1)}</p>
              </div>
              <div className="da-deep-card">
                <p className="da-card-kicker">Writing Style</p>
                <h3>{style.writing_style || 'N/A'}</h3>
                <p className="da-muted">Passive: {style.passive_voice_instances || 0} | Transitions: {style.transition_words || 0}</p>
              </div>
              <div className="da-deep-card">
                <p className="da-card-kicker">Structure</p>
                <h3>{structure.structure_score || 'N/A'}</h3>
                <p className="da-muted">{structure.headings?.length || 0} headings, {structure.lists_detected || 0} lists, {structure.tables_detected || 0} tables</p>
              </div>
              <div className="da-deep-card">
                <p className="da-card-kicker">Reading estimate</p>
                {(() => {
                  const wc = statistics.word_count || 0;
                  const minutes = Math.ceil(wc / 200);
                  const barPct = Math.min(100, (wc / 5000) * 100);
                  return (
                    <>
                      <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginTop: '0.5rem' }}>
                        <span style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text)' }}>
                          {minutes < 1 ? '< 1' : minutes} min
                        </span>
                        <span className="da-muted" style={{ fontSize: '0.82rem' }}>
                          @ 200 wpm
                        </span>
                      </div>
                      <div className="da-reading-bar-track" style={{ marginTop: '0.6rem' }}>
                        <div className="da-reading-bar-fill" style={{ width: `${barPct}%` }} />
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                        <span>Short</span>
                        <span>Medium</span>
                        <span>Long</span>
                      </div>
                    </>
                  );
                })()}
              </div>
            </div>
            <div>
              <h3>Tone Profile</h3>
              <div className="da-tone-grid">
                {Object.entries(tone).map(([key, value]) => (
                  <div key={key} className="da-tone-item">
                    <span className="da-tone-label">{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                    <div className="da-tone-bar-track">
                      <div className="da-tone-bar-fill" style={{ width: `${value * 100}%`, background: value > 0.3 ? 'var(--primary)' : 'var(--line)' }} />
                    </div>
                    <span className="da-tone-value">{Math.round(value * 100)}%</span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h3>Executive Summary</h3>
              <p className="da-summary-text">{summary || 'Summary not available.'}</p>
            </div>
          </div>
        )}

        {activeTab === 'quality' && (
          <div className="da-stack-large">
            <div className="da-quality-header">
              <div className="da-quality-grade" style={{ color: qualityGradeColor(contentQuality.grade) }}>
                <span className="da-quality-grade-letter">{contentQuality.grade || 'N/A'}</span>
                <span className="da-quality-grade-score">{contentQuality.overall_score || 0} / {contentQuality.max_score || 100}</span>
              </div>
              <div>
                <h3>Content Quality Breakdown</h3>
              </div>
            </div>
            <div className="da-quality-breakdown">
              {Object.entries(contentQuality.breakdown || {}).map(([key, value]) => (
                <div key={key} className="da-quality-item">
                  <span className="da-quality-item-label">{key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span>
                  <span className={`da-quality-item-value da-quality-${value.toLowerCase().replace(/[^a-z]/g, '')}`}>{value}</span>
                </div>
              ))}
            </div>
            <div className="da-deep-grid">
              <div className="da-deep-card">
                <h3>Audience Fit</h3>
                <p className="da-muted" style={{ marginBottom: '0.5rem' }}>Recommended for:</p>
                <div className="da-token-grid">
                  {(audienceFit.recommended_audiences || []).map((a) => (
                    <span key={a} className="da-token">{a}</span>
                  ))}
                </div>
                <p style={{ marginTop: '0.8rem' }}>Reading Level: {audienceFit.reading_level || 'N/A'}</p>
                <p>Grade Level: {audienceFit.grade_level ?? 'N/A'}</p>
                <p>Writing Style: {audienceFit.writing_style || style.writing_style || 'N/A'}</p>
              </div>
              <div className="da-deep-card">
                <h3>Document Structure</h3>
                <p>Structure: <strong>{structure.structure_score || 'N/A'}</strong></p>
                <p>Headings: {structure.headings?.length || 0}</p>
                <p>Lists: {structure.lists_detected || 0} items</p>
                <p>Tables: {structure.tables_detected || 0}</p>
                <p>Sections: {structure.section_count || 0}</p>
                <p>Has Introduction: {structure.has_abstract_or_intro ? 'Yes' : 'No'}</p>
                <p>Has Conclusion: {structure.has_conclusion ? 'Yes' : 'No'}</p>
                <p>Has References: {structure.has_references ? 'Yes' : 'No'}</p>
              </div>
            </div>
            <div className="da-deep-grid">
              <div className="da-deep-card">
                <h3>Readability Metrics</h3>
                <p>Flesch Reading Ease: <strong>{readability.flesch_reading_ease ?? 'N/A'}</strong></p>
                <p>Flesch-Kincaid Grade: {readability.flesch_kincaid_grade ?? 'N/A'}</p>
                <p>Gunning Fog: {readability.gunning_fog ?? 'N/A'}</p>
                <p>SMOG Index: {readability.smog_index ?? 'N/A'}</p>
                <p>Reading Level: {readability.reading_level || 'N/A'}</p>
                <p>Complex Words: {readability.complex_words || 0} ({readability.complex_word_percentage || 0}%)</p>
              </div>
              <div className="da-deep-card">
                <h3>Writing Style Details</h3>
                <p>Avg Word Length: {style.avg_word_length || 0}</p>
                <p>Avg Sentence Length: {style.avg_sentence_length || 0}</p>
                <p>Passive Voice: {style.passive_voice_instances || 0} instances</p>
                <p>Transition Words: {style.transition_words || 0}</p>
                <p>Questions: {style.questions || 0}</p>
                <p>Exclamations: {style.exclamations || 0}</p>
                <p>Quotes: {style.quotes || 0}</p>
                <p>Vocabulary Richness: {style.vocabulary_richness || statistics.vocabulary_richness || 0}%</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'deep' && (
          <div className="da-stack-large">
            <div>
              <h3>Detailed Summary</h3>
              <p className="da-summary-text">{detailedSummary || 'Detailed summary not available.'}</p>
            </div>
            <div className="da-deep-grid">
              <div className="da-deep-card">
                <h3>Key Findings</h3>
                <ul className="da-bullet-list">
                  {(deep.key_findings || []).map((item, idx) => <li key={`${item}-${idx}`}>{item}</li>)}
                </ul>
              </div>
              <div className="da-deep-card">
                <h3>Risk Flags</h3>
                <ul className="da-bullet-list">
                  {(deep.risk_flags || []).map((item, idx) => <li key={`${item}-${idx}`}>{item}</li>)}
                </ul>
              </div>
              <div className="da-deep-card">
                <h3>Recommended Actions</h3>
                <ul className="da-bullet-list">
                  {(deep.recommended_actions || []).map((item, idx) => <li key={`${item}-${idx}`}>{item}</li>)}
                </ul>
              </div>
              <div className="da-deep-card">
                <h3>Recommendations</h3>
                <ul className="da-bullet-list">
                  {(deep.recommendations || []).map((item, idx) => <li key={`${item}-${idx}`}>{item}</li>)}
                </ul>
              </div>
            </div>
            <div className="da-deep-grid">
              <div className="da-deep-card">
                <h3>Timeline</h3>
                <div className="da-token-grid">
                  {(deep.timeline || []).map((item) => <span key={item} className="da-token">{item}</span>)}
                </div>
              </div>
              <div className="da-deep-card">
                <h3>Primary Entities</h3>
                {deep.primary_entities && (
                  <div>
                    {deep.primary_entities.people?.length > 0 && <p><strong>People:</strong> {deep.primary_entities.people.join(', ')}</p>}
                    {deep.primary_entities.organizations?.length > 0 && <p><strong>Organizations:</strong> {deep.primary_entities.organizations.join(', ')}</p>}
                    {deep.primary_entities.amounts?.length > 0 && <p><strong>Amounts:</strong> {deep.primary_entities.amounts.join(', ')}</p>}
                    {deep.primary_entities.emails?.length > 0 && <p><strong>Emails:</strong> {deep.primary_entities.emails.join(', ')}</p>}
                    {deep.primary_entities.phones?.length > 0 && <p><strong>Phones:</strong> {deep.primary_entities.phones.join(', ')}</p>}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'topics' && (
          <div className="da-stack-large">
            <div>
              <h3>Topics</h3>
              {topics.length === 0 ? (
                <p className="da-muted">No topics detected.</p>
              ) : (
                <div className="da-topics-grid">
                  {topics.map((topic, idx) => (
                    <div key={topic.topic} className="da-topic-card" style={{ animationDelay: `${idx * 80}ms` }}>
                      <h4>{topic.topic}</h4>
                      <p className="da-topic-score">Score: {topic.score}</p>
                      {topic.related_terms && topic.related_terms.length > 0 && (
                        <div className="da-token-grid" style={{ marginTop: '0.5rem' }}>
                          {topic.related_terms.map((t) => (
                            <span key={t} className="da-token" style={{ fontSize: '0.72rem' }}>{t}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div>
              <h3>Thematic Categories</h3>
              {Object.keys(themes).length === 0 ? (
                <p className="da-muted">No themes detected.</p>
              ) : (
                <div className="da-themes-grid">
                  {Object.entries(themes).map(([theme, keywords_list]) => (
                    <div key={theme} className="da-theme-card">
                      <h4>{theme.charAt(0).toUpperCase() + theme.slice(1)}</h4>
                      <div className="da-token-grid">
                        {keywords_list.map((kw) => (
                          <span key={kw} className="da-token">{kw}</span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div>
              <h3>Keywords</h3>
              <div className="da-token-grid">
                {keywords.length === 0 ? <p className="da-muted">No keywords extracted.</p> : keywords.map((kw) => <span key={kw} className="da-token">{kw}</span>)}
              </div>
            </div>
            <div>
              <h3>Key Phrases</h3>
              <div className="da-token-grid">
                {keyPhrases.length === 0 ? <p className="da-muted">No key phrases extracted.</p> : keyPhrases.map((phrase) => <span key={phrase} className="da-token">{phrase}</span>)}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'entities' && (
          <div className="da-stack-large">
            <div>
              <h3>Names</h3>
              {(entities.names || []).length === 0 ? (
                <p className="da-muted">No names detected.</p>
              ) : (
                <div className="da-token-grid">
                  {entities.names.map((name) => (
                    <span key={name} className="da-token da-token-copy" onClick={() => copyText(name, `name-${name}`)} title="Click to copy">
                      {name}
                      {copiedState === `name-${name}` ? (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      ) : (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                        </svg>
                      )}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div>
              <h3>Dates</h3>
              {(entities.dates || []).length === 0 ? (
                <p className="da-muted">No dates detected.</p>
              ) : (
                <div className="da-token-grid">
                  {entities.dates.map((date) => (
                    <span key={date} className="da-token da-token-copy" onClick={() => copyText(date, `date-${date}`)} title="Click to copy">
                      {date}
                      {copiedState === `date-${date}` ? (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      ) : (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                        </svg>
                      )}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div>
              <h3>Organizations</h3>
              {(entities.organizations || []).length === 0 ? (
                <p className="da-muted">No organizations detected.</p>
              ) : (
                <div className="da-token-grid">
                  {entities.organizations.map((org) => (
                    <span key={org} className="da-token da-token-copy" onClick={() => copyText(org, `org-${org}`)} title="Click to copy">
                      {org}
                      {copiedState === `org-${org}` ? (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      ) : (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                        </svg>
                      )}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div>
              <h3>Amounts</h3>
              {(entities.amounts || []).length === 0 ? (
                <p className="da-muted">No monetary amounts detected.</p>
              ) : (
                <div className="da-token-grid">
                  {entities.amounts.map((amount) => (
                    <span key={amount} className="da-token da-token-copy" onClick={() => copyText(amount, `amount-${amount}`)} title="Click to copy">
                      {amount}
                      {copiedState === `amount-${amount}` ? (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      ) : (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                        </svg>
                      )}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {entities.emails && entities.emails.length > 0 && (
              <div>
                <h3>Email Addresses</h3>
                <div className="da-token-grid">
                  {entities.emails.map((email) => (
                    <span key={email} className="da-token da-token-copy" onClick={() => copyText(email, `email-${email}`)} title="Click to copy">
                      {email}
                      {copiedState === `email-${email}` ? (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      ) : (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                        </svg>
                      )}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {entities.phones && entities.phones.length > 0 && (
              <div>
                <h3>Phone Numbers</h3>
                <div className="da-token-grid">
                  {entities.phones.map((phone) => (
                    <span key={phone} className="da-token da-token-copy" onClick={() => copyText(phone, `phone-${phone}`)} title="Click to copy">
                      {phone}
                      {copiedState === `phone-${phone}` ? (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      ) : (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                        </svg>
                      )}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {entities.urls && entities.urls.length > 0 && (
              <div>
                <h3>URLs</h3>
                <div className="da-token-grid">
                  {entities.urls.map((url) => (
                    <span key={url} className="da-token da-token-copy" onClick={() => copyText(url, `url-${url}`)} title="Click to copy" style={{ fontSize: '0.75rem' }}>
                      {url}
                      {copiedState === `url-${url}` ? (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                      ) : (
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                        </svg>
                      )}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'summary' && (
          <div className="da-stack-large">
            {!summary || summary.length === 0 ? (
              <p className="da-muted">Summary could not be generated for this text.</p>
            ) : (
              <>
                <div>
                  <h3>Executive Summary</h3>
                  <p className="da-summary-text">{summary}</p>
                </div>
                <div>
                  <h3>Detailed Summary</h3>
                  <p className="da-summary-text">{detailedSummary}</p>
                </div>
                <button
                  type="button"
                  className="da-button da-button-secondary"
                  onClick={() => copyText(summary, 'summary')}
                >
                  {copiedState === 'summary' ? 'Copied' : 'Copy summary'}
                </button>
              </>
            )}
          </div>
        )}

        {activeTab === 'signals' && (
          <div className="da-stack-large">
            <div className="da-deep-grid">
              <div className="da-deep-card">
                <p className="da-card-kicker">Statistics</p>
                <p>Words: {statistics.word_count || 0}</p>
                <p>Characters: {statistics.character_count || 0}</p>
                <p>Paragraphs: {statistics.paragraph_count || 0}</p>
                <p>Sentences: {statistics.sentence_count || 0}</p>
                <p>Unique words: {statistics.unique_words || 0}</p>
                <p>Vocab richness: {statistics.vocabulary_richness || 0}%</p>
              </div>
              <div className="da-deep-card">
                <p className="da-card-kicker">Readability</p>
                <p>Flesch Reading Ease: {readability.flesch_reading_ease ?? 'N/A'}</p>
                <p>Flesch-Kincaid Grade: {readability.flesch_kincaid_grade ?? 'N/A'}</p>
                <p>Gunning Fog: {readability.gunning_fog ?? 'N/A'}</p>
                <p>SMOG Index: {readability.smog_index ?? 'N/A'}</p>
                <p>Reading Level: {readability.reading_level || 'N/A'}</p>
              </div>
            </div>
            {statistics.word_frequency && statistics.word_frequency.length > 0 && (
              <div>
                <h3>Word frequency</h3>
                <div className="da-bar-chart">
                  <div className="da-bar-chart-bars">
                    {statistics.word_frequency.slice(0, 10).map((word, idx) => {
                      const maxH = 100;
                      const h = maxH - (idx * 8);
                      return (
                        <div key={word} className="da-bar-chart-item" style={{ animationDelay: `${idx * 60}ms` }}>
                          <div className="da-bar-chart-bar" style={{ height: `${Math.max(8, h)}%` }}>
                            <span className="da-bar-chart-value">{idx + 1}</span>
                          </div>
                          <span className="da-bar-chart-label" title={word}>{word}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
            <div>
              <h3>Keywords</h3>
              <div className="da-token-grid">
                {keywords.length === 0 ? <p className="da-muted">No keywords extracted.</p> : keywords.map((kw) => <span key={kw} className="da-token">{kw}</span>)}
              </div>
            </div>
            <div>
              <h3>Key Phrases</h3>
              <div className="da-token-grid">
                {keyPhrases.length === 0 ? <p className="da-muted">No key phrases extracted.</p> : keyPhrases.map((phrase) => <span key={phrase} className="da-token">{phrase}</span>)}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'report' && (
          <div className="da-stack-large">
            <pre className="da-report-block">{analysisResult.report}</pre>
            <div className="da-row-actions">
              <button type="button" className="da-button da-button-secondary" onClick={exportReport}>
                Download report
              </button>
              <button
                type="button"
                className="da-button da-button-ghost"
                onClick={() => copyText(analysisResult.report, 'report')}
              >
                {copiedState === 'report' ? 'Copied' : 'Copy report'}
              </button>
            </div>
          </div>
        )}
      </article>
    </section>
  );
}

export default Analyze;
