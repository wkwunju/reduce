import { useState } from 'react';
import { Menu } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Navbar({ onShowAuth, onToggleMenu, onShowProfile }) {
  const { user, logout } = useAuth();
  const [showMenu, setShowMenu] = useState(false);

  return (
    <>
      <nav style={{
        background: '#f8f8f8',
        padding: '12px 32px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div className="brand">
          <div style={{
            fontSize: '20px',
            fontWeight: '600',
            color: '#1a1a1a',
            letterSpacing: '-0.02em'
          }}>
            XTrack
          </div>
          <div className="brand-tagline">Only the signal. No noise.</div>
        </div>

        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: '12px' }}>
          {onToggleMenu && (
            <button
              className="mobile-menu-button"
              onClick={onToggleMenu}
              aria-label="Toggle menu"
              style={{
                background: '#ffffff',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                padding: '6px',
                cursor: 'pointer',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <Menu size={18} />
            </button>
          )}
          {user ? (
            <>
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="account-button"
                style={{
                  background: '#f5f5f5',
                  border: '1px solid #e0e0e0',
                  borderRadius: '20px',
                  padding: '8px 16px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <span className="account-email">{user.email}</span>
                <span className="account-initial" aria-hidden="true">
                  {(user.email || 'U').trim().charAt(0).toUpperCase()}
                </span>
                <span style={{ fontSize: '12px' }}>▼</span>
              </button>

              {showMenu && (
                <div style={{
                  position: 'absolute',
                  right: 0,
                  top: '100%',
                  marginTop: '8px',
                  background: '#fff',
                  border: '1px solid #e0e0e0',
                  borderRadius: '8px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  minWidth: '200px',
                  zIndex: 100
                }}>
                  <button
                    onClick={() => {
                      if (onShowProfile) {
                        onShowProfile();
                      }
                      setShowMenu(false);
                    }}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      background: 'none',
                      border: 'none',
                      textAlign: 'left',
                      cursor: 'pointer',
                      fontSize: '14px',
                      borderBottom: '1px solid #f0f0f0'
                    }}
                    onMouseEnter={(e) => e.target.style.background = '#f5f5f5'}
                    onMouseLeave={(e) => e.target.style.background = 'none'}
                  >
                    Setting
                  </button>
                  <button
                    onClick={() => {
                      logout();
                      setShowMenu(false);
                    }}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      background: 'none',
                      border: 'none',
                      textAlign: 'left',
                      cursor: 'pointer',
                      fontSize: '14px'
                    }}
                    onMouseEnter={(e) => e.target.style.background = '#f5f5f5'}
                    onMouseLeave={(e) => e.target.style.background = 'none'}
                  >
                    Log out
                  </button>
                </div>
              )}
            </>
          ) : (
            <button
              onClick={onShowAuth}
              style={{
                background: '#000',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                padding: '10px 20px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500'
              }}
            >
              Login
            </button>
          )}
        </div>
      </nav>

    </>
  );
}
