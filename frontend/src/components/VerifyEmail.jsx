import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function VerifyEmail({ email, onBack, onSuccess }) {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const { login } = useAuth();

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (code.length !== 6) {
      setError('Please enter a 6-digit code');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/auth/verify-email`, {
        email,
        code
      });

      const { token, user } = response.data;
      login(token, user, false);
      if (onSuccess) onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Verification failed. Please check the code.');
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setError('');
    setResending(true);

    try {
      await axios.post(`${API_BASE}/auth/resend-verification`, { email });
      setCountdown(60);
    } catch (err) {
      setError(err.response?.data?.detail || 'Resend failed. Please try again later.');
    } finally {
      setResending(false);
    }
  };

  return (
    <div style={{ 
      width: '100%', 
      padding: '32px', 
      background: '#ffffff'
    }}>
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <h1 style={{ fontSize: '24px', fontWeight: '600', color: '#000', marginBottom: '8px' }}>
            Verify Email
          </h1>
          <p style={{ color: '#666', fontSize: '14px', marginBottom: '4px' }}>
            A verification code has been sent to
          </p>
          <p style={{ color: '#000', fontSize: '14px', fontWeight: '500' }}>
            {email}
          </p>
          <p style={{ color: '#999', fontSize: '12px', marginTop: '8px' }}>
            Please check your email and enter the 6-digit code
          </p>
        </div>

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

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontSize: '14px', fontWeight: '500' }}>
              Verification Code
            </label>
            <input
              type="text"
              value={code}
              onChange={(e) => {
                const value = e.target.value.replace(/\D/g, '').slice(0, 6);
                setCode(value);
              }}
              required
              maxLength={6}
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '20px',
                textAlign: 'center',
                letterSpacing: '8px',
                boxSizing: 'border-box',
                fontFamily: 'monospace'
              }}
              placeholder="000000"
            />
          </div>

          <button
            type="submit"
            disabled={loading || code.length !== 6}
            style={{
              width: '100%',
              padding: '12px',
              background: '#000',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              fontSize: '16px',
              fontWeight: '500',
              cursor: (loading || code.length !== 6) ? 'not-allowed' : 'pointer',
              opacity: (loading || code.length !== 6) ? 0.7 : 1,
              marginBottom: '12px'
            }}
          >
            {loading ? 'Verifying...' : 'Verify and Login'}
          </button>

          <button
            type="button"
            onClick={handleResend}
            disabled={resending || countdown > 0}
            style={{
              width: '100%',
              padding: '12px',
              background: '#fff',
              color: '#000',
              border: '1px solid #000',
              borderRadius: '4px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: (resending || countdown > 0) ? 'not-allowed' : 'pointer',
              opacity: (resending || countdown > 0) ? 0.5 : 1
            }}
          >
            {resending ? 'Sending...' : countdown > 0 ? `Resend in ${countdown}s` : 'Resend Code'}
          </button>
        </form>

        <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '14px', color: '#666' }}>
          <button
            onClick={onBack}
            style={{
              background: 'none',
              border: 'none',
              color: '#000',
              cursor: 'pointer',
              textDecoration: 'underline',
              fontSize: '14px'
            }}
          >
            ← Back to Login
          </button>
        </div>
      </div>
  );
}
