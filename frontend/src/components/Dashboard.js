import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useToast } from './Toast';
import { useCounter } from '../hooks/useCounter';

function Dashboard() {
  const [selectedReport, setSelectedReport] = useState(null);
  const [reports, setReports] = useState(() =>
    JSON.parse(localStorage.getItem('analysisReports') || '[]')
  );
  const [searchTerm, setSearchTerm] = useState('');
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
  const { addToast } = useToast();

  useEffect(() => {
    const handler = () => {
      setReports(JSON.parse(localStorage.getItem('analysisReports') || '[]'));
    };
    window.addEventListener('da-reports-updated', handler);
    return () => window.removeEventListener('da-reports-updated', handler);
  }, []);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const storedFullName = localStorage.getItem('userFullName') || '';
  const storedName = localStorage.getItem('userName') || '';
  const greetingName = storedFullName || storedName || '';

  const toggleFavorite = (id) => {
    setReports((prev) => {
      const updated = prev.map((r) =>
        r.id === id ? { ...r, favorite: !r.favorite } : r
      );
      localStorage.setItem('analysisReports', JSON.stringify(updated));
      return updated;
    });
  };

  const handleDelete = (id) => {
    const updated = reports.filter((r) => r.id !== id);
    localStorage.setItem('analysisReports', JSON.stringify(updated));
    if (selectedReport?.id === id) setSelectedReport(null);
    window.dispatchEvent(new Event('da-reports-updated'));
    addToast('Report deleted.', 'success');
  };

  const downloadReport = (entry) => {
    if (!entry?.report) return;
    const blob = new Blob([entry.report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const safeName = (entry.filename || 'analysis').toString().replace(/[^a-z0-9\-_]+/gi, '_');
    a.download = `analysis_${safeName}_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    addToast('Report downloaded.', 'success');
  };

  const exportAllReports = () => {
    if (filteredReports.length === 0) {
      addToast('No reports to export.', 'warning');
      return;
    }
    const combined = filteredReports
      .map((r) => `=== ${r.filename} (${new Date(r.timestamp).toLocaleString()}) ===\n\n${r.report || ''}`)
      .join('\n\n---\n\n');
    const blob = new Blob([combined], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `all_analyses_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    addToast(`Exported ${filteredReports.length} reports.`, 'success');
  };

  const getStats = (analysis) => {
    if (analysis?.statistics) return analysis.statistics;
    return {
      word_count: analysis?.word_count || 0,
      character_count: analysis?.character_count || 0,
      sentence_count: analysis?.sentence_count || 0,
    };
  };

  const getReadingTime = (wordCount) => {
    const minutes = Math.ceil(wordCount / 200);
    if (minutes < 1) return '< 1 min';
    if (minutes === 1) return '1 min';
    return `${minutes} min`;
  };

  const filteredReports = useMemo(() => {
    let result = reports;
    if (showFavoritesOnly) {
      result = result.filter((r) => r.favorite);
    }
    if (searchTerm.trim()) {
      const q = searchTerm.trim().toLowerCase();
      result = result.filter(
        (r) =>
          (r.filename || '').toLowerCase().includes(q) ||
          (r.analysis?.sentiment || '').toLowerCase().includes(q)
      );
    }
    return result;
  }, [reports, searchTerm, showFavoritesOnly]);

  const totalWords = reports.reduce((sum, r) => sum + (getStats(r.analysis).word_count || 0), 0);
  const favoriteCount = reports.filter((r) => r.favorite).length;

  const animatedTotalAnalyses = useCounter(reports.length, 800);
  const animatedTotalWords = useCounter(totalWords, 1500);

  const sentimentDistribution = useMemo(() => {
    const counts = { Positive: 0, Neutral: 0, Negative: 0 };
    reports.forEach((r) => {
      const s = (r.analysis?.sentiment || '').toLowerCase();
      if (s.includes('positive')) counts.Positive++;
      else if (s.includes('negative')) counts.Negative++;
      else counts.Neutral++;
    });
    return counts;
  }, [reports]);

  const wordCloudData = useMemo(() => {
    const freq = {};
    reports.forEach((r) => {
      const preview = (r.textPreview || '').toLowerCase();
      const words = preview.split(/\s+/).filter((w) => w.length > 3);
      words.forEach((w) => {
        const clean = w.replace(/[^a-z]/g, '');
        if (clean.length > 3) freq[clean] = (freq[clean] || 0) + 1;
      });
    });
    return Object.entries(freq)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 20);
  }, [reports]);

  const copySummary = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      addToast('Summary copied to clipboard!', 'success');
    });
  };

  return (
    <section className="da-page da-fade-in">
      <header className="da-page-header">
        <div>
          <p className="da-overline">Workspace</p>
          <h1>
            {greetingName ? `${getGreeting()}, ${greetingName}` : 'Dashboard'}
          </h1>
          <p className="da-muted">
            Upload a document to get started with instant analysis.
          </p>
        </div>
        <Link to="/analyze" className="da-button">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          New analysis
        </Link>
      </header>

      {reports.length > 0 && (
        <div className="da-stats-grid">
          <article className="da-card da-stat-card da-stat-card-enhanced da-slide-up" style={{ animationDelay: '0ms' }}>
            <div className="da-stat-card-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
            </div>
            <p className="da-card-kicker">Total analyses</p>
            <p className="da-stat-value">{Number(animatedTotalAnalyses).toLocaleString()}</p>
          </article>

          <article className="da-card da-stat-card da-stat-card-enhanced da-slide-up" style={{ animationDelay: '80ms' }}>
            <div className="da-stat-card-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 7V4h16v3" />
                <path d="M9 20h6" />
                <path d="M12 4v16" />
              </svg>
            </div>
            <p className="da-card-kicker">Words analyzed</p>
            <p className="da-stat-value">{Number(animatedTotalWords).toLocaleString()}</p>
          </article>

          <article className="da-card da-stat-card da-stat-card-enhanced da-slide-up" style={{ animationDelay: '160ms' }}>
            <div className="da-stat-card-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <path d="M8 14s1.5 2 4 2 4-2 4-2" />
                <line x1="9" y1="9" x2="9.01" y2="9" />
                <line x1="15" y1="9" x2="15.01" y2="9" />
              </svg>
            </div>
            <p className="da-card-kicker">Latest sentiment</p>
            <p className="da-stat-value">{reports[0]?.analysis?.sentiment || 'N/A'}</p>
          </article>

          <article className="da-card da-stat-card da-stat-card-enhanced da-slide-up" style={{ animationDelay: '240ms' }}>
            <div className="da-stat-card-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
              </svg>
            </div>
            <p className="da-card-kicker">Favorites</p>
            <p className="da-stat-value">{favoriteCount}</p>
          </article>
        </div>
      )}

      <div className="da-dashboard-columns">
        <article className="da-card da-slide-up">
          <div className="da-card-header">
            <h2>{reports.length > 0 ? 'Recent analyses' : 'Quick start'}</h2>
            {reports.length > 0 && (
              <div className="da-row-actions">
                <button
                  type="button"
                  className={`da-button da-button-small ${showFavoritesOnly ? 'da-button-secondary' : 'da-button-ghost'}`}
                  onClick={() => setShowFavoritesOnly((p) => !p)}
                  title="Toggle favorites filter"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill={showFavoritesOnly ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                  </svg>
                  Favorites
                </button>
                <button
                  type="button"
                  className="da-button da-button-small da-button-secondary"
                  onClick={exportAllReports}
                  title="Export all reports"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                  </svg>
                  Export all
                </button>
              </div>
            )}
          </div>

          {reports.length > 0 && (
            <div className="da-search-wrapper" style={{ marginBottom: '0.85rem' }}>
              <svg className="da-search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <input
                type="text"
                className="da-input da-search-input"
                placeholder="Search reports..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          )}

          {reports.length === 0 ? (
            <div className="da-empty-state da-empty-state-enhanced">
              <div className="da-empty-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
              </div>
              <h3>Ready to analyze</h3>
              <p>Upload a PDF, DOCX, or TXT file to get instant insights.</p>
              <Link to="/analyze" className="da-button">Upload document</Link>
            </div>
          ) : filteredReports.length === 0 ? (
            <div className="da-empty-state da-empty-state-enhanced">
              <div className="da-empty-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
              </div>
              <h3>No matching reports</h3>
              <p>{showFavoritesOnly ? 'No favorite reports yet.' : 'Try a different search term.'}</p>
            </div>
          ) : (
            <div className="da-list">
              {filteredReports.map((item) => {
                const stats = getStats(item.analysis);
                return (
                  <div key={item.id} className="da-list-item da-list-item-rich da-fade-in">
                    <div className="da-list-item-header">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <button
                          type="button"
                          className="da-fav-btn"
                          onClick={() => toggleFavorite(item.id)}
                          title={item.favorite ? 'Remove from favorites' : 'Add to favorites'}
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill={item.favorite ? '#f59e0b' : 'none'} stroke={item.favorite ? '#f59e0b' : 'currentColor'} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                          </svg>
                        </button>
                        <div>
                          <p className="da-list-title">{item.filename}</p>
                          <p className="da-muted">{new Date(item.timestamp).toLocaleString()}</p>
                        </div>
                      </div>
                      <div className="da-mini-stats">
                        <span>Words: {Number(stats.word_count || 0).toLocaleString()}</span>
                        <span>Reading: {getReadingTime(stats.word_count)}</span>
                        <span>{item.analysis?.sentiment || 'Neutral'}</span>
                      </div>
                    </div>

                    <div className="da-row-actions">
                      <button type="button" className="da-button da-button-secondary" onClick={() => setSelectedReport(item)}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                          <circle cx="12" cy="12" r="3" />
                        </svg>
                        View
                      </button>
                      <button type="button" className="da-button da-button-secondary" onClick={() => downloadReport(item)}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                          <polyline points="7 10 12 15 17 10" />
                          <line x1="12" y1="15" x2="12" y2="3" />
                        </svg>
                        Download
                      </button>
                      <button type="button" className="da-button da-button-danger" onClick={() => handleDelete(item.id)}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="3 6 5 6 21 6" />
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                        </svg>
                        Delete
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </article>

        <article className="da-card da-slide-up" style={{ animationDelay: '120ms' }}>
          <div className="da-card-header">
            <h2>Insights</h2>
          </div>

          {reports.length > 0 ? (
            <div className="da-stack-large">
              <div>
                <h3 style={{ fontSize: '0.9rem', marginBottom: '0.6rem', fontWeight: 600 }}>Sentiment breakdown</h3>
                <div className="da-donut-chart">
                  <svg viewBox="0 0 120 120" width="120" height="120" className="da-donut-svg">
                    {(() => {
                      const total = reports.length || 1;
                      const segments = [
                        { label: 'Positive', count: sentimentDistribution.Positive, color: '#10b981' },
                        { label: 'Neutral', count: sentimentDistribution.Neutral, color: '#6a6a8a' },
                        { label: 'Negative', count: sentimentDistribution.Negative, color: '#ef4444' },
                      ];
                      const radius = 45;
                      const circumference = 2 * Math.PI * radius;
                      let offset = 0;
                      return segments.map((seg) => {
                        const pct = seg.count / total;
                        const dashArray = `${pct * circumference} ${circumference}`;
                        const dashOffset = -offset;
                        offset += pct * circumference;
                        return (
                          <circle
                            key={seg.label}
                            cx="60"
                            cy="60"
                            r={radius}
                            fill="none"
                            stroke={seg.color}
                            strokeWidth="16"
                            strokeDasharray={dashArray}
                            strokeDashoffset={dashOffset}
                            transform="rotate(-90 60 60)"
                            className="da-donut-segment"
                          />
                        );
                      });
                    })()}
                    <text x="60" y="56" textAnchor="middle" className="da-donut-center-text">{reports.length}</text>
                    <text x="60" y="72" textAnchor="middle" fill="var(--text-muted)" fontSize="10" fontFamily="Poppins">total</text>
                  </svg>
                  <div className="da-donut-legend">
                    {Object.entries(sentimentDistribution).map(([label, count]) => (
                      <div key={label} className="da-donut-legend-item">
                        <span className="da-donut-legend-color" style={{ background: label === 'Positive' ? 'var(--success)' : label === 'Negative' ? 'var(--danger)' : 'var(--text-muted)' }} />
                        <span className="da-donut-legend-label">{label}</span>
                        <span className="da-donut-legend-value">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {wordCloudData.length > 0 && (
                <div>
                  <h3 style={{ fontSize: '0.9rem', marginBottom: '0.6rem', fontWeight: 600 }}>Common words</h3>
                  <div className="da-word-cloud">
                    {wordCloudData.map(([word, count]) => (
                      <span
                        key={word}
                        style={{
                          fontSize: `${Math.max(0.7, Math.min(1.2, count / 3))}rem`,
                          opacity: Math.max(0.4, Math.min(1, count / 5)),
                        }}
                      >
                        {word}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h3 style={{ fontSize: '0.9rem', marginBottom: '0.6rem', fontWeight: 600 }}>Quick stats</h3>
                <div className="da-quick-stat-row">
                  <span className="da-quick-stat-label">Avg words per doc</span>
                  <span className="da-quick-stat-value">{reports.length > 0 ? Math.round(totalWords / reports.length).toLocaleString() : 0}</span>
                </div>
                <div className="da-quick-stat-row">
                  <span className="da-quick-stat-label">Total reading time</span>
                  <span className="da-quick-stat-value">{getReadingTime(totalWords)}</span>
                </div>
                <div className="da-quick-stat-row">
                  <span className="da-quick-stat-label">Favorites</span>
                  <span className="da-quick-stat-value">{favoriteCount} / {reports.length}</span>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '0.65rem' }}>
              <div className="da-feature-card da-feature-card-compact">
                <h3>Sentiment analysis</h3>
                <p className="da-muted">Understand the tone of your documents.</p>
              </div>
              <div className="da-feature-card da-feature-card-compact">
                <h3>Readability scoring</h3>
                <p className="da-muted">Measure grade level and complexity.</p>
              </div>
              <div className="da-feature-card da-feature-card-compact">
                <h3>Entity extraction</h3>
                <p className="da-muted">Capture names, dates, and organizations.</p>
              </div>
            </div>
          )}

          <div className="da-quick-actions">
            <Link to="/analyze" className="da-button da-button-secondary">Analyze now</Link>
          </div>
        </article>
      </div>

      {selectedReport && (
        <div className="da-modal-backdrop" onClick={() => setSelectedReport(null)}>
          <article className="da-modal da-scale-in" onClick={(e) => e.stopPropagation()}>
            <header className="da-modal-header">
              <h2>{selectedReport.filename}</h2>
              <button type="button" className="da-mini-action" onClick={() => setSelectedReport(null)}>Close</button>
            </header>

            <div className="da-modal-body">
              {selectedReport.textPreview && (
                <section>
                  <h3>Text preview</h3>
                  <div className="da-preview-box">{selectedReport.textPreview}</div>
                </section>
              )}

              {selectedReport.analysis?.statistics && (
                <section>
                  <h3>Statistics</h3>
                  <div className="da-token-grid">
                    <span className="da-token">Words: {selectedReport.analysis.statistics.word_count || 0}</span>
                    <span className="da-token">Characters: {selectedReport.analysis.statistics.character_count || 0}</span>
                    <span className="da-token">Sentences: {selectedReport.analysis.statistics.sentence_count || 0}</span>
                    <span className="da-token">Sentiment: {selectedReport.analysis.sentiment || 'Neutral'}</span>
                    <span className="da-token">Reading time: {getReadingTime(selectedReport.analysis.statistics.word_count)}</span>
                  </div>
                </section>
              )}

              {selectedReport.analysis?.summary && selectedReport.analysis.summary.length > 0 && (
                <section>
                  <h3>Summary</h3>
                  <p className="da-summary-text">{selectedReport.analysis.summary}</p>
                  <button type="button" className="da-button da-button-ghost da-button-small" onClick={() => copySummary(selectedReport.analysis.summary)}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                    </svg>
                    Copy summary
                  </button>
                </section>
              )}

              {selectedReport.report && (
                <section>
                  <h3>Full report</h3>
                  <pre className="da-report-block">{selectedReport.report}</pre>
                  <div className="da-row-actions">
                    <button type="button" className="da-button da-button-secondary" onClick={() => downloadReport(selectedReport)}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="7 10 12 15 17 10" />
                        <line x1="12" y1="15" x2="12" y2="3" />
                      </svg>
                      Download report
                    </button>
                  </div>
                </section>
              )}
            </div>
          </article>
        </div>
      )}
    </section>
  );
}

export default Dashboard;
