import { useEffect, useState } from 'react';
import { Send } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function Profile({ onClose }) {
  const { user } = useAuth();
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [telegramToken, setTelegramToken] = useState('');
  const [telegramTargets, setTelegramTargets] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [telegramLoading, setTelegramLoading] = useState(false);

  useEffect(() => {
    if (user) {
      loadTelegramTargets();
    }
  }, [user]);

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }

    setLoading(true);

    try {
      await axios.post(`${API_BASE}/auth/change-password`, {
        old_password: oldPassword,
        new_password: newPassword
      });
      setSuccess('Password updated successfully.');
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Update failed.');
    } finally {
      setLoading(false);
    }
  };

  const loadTelegramTargets = async () => {
    try {
      const response = await axios.get(`${API_BASE}/notifications/targets`);
      setTelegramTargets(response.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load Telegram targets.');
    }
  };

  const handleGenerateTelegramToken = async () => {
    setError('');
    setSuccess('');
    setTelegramLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/notifications/telegram/bind-token`);
      setTelegramToken(response.data.token);
      setSuccess('Telegram bind token generated.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate Telegram token.');
    } finally {
      setTelegramLoading(false);
    }
  };

  const handleSetDefaultTarget = async (targetId) => {
    setError('');
    setSuccess('');
    setTelegramLoading(true);
    try {
      await axios.patch(`${API_BASE}/notifications/targets/${targetId}/default`);
      await loadTelegramTargets();
      setSuccess('Default Telegram target updated.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update default target.');
    } finally {
      setTelegramLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        background: '#fff',
        borderRadius: '8px',
        width: '90%',
        maxWidth: '600px',
        maxHeight: '80vh',
        overflow: 'auto',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
      }}>
        <div style={{
          padding: '20px',
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>Password</h2>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '24px',
              cursor: 'pointer',
              color: '#666'
            }}
          >
            ×
          </button>
        </div>

        <div style={{ padding: '20px' }}>
          {error && (
            <div style={{
              padding: '12px',
              background: '#fee',
              border: '1px solid #fcc',
              borderRadius: '4px',
              color: '#c33',
              fontSize: '14px',
              marginBottom: '20px'
            }}>
              {error}
            </div>
          )}

          {success && (
            <div style={{
              padding: '12px',
              background: '#efe',
              border: '1px solid #cfc',
              borderRadius: '4px',
              color: '#3c3',
              fontSize: '14px',
              marginBottom: '20px'
            }}>
              {success}
            </div>
          )}

          <form onSubmit={handleChangePassword}>
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: '#666',
                fontSize: '14px'
              }}>
                Email
              </label>
              <input
                type="text"
                value={user?.email}
                disabled
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '14px',
                  background: '#f5f5f5',
                  boxSizing: 'border-box'
                }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: '#666',
                fontSize: '14px'
              }}>
                Registration Time
              </label>
              <input
                type="text"
                value={user?.created_at ? new Date(user.created_at).toLocaleString('zh-CN') : ''}
                disabled
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '14px',
                  background: '#f5f5f5',
                  boxSizing: 'border-box'
                }}
                />
              </div>

            <div style={{
              marginBottom: '24px',
              padding: '16px',
              border: '1px solid #e5e5e5',
              borderRadius: '6px',
              background: '#fafafa'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '14px',
                fontWeight: '600',
                marginBottom: '8px',
                color: '#1a1a1a'
              }}>
                <Send size={16} />
                Telegram Binding
              </div>
              {telegramTargets.length > 0 && (
                <div style={{ marginTop: '8px' }}>
                  <div style={{ fontSize: '13px', color: '#666', marginBottom: '6px' }}>
                    Bound targets
                  </div>
                  {telegramTargets.map((target) => (
                    <div key={target.id} style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '8px 10px',
                      border: '1px solid #e0e0e0',
                      borderRadius: '4px',
                      background: '#ffffff',
                      marginBottom: '6px',
                      fontSize: '13px'
                    }}>
                      <span>
                        {target.metadata?.title || target.destination}
                        {target.is_default ? ' (default)' : ''}
                      </span>
                      {!target.is_default && (
                        <button
                          type="button"
                          onClick={() => handleSetDefaultTarget(target.id)}
                          disabled={telegramLoading}
                          style={{
                            border: 'none',
                            background: 'none',
                            color: '#1a1a1a',
                            cursor: 'pointer',
                            textDecoration: 'underline',
                            fontSize: '13px'
                          }}
                        >
                          Set default
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
              <div style={{ fontSize: '13px', color: '#666', marginTop: '12px' }}>
                To add a new target: first send the token to <a href="https://t.me/uptospeed_bot" target="_blank" rel="noreferrer" style={{ color: '#1a1a1a' }}>@uptospeed_bot</a> in a private chat,
                or add the bot to a group. Then send the command below in the target chat.
              </div>
              <div style={{ marginTop: '10px' }}>
                <button
                  type="button"
                  onClick={handleGenerateTelegramToken}
                  disabled={telegramLoading}
                  style={{
                    padding: '8px 14px',
                    borderRadius: '4px',
                    border: '1px solid #1a1a1a',
                    background: '#ffffff',
                    color: '#1a1a1a',
                    fontSize: '14px',
                    cursor: telegramLoading ? 'not-allowed' : 'pointer'
                  }}
                >
                  {telegramLoading ? 'Generating...' : 'Generate Telegram Token'}
                </button>
              </div>
              {telegramToken && (
                <div style={{
                  marginTop: '10px',
                  padding: '10px',
                  background: '#ffffff',
                  border: '1px solid #e0e0e0',
                  borderRadius: '4px',
                  fontSize: '13px'
                }}>
                  <div style={{ marginBottom: '6px', color: '#666' }}>
                    Send this in the target chat to link it:
                  </div>
                  <div style={{ fontFamily: 'monospace' }}>/start {telegramToken}</div>
                </div>
              )}
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: '#333',
                fontSize: '14px',
                fontWeight: '500'
              }}>
                Current Password
              </label>
              <input
                type="password"
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '14px',
                  boxSizing: 'border-box'
                }}
                placeholder="Enter current password"
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: '#333',
                fontSize: '14px',
                fontWeight: '500'
              }}>
                New Password
              </label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '14px',
                  boxSizing: 'border-box'
                }}
                placeholder="At least 8 characters"
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: '#333',
                fontSize: '14px',
                fontWeight: '500'
              }}>
                Confirm New Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '14px',
                  boxSizing: 'border-box'
                }}
                placeholder="Re-enter new password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '12px',
                background: '#000',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                fontSize: '16px',
                fontWeight: '500',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1
              }}
            >
              {loading ? 'Changing...' : 'Change Password'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
