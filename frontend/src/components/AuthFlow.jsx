import { useState } from 'react';
import Login from './Login';
import Register from './Register';
import VerifyEmail from './VerifyEmail';
import ForgotPassword from './ForgotPassword';

export default function AuthFlow({ onSuccess }) {
  const [currentView, setCurrentView] = useState('login'); // 'login', 'register', 'verify', 'forgot'
  const [pendingEmail, setPendingEmail] = useState('');

  const handleRegistrationSuccess = (email) => {
    setPendingEmail(email);
    setCurrentView('verify');
  };

  const handleBackToLogin = () => {
    setPendingEmail('');
    setCurrentView('login');
  };

  if (currentView === 'register') {
    return (
      <Register
        onSwitchToLogin={() => setCurrentView('login')}
        onRegistrationSuccess={handleRegistrationSuccess}
      />
    );
  }

  if (currentView === 'verify') {
    return (
      <VerifyEmail
        email={pendingEmail}
        onBack={handleBackToLogin}
        onSuccess={onSuccess}
      />
    );
  }

  if (currentView === 'forgot') {
    return (
      <ForgotPassword
        onBack={() => setCurrentView('login')}
      />
    );
  }

  return (
    <Login
      onSwitchToRegister={() => setCurrentView('register')}
      onSwitchToForgotPassword={() => setCurrentView('forgot')}
      onSuccess={onSuccess}
    />
  );
}

