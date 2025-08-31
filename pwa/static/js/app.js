import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ServiceProvider } from './service-context';
import { AuthFlow, withAuth } from './auth-flow';
import { ErrorBoundary } from './error-boundary';
import { supabase } from './supabase';
import { AuthService } from './auth-service';
import './api-interceptor'; // Initialize API interceptors

// Import your components
const Dashboard = React.lazy(() => import('./components/Dashboard'));
const Orders = React.lazy(() => import('./components/Orders'));
const Menu = React.lazy(() => import('./components/Menu'));
const Settings = React.lazy(() => import('./components/Settings'));

// Create services
const authService = new AuthService();

// Initialize services
const services = {
  auth: authService,
  supabase,
  // Add other services here as they're implemented
};

// Protected route component
const ProtectedRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = React.useState(null);
  
  React.useEffect(() => {
    const checkAuth = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        setIsAuthenticated(!!session);
      } catch (error) {
        console.error('Auth check failed:', error);
        setIsAuthenticated(false);
      }
    };
    
    checkAuth();
    
    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      setIsAuthenticated(!!session);
    });
    
    return () => {
      subscription?.unsubscribe();
    };
  }, []);
  
  if (isAuthenticated === null) {
    // Show loading state
    return <div>Loading...</div>;
  }
  
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Main App component
const App = () => {
  return (
    <ServiceProvider services={services}>
      <ErrorBoundary>
        <React.Suspense fallback={<div>Loading...</div>}>
          <Router>
            <Routes>
              <Route path="/login" element={<AuthFlow onAuthSuccess={() => window.location.href = '/dashboard'} />} />
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/orders" 
                element={
                  <ProtectedRoute>
                    <Orders />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/menu" 
                element={
                  <ProtectedRoute>
                    <Menu />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/settings" 
                element={
                  <ProtectedRoute>
                    <Settings />
                  </ProtectedRoute>
                } 
              />
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="*" element={<div>404 Not Found</div>} />
            </Routes>
          </Router>
        </React.Suspense>
      </ErrorBoundary>
    </ServiceProvider>
  );
};

// Initialize the app
const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}

// Global error handler
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
  // Here you can add error reporting to a service like Sentry
});

// Unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled rejection:', event.reason);
  // Here you can add error reporting to a service like Sentry
});

// Service Worker registration
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js').then(
      (registration) => {
        console.log('ServiceWorker registration successful');
      },
      (err) => {
        console.error('ServiceWorker registration failed: ', err);
      }
    );
  });
}
