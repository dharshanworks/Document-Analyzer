import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { getToken } from '../api';

export function useKeyboardShortcuts() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handler = (event) => {
      if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA' || event.target.isContentEditable) {
        return;
      }

      const key = event.key.toLowerCase();

      if (event.altKey) {
        const isAuthenticated = Boolean(getToken());

        const shortcuts = {
          d: () => isAuthenticated && navigate('/dashboard'),
          a: () => isAuthenticated && navigate('/analyze'),
          l: () => !isAuthenticated && navigate('/login'),
          r: () => !isAuthenticated && navigate('/register'),
          '?': () => {
            event.preventDefault();
            const existing = document.querySelector('.da-shortcut-modal');
            if (existing) {
              existing.remove();
            } else {
              showShortcutModal();
            }
          },
        };

        if (shortcuts[key]) {
          event.preventDefault();
          shortcuts[key]();
        }
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [navigate, location]);
}

function showShortcutModal() {
  const modal = document.createElement('div');
  modal.className = 'da-modal-backdrop da-shortcut-modal';
  modal.innerHTML = `
    <div class="da-modal da-shortcut-dialog" onclick="event.stopPropagation()">
      <div class="da-modal-header">
        <h2>Keyboard Shortcuts</h2>
        <button type="button" class="da-mini-action" onclick="this.closest('.da-shortcut-modal').remove()">Close</button>
      </div>
      <div class="da-modal-body">
        <div class="da-shortcut-grid">
          <div class="da-shortcut-category">
            <h3>Navigation</h3>
            <div class="da-shortcut-row"><kbd>Alt + D</kbd> Dashboard</div>
            <div class="da-shortcut-row"><kbd>Alt + A</kbd> Analyze</div>
          </div>
          <div class="da-shortcut-category">
            <h3>Actions</h3>
            <div class="da-shortcut-row"><kbd>Alt + ?</kbd> Show shortcuts</div>
          </div>
        </div>
      </div>
    </div>
  `;
  modal.addEventListener('click', () => modal.remove());
  document.body.appendChild(modal);
}

export default useKeyboardShortcuts;
