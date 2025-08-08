import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  // Configure axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      localStorage.setItem('token', token);
    } else {
      delete axios.defaults.headers.common['Authorization'];
      localStorage.removeItem('token');
    }
  }, [token]);

  // Check if user is logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const tokenFromUrl = urlParams.get('token');
      
      if (tokenFromUrl) {
        // Save token from OAuth callback
        setToken(tokenFromUrl);
        localStorage.setItem('token', tokenFromUrl);
        axios.defaults.headers.common['Authorization'] = `Bearer ${tokenFromUrl}`;
        
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname);
      }

      if (token || tokenFromUrl) {
        try {
          const response = await axios.get('http://localhost:8000/user/me');
          setUser(response.data);
        } catch (error) {
          console.error('Auth check failed:', error);
          // Token is invalid, clear it
          setToken(null);
          setUser(null);
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = () => {
    // Redirect to Google OAuth
    window.location.href = 'http://localhost:8000/user/auth/google';
  };

  const logout = async () => {
    try {
      await axios.post('http://localhost:8000/user/logout');
    } catch (error) {
      console.error('Logout error:', error);
    }
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
