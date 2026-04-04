import React from 'react';
import { Link } from 'react-router-dom';

function PublicHeader() {
  return (
    <header className="da-public-header">
      <Link to="/" className="da-public-brand">
        <span className="da-brand-mark">DA</span>
        <span>DocAnalyzer</span>
      </Link>

      <nav className="da-public-nav" aria-label="Public navigation">
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
        <Link to="/login">Sign in</Link>
        <Link to="/register">Get started</Link>
      </nav>
    </header>
  );
}

export default PublicHeader;
