import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Profile from './Profile';

export default function Navbar({ onShowAuth }) {
  const { user } = useAuth();
  const [showProfile, setShowProfile] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  return (
    <>
      <nav style={{
        background: '#fff',
        borderBottom: '1px solid #e0e0e0',
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <div style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#000',
            marginBottom: '4px'
          }}>
            XTrack
          </div>
          <div style={{
            fontSize: '13px',
            color: '#666'
          }}>
            Track X accounts and get AI summaries
          </div>
        </div>

        <div style={{ position: 'relative' }}>
          {user ? (
            <>
              <button
                onClick={() => setShowMenu(!showMenu)}
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
                <span>{user.email}</span>
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
                      setShowProfile(true);
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
                    Profile
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
              Login / Register
            </button>
          )}
        </div>
      </nav>

      {showProfile && <Profile onClose={() => setShowProfile(false)} />}
    </>
  );
}
