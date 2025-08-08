import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for cookies/sessions
});

// Add request interceptor to include auth token if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export const linksAPI = {
  // Create a new link
  createLink: async (linkData) => {
    try {
      const response = await api.post('/link/links', linkData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // Get all links
  getLinks: async (skip = 0, limit = 100, user_id = null) => {
    try {
      const params = { skip, limit };
      if (user_id) {
        params.user_id = user_id;
      }
      const response = await api.get('/link/links', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // Get a specific link - NOT IMPLEMENTED IN BACKEND
  // Commenting out until backend implements this endpoint
  /*
  getLink: async (linkId) => {
    try {
      const response = await api.get(`/link/links/${linkId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
  */

  // Delete a link - NOT IMPLEMENTED IN BACKEND
  // Commenting out until backend implements this endpoint
  /*
  deleteLink: async (linkId) => {
    try {
      await api.delete(`/link/links/${linkId}`);
      return true;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
  */

  // Search links
  searchLinks: async (query, limit = 10, similarity_threshold = 0.7, user_id = null) => {
    try {
      const params = { 
        q: query, 
        limit,
        similarity_threshold
      };
      if (user_id) {
        params.user_id = user_id;
      }
      const response = await api.get('/link/search', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};

export const authAPI = {
  // Initiate Google OAuth login
  googleLogin: () => {
    window.location.href = `${API_BASE_URL}/user/auth/google`;
  },

  // Get current user information
  getCurrentUser: async () => {
    try {
      const response = await api.get('/user/me');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // Logout
  logout: async () => {
    try {
      const response = await api.post('/user/logout');
      localStorage.removeItem('token');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // Handle OAuth callback (extract token from URL)
  handleOAuthCallback: () => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (token) {
      localStorage.setItem('token', token);
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
      return token;
    }
    return null;
  },
};

// Export wrapper functions for backwards compatibility
export const createLink = linksAPI.createLink;
export const fetchLinks = () => linksAPI.getLinks();
export const searchLinks = (query, limit) => linksAPI.searchLinks(query, limit);

export default { linksAPI, authAPI };