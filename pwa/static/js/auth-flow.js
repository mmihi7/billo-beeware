import { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useServices } from './service-context';
import { ErrorBoundary } from './error-boundary';

// Login Component
export const LoginForm = ({ onSuccess, onSwitchToRegister, onSwitchToReset }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { auth } = useServices();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const { error: signInError } = await auth.signInWithPassword({
        email,
        password,
      });

      if (signInError) throw signInError;
      
      if (onSuccess) onSuccess();
      
    } catch (error) {
      console.error('Login error:', error);
      setError(error.message || 'Failed to sign in');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-form">
      <h2>Login</h2>
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        
        <div className="form-footer">
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
          <div className="auth-links">
            <button type="button" className="link" onClick={onSwitchToRegister}>
              Create an account
            </button>
            <button type="button" className="link" onClick={onSwitchToReset}>
              Forgot password?
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

// Registration Component
export const RegisterForm = ({ onSuccess, onSwitchToLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { auth } = useServices();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setError('');
    setIsLoading(true);

    try {
      // First sign up the user
      const { data, error: signUpError } = await auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
          },
        },
      });

      if (signUpError) throw signUpError;
      
      if (onSuccess) onSuccess(data);
      
    } catch (error) {
      console.error('Registration error:', error);
      setError(error.message || 'Failed to register');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-form">
      <h2>Create Account</h2>
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="fullName">Full Name</label>
          <input
            id="fullName"
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={6}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            id="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            minLength={6}
            required
          />
        </div>
        
        <div className="form-footer">
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Creating account...' : 'Create Account'}
          </button>
          <div className="auth-links">
            <button type="button" className="link" onClick={onSwitchToLogin}>
              Already have an account? Sign in
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

// Password Reset Component
export const ResetPasswordForm = ({ onSuccess, onSwitchToLogin }) => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { auth } = useServices();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const { error: resetError } = await auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/update-password`,
      });

      if (resetError) throw resetError;
      
      setMessage('Check your email for the password reset link');
      
    } catch (error) {
      console.error('Password reset error:', error);
      setError(error.message || 'Failed to send reset email');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-form">
      <h2>Reset Password</h2>
      {error && <div className="error-message">{error}</div>}
      {message ? (
        <div className="success-message">{message}</div>
      ) : (
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          
          <div className="form-footer">
            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Sending...' : 'Send Reset Link'}
            </button>
            <div className="auth-links">
              <button type="button" className="link" onClick={onSwitchToLogin}>
                Back to Login
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
};

// Main Auth Component
export const AuthFlow = ({ onAuthSuccess }) => {
  const [view, setView] = useState('login'); // 'login', 'register', 'reset'
  const { auth } = useServices();
  const navigate = useNavigate();

  const handleAuthSuccess = () => {
    if (onAuthSuccess) {
      onAuthSuccess();
    } else {
      // Default redirect
      navigate('/dashboard');
    }
  };

  // Check if user is already logged in
  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await auth.getSession();
      if (session) {
        handleAuthSuccess();
      }
    };
    
    checkAuth();
    
    // Listen for auth state changes
    const { data: { subscription } } = auth.onAuthStateChange((event, session) => {
      if (event === 'SIGNED_IN' && session) {
        handleAuthSuccess();
      }
    });
    
    return () => {
      subscription?.unsubscribe();
    };
  }, [auth, navigate, handleAuthSuccess]);

  const renderView = () => {
    switch (view) {
      case 'register':
        return (
          <RegisterForm
            onSuccess={handleAuthSuccess}
            onSwitchToLogin={() => setView('login')}
          />
        );
      case 'reset':
        return (
          <ResetPasswordForm
            onSuccess={handleAuthSuccess}
            onSwitchToLogin={() => setView('login')}
          />
        );
      case 'login':
      default:
        return (
          <LoginForm
            onSuccess={handleAuthSuccess}
            onSwitchToRegister={() => setView('register')}
            onSwitchToReset={() => setView('reset')}
          />
        );
    }
  };

  return (
    <ErrorBoundary>
      <div className="auth-container">
        <div className="auth-card">
          {renderView()}
        </div>
      </div>
    </ErrorBoundary>
  );
};

// Higher Order Component for protected routes
export const withAuth = (Component) => {
  const WrappedComponent = (props) => {
    const { auth } = useServices();
    const [isLoading, setIsLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
      const checkAuth = async () => {
        try {
          const { data: { session } } = await auth.getSession();
          if (!session) {
            navigate('/login');
          } else {
            setIsAuthenticated(true);
          }
        } catch (error) {
          console.error('Auth check failed:', error);
          navigate('/login');
        } finally {
          setIsLoading(false);
        }
      };

      checkAuth();

      // Listen for auth state changes
      const { data: { subscription } } = auth.onAuthStateChange((event, session) => {
        if (event === 'SIGNED_OUT') {
          navigate('/login');
        }
      });

      return () => {
        subscription?.unsubscribe();
      };
    }, [auth, navigate]);

    if (isLoading) {
      return <div>Loading...</div>; // Or a loading spinner
    }

    return isAuthenticated ? <Component {...props} /> : null;
  };

  return WrappedComponent;
};

// Example usage in a protected route:
/*
import { withAuth } from './auth-flow';

const Dashboard = () => {
  return <div>Protected Dashboard Content</div>;
};

export default withAuth(Dashboard);
*/
