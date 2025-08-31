import { createContext, useContext } from 'react';
import { AuthService } from './auth-service';
import { supabase } from './supabase';

// Create context with default values
const ServiceContext = createContext({
  auth: null,
  supabase: null,
  // Will be populated with actual services
  orders: null,
  payments: null,
  tabs: null,
  // Add other services here
});

// Custom hook to use the service context
export const useServices = () => {
  const context = useContext(ServiceContext);
  if (!context) {
    throw new Error('useServices must be used within a ServiceProvider');
  }
  return context;
};

// Service provider component
export const ServiceProvider = ({ children, services = {} }) => {
  // Default services
  const defaultServices = {
    auth: AuthService,
    supabase,
    // Initialize other services here
  };

  // Merge default services with any provided services
  const value = {
    ...defaultServices,
    ...services,
  };

  return (
    <ServiceContext.Provider value={value}>
      {children}
    </ServiceContext.Provider>
  );
};

// Export the context itself for advanced use cases
export default ServiceContext;
