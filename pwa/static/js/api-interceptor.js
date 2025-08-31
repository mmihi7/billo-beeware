import { supabase } from './supabase';

// Request interceptors
const requestInterceptors = [];

// Response interceptors
const responseInterceptors = [];

// Error interceptors
const errorInterceptors = [];

/**
 * Add a request interceptor
 * @param {Function} onFulfilled - Function to handle the request
 * @param {Function} onRejected - Function to handle request errors
 * @returns {Function} Function to remove the interceptor
 */
export const addRequestInterceptor = (onFulfilled, onRejected) => {
  const interceptor = { onFulfilled, onRejected };
  requestInterceptors.push(interceptor);
  
  // Return a function to remove this interceptor
  return () => {
    const index = requestInterceptors.indexOf(interceptor);
    if (index !== -1) {
      requestInterceptors.splice(index, 1);
    }
  };
};

/**
 * Add a response interceptor
 * @param {Function} onFulfilled - Function to handle the response
 * @param {Function} onRejected - Function to handle response errors
 * @returns {Function} Function to remove the interceptor
 */
export const addResponseInterceptor = (onFulfilled, onRejected) => {
  const interceptor = { onFulfilled, onRejected };
  responseInterceptors.push(interceptor);
  
  // Return a function to remove this interceptor
  return () => {
    const index = responseInterceptors.indexOf(interceptor);
    if (index !== -1) {
      responseInterceptors.splice(index, 1);
    }
  };
};

/**
 * Add an error interceptor
 * @param {Function} handler - Function to handle errors
 * @returns {Function} Function to remove the interceptor
 */
export const addErrorInterceptor = (handler) => {
  errorInterceptors.push(handler);
  
  // Return a function to remove this interceptor
  return () => {
    const index = errorInterceptors.indexOf(handler);
    if (index !== -1) {
      errorInterceptors.splice(index, 1);
    }
  };
};

/**
 * Process request through interceptors
 * @param {Object} config - Request configuration
 * @returns {Promise<Object>} Processed request configuration
 */
const processRequest = async (config) => {
  let processedConfig = { ...config };
  
  for (const interceptor of requestInterceptors) {
    try {
      processedConfig = await interceptor.onFulfilled(processedConfig) || processedConfig;
    } catch (error) {
      if (interceptor.onRejected) {
        await interceptor.onRejected(error);
      }
      throw error;
    }
  }
  
  return processedConfig;
};

/**
 * Process response through interceptors
 * @param {Object} response - Response object
 * @returns {Promise<Object>} Processed response
 */
const processResponse = async (response) => {
  let processedResponse = response;
  
  for (const interceptor of responseInterceptors) {
    try {
      processedResponse = await interceptor.onFulfilled(processedResponse) || processedResponse;
    } catch (error) {
      if (interceptor.onRejected) {
        await interceptor.onRejected(error);
      }
      throw error;
    }
  }
  
  return processedResponse;
};

/**
 * Handle errors through interceptors
 * @param {Error} error - The error that occurred
 * @returns {Promise<void>}
 */
const handleError = async (error) => {
  console.error('API Error:', error);
  
  for (const handler of errorInterceptors) {
    try {
      await handler(error);
    } catch (e) {
      console.error('Error in error interceptor:', e);
    }
  }
  
  // Re-throw the error for further handling
  throw error;
};

// Wrap the supabase client methods with interceptors
const originalFrom = supabase.from;
supabase.from = function(table) {
  const query = originalFrom.call(this, table);
  
  // Add interceptors to the query methods
  const methods = ['select', 'insert', 'update', 'delete'];
  
  methods.forEach(method => {
    if (typeof query[method] === 'function') {
      const originalMethod = query[method].bind(query);
      
      query[method] = async function(...args) {
        try {
          // Process request
          const requestConfig = {
            method,
            table,
            args,
            headers: {}
          };
          
          const processedConfig = await processRequest(requestConfig);
          
          // Execute the original method
          const response = await originalMethod(...processedConfig.args);
          
          // Process response
          return processResponse({
            ...response,
            config: processedConfig
          });
          
        } catch (error) {
          return handleError(error);
        }
      };
    }
  });
  
  return query;
};

// Export the enhanced supabase client
export { supabase as api };

// Example usage:
/*
// Add request interceptor
addRequestInterceptor(
  (config) => {
    // Add auth token to all requests
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor
addResponseInterceptor(
  (response) => {
    // Handle successful responses
    return response;
  },
  (error) => {
    // Handle response errors
    if (error.status === 401) {
      // Handle unauthorized
    }
    return Promise.reject(error);
  }
);

// Add error interceptor
addErrorInterceptor((error) => {
  // Log error to error tracking service
  console.error('API Error:', error);
});
*/
