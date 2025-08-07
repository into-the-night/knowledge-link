import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const linksAPI = {
  // Create a new link
  createLink: async (linkData) => {
    try {
      const response = await api.post('/links', linkData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // Get all links
  getLinks: async (skip = 0, limit = 100) => {
    try {
      const response = await api.get('/links', {
        params: { skip, limit }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // Get a specific link
  getLink: async (linkId) => {
    try {
      const response = await api.get(`/links/${linkId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  // Delete a link
  deleteLink: async (linkId) => {
    try {
      await api.delete(`/links/${linkId}`);
      return true;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};

export default linksAPI;
