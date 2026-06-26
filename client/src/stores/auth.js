import { defineStore } from 'pinia';
import apiClient from '../api';

export const useAuthStore = defineStore('auth', {
  state: () => {
    // 1. Check if we are safely in the browser
    const isClient = typeof window !== 'undefined';
    
    return {
      // 2. Safely parse user, or default to null if on the server or no user exists
      user: isClient && localStorage.getItem('user') 
              ? JSON.parse(localStorage.getItem('user')) 
              : null,
              
      // 3. Safely get token
      token: isClient ? localStorage.getItem('token') : null,
    };
  },
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(email, password) {
      // Example Backend Call
      const res = await apiClient.post('/auth/login', { email, password });
      this.token = res.data.access_token;
      this.user = res.data.user;
      
      // Persist
      localStorage.setItem('token', this.token);
      localStorage.setItem('user', JSON.stringify(this.user));
    },
    logout() {
      this.user = null;
      this.token = null;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // Redirect to home
      window.location.href = '/';
    }
  }
});