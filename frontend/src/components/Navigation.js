import React, { useEffect, useState } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { clearAuthToken } from '../api';

const NAV_ITEMS = [
  {
    to: '/dashboard',
    label: 'Dashboard',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
      </svg>
    ),
  },
  {
    to: '/analyze',
    label: 'Analyze',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
      </svg>
    ),
  },
];

function Navigation({ onLogout }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const storedName = localStorage.getItem('userName') || '';
  const storedFullName = localStorage.getItem('userFullName') || '';
  const displayName = storedFullName || storedName || 'User';
  const displayInitial = displayName[0]?.toUpperCase() || 'U';

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  const handleLogout = () => {
    clearAuthToken();
    localStorage.removeItem('userName');
    localStorage.removeItem('userFullName');
    onLogout();
    navigate('/login', { replace: true });
  };

  return (
    <>
      <button
        className="da-nav-mobile-toggle"
        type="button"
        onClick={() => setMenuOpen((current) => !current)}
        aria-label="Toggle menu"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>

      <aside className={`da-sidebar ${menuOpen ? 'is-open' : ''}`}>
        <div className="da-sidebar-brand">
          <span className="da-brand-mark">DA</span>
          <div>
            <p className="da-brand-title">DocAnalyzer</p>
            <p className="da-brand-subtitle">Workspace</p>
          </div>
        </div>

        <nav className="da-sidebar-nav" aria-label="Primary">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `da-sidebar-link ${isActive ? 'is-active' : ''}`
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="da-sidebar-footer">
          <div className="da-user-chip">
            <span className="da-user-avatar">
              {displayInitial}
            </span>
            <div>
              <p className="da-user-name">{displayName}</p>
              <p className="da-user-meta">Active session</p>
            </div>
          </div>

          <button type="button" className="da-ghost-button" onClick={handleLogout}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            Log out
          </button>
        </div>
      </aside>

      {menuOpen && (
        <button
          type="button"
          className="da-sidebar-backdrop"
          aria-label="Close menu"
          onClick={() => setMenuOpen(false)}
        />
      )}
    </>
  );
}

export default Navigation;
