import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import PublicHeader from './PublicHeader';
import { api } from '../api';

function Login({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/login', { username, password });
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('userName', response.data.username || username);
      if (response.data.full_name) {
        localStorage.setItem('userFullName', response.data.full_name);
      }
      onLoginSuccess();
      navigate('/dashboard', { replace: true });
    } catch (loginError) {
      setError(loginError.response?.data?.error || 'Unable to sign in with these credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="da-public-page da-auth-page">
      <PublicHeader />

      <main className="da-auth-layout">
        <section className="da-auth-promo">
          <p className="da-overline">Welcome back</p>
          <h1>Your analysis workspace is ready.</h1>
          <p className="da-muted">
            Continue with your document archive, inspect reports, and launch new analysis runs.
          </p>
          <ul className="da-auth-points">
            <li>Secure token-based login</li>
            <li>Instant file analysis pipeline</li>
            <li>Export and archive support</li>
          </ul>
        </section>

        <section className="da-card da-auth-card">
          <h2>Sign in</h2>

          <form onSubmit={handleSubmit} className="da-form">
            {error && <p className="da-alert da-alert-error">{error}</p>}

            <label className="da-field">
              <span>Username</span>
              <input className="da-input" type="text" value={username} onChange={(event) => setUsername(event.target.value)} required />
            </label>

            <label className="da-field">
              <span>Password</span>
              <input className="da-input" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
            </label>

            <button type="submit" className="da-button" disabled={loading}>
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <p className="da-muted">
            Need an account? <Link className="da-inline-link" to="/register">Create one</Link>
          </p>
        </section>
      </main>
    </div>
  );
}

export default Login;
