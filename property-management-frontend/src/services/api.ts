import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;

      // Handle 401 Unauthorized
      if (status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        toast.error('Session expired. Please login again.');
        return Promise.reject(error);
      }

      // Handle 403 Forbidden
      if (status === 403) {
        toast.error('You do not have permission to perform this action.');
        return Promise.reject(error);
      }

      // Handle 404 Not Found
      if (status === 404) {
        toast.error('Resource not found.');
        return Promise.reject(error);
      }

      // Handle 422 Validation Error
      if (status === 422) {
        const message = data.detail || 'Validation error';
        toast.error(message);
        return Promise.reject(error);
      }

      // Handle 500 Server Error
      if (status === 500) {
        toast.error('Server error. Please try again later.');
        return Promise.reject(error);
      }

      // Handle other errors
      const message = data.detail || data.message || 'An error occurred';
      toast.error(message);
    } else if (error.request) {
      // Network error
      toast.error('Network error. Please check your connection.');
    } else {
      toast.error('An unexpected error occurred.');
    }

    return Promise.reject(error);
  }
);

export default api;