import React, { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import PublicHeader from './PublicHeader';
import { api } from '../api';

function Register({ onRegisterSuccess }) {
  const [formData, setFormData] = useState({
    username: '',
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const passwordStrength = useMemo(() => {
    const value = formData.password;
    let score = 0;
    if (value.length >= 6) score += 1;
    if (value.length >= 10) score += 1;
    if (/[A-Z]/.test(value)) score += 1;
    if (/[0-9]/.test(value)) score += 1;
    if (/[^A-Za-z0-9]/.test(value)) score += 1;
    return score;
  }, [formData.password]);

  const strengthLabel = ['Very weak', 'Weak', 'Fair', 'Good', 'Strong', 'Very strong'][passwordStrength];

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Password confirmation does not match.');
      return;
    }

    setLoading(true);

    try {
      await api.post('/register', {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.fullName || undefined,
      });

      const loginResponse = await api.post('/login', {
        username: formData.username,
        password: formData.password,
      });

      localStorage.setItem('token', loginResponse.data.access_token);
      localStorage.setItem('userName', formData.username);
      if (formData.fullName) {
        localStorage.setItem('userFullName', formData.fullName);
      }
      onRegisterSuccess();
      navigate('/dashboard', { replace: true });
    } catch (registerError) {
      setError(registerError.response?.data?.error || 'Unable to create account right now.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="da-public-page da-auth-page">
      <PublicHeader />

      <main className="da-auth-layout">
        <section className="da-auth-promo">
          <p className="da-overline">Create your workspace</p>
          <h1>Start analyzing documents in one focused dashboard.</h1>
          <p className="da-muted">
            Save report history, inspect readability and sentiment, and export full summaries.
          </p>
          <ul className="da-auth-points">
            <li>Register in seconds</li>
            <li>No setup complexity</li>
            <li>Immediate access after sign-up</li>
          </ul>
        </section>

        <section className="da-card da-auth-card">
          <h2>Create account</h2>

          <form onSubmit={handleSubmit} className="da-form">
            {error && <p className="da-alert da-alert-error">{error}</p>}

            <label className="da-field">
              <span>Username</span>
              <input className="da-input" type="text" name="username" value={formData.username} onChange={handleChange} required />
            </label>

            <label className="da-field">
              <span>Full name</span>
              <input className="da-input" type="text" name="fullName" value={formData.fullName} onChange={handleChange} placeholder="e.g. John Doe" />
            </label>

            <label className="da-field">
              <span>Email</span>
              <input className="da-input" type="email" name="email" value={formData.email} onChange={handleChange} required />
            </label>

            <label className="da-field">
              <span>Password</span>
              <input className="da-input" type="password" name="password" value={formData.password} onChange={handleChange} required />
            </label>

            {formData.password && (
              <div className="da-password-meter" aria-live="polite">
                <div className="da-password-meter-track">
                  <span style={{ width: `${(passwordStrength / 5) * 100}%` }} />
                </div>
                <p className="da-muted">Strength: {strengthLabel}</p>
              </div>
            )}

            <label className="da-field">
              <span>Confirm password</span>
              <input className="da-input" type="password" name="confirmPassword" value={formData.confirmPassword} onChange={handleChange} required />
            </label>

            <button type="submit" className="da-button" disabled={loading}>
              {loading ? 'Creating account...' : 'Create account'}
            </button>
          </form>

          <p className="da-muted">
            Already registered? <Link className="da-inline-link" to="/login">Sign in</Link>
          </p>
        </section>
      </main>
    </div>
  );
}

export default Register;
