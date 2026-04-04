import React from 'react';
import { Link } from 'react-router-dom';
import PublicHeader from './PublicHeader';
import Footer from './Footer';

function Home() {
  return (
    <div className="da-public-page da-home-page">
      <PublicHeader />

      <main>
        <section className="da-hero">
          <div className="da-hero-text da-fade-in">
            <p className="da-overline">AI-Powered Document Analysis</p>
            <h1>Analyze documents with precision.</h1>
            <p className="da-muted">
              Upload PDF, DOCX, or TXT files and receive structured analysis including sentiment,
              readability scores, entity extraction, and comprehensive summaries.
            </p>
            <div className="da-row-actions">
              <Link to="/register" className="da-button">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
                </svg>
                Get started
              </Link>
              <Link to="/about" className="da-button da-button-secondary">Learn more</Link>
            </div>
          </div>

          <div className="da-hero-card da-scale-in">
            <p className="da-card-kicker" style={{ color: '#94a3b8' }}>Sample analysis output</p>
            <div className="da-hero-metrics">
              <div>
                <span>2,847</span>
                <small>Words</small>
              </div>
              <div>
                <span>156</span>
                <small>Sentences</small>
              </div>
              <div>
                <span>Positive</span>
                <small>Sentiment</small>
              </div>
              <div>
                <span>8.2</span>
                <small>Grade Level</small>
              </div>
            </div>
          </div>
        </section>

        <section className="da-section da-fade-in">
          <header className="da-section-header">
            <p className="da-overline">Capabilities</p>
            <h2>Comprehensive document intelligence.</h2>
          </header>

          <div className="da-feature-grid">
            <article className="da-card da-feature-card">
              <h3>Multi-format parsing</h3>
              <p>Process PDF, DOCX, and TXT files through a unified analysis pipeline.</p>
            </article>
            <article className="da-card da-feature-card">
              <h3>Readability scoring</h3>
              <p>Calculate Flesch Reading Ease and Flesch-Kincaid Grade Level metrics.</p>
            </article>
            <article className="da-card da-feature-card">
              <h3>Sentiment analysis</h3>
              <p>Determine document tone using polarity and subjectivity measurements.</p>
            </article>
            <article className="da-card da-feature-card">
              <h3>Entity extraction</h3>
              <p>Identify names, dates, organizations, and monetary amounts automatically.</p>
            </article>
            <article className="da-card da-feature-card">
              <h3>Keyword analysis</h3>
              <p>Extract key terms and phrases that represent core document topics.</p>
            </article>
            <article className="da-card da-feature-card">
              <h3>Exportable reports</h3>
              <p>Download complete analysis reports in plain text for documentation and audits.</p>
            </article>
          </div>
        </section>

        <section className="da-section da-section-steps da-fade-in">
          <header className="da-section-header">
            <p className="da-overline">Workflow</p>
            <h2>Three steps from file to findings.</h2>
          </header>

          <div className="da-step-grid">
            <article className="da-card da-step-card">
              <span>01</span>
              <h3>Upload</h3>
              <p>Select a file from your machine or drag-and-drop into the analyzer.</p>
            </article>
            <article className="da-card da-step-card">
              <span>02</span>
              <h3>Analyze</h3>
              <p>Compute text statistics, readability, sentiment, and semantic clues.</p>
            </article>
            <article className="da-card da-step-card">
              <span>03</span>
              <h3>Act</h3>
              <p>Review key outcomes, copy summary snippets, and export full reports.</p>
            </article>
          </div>
        </section>

        <section className="da-cta da-fade-in">
          <h2>Ready to analyze your first document?</h2>
          <p className="da-muted">Create an account and start generating insights in minutes.</p>
          <Link to="/register" className="da-button">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
            </svg>
            Create account
          </Link>
        </section>
      </main>

      <Footer />
    </div>
  );
}

export default Home;
