import axios from 'axios';

// 1. Get the URL (Vite handles the switching between dev/prod automatically now)
export const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// 2. Create the custom Axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'ngrok-skip-browser-warning': 'true', 
    'Content-Type': 'application/json'
  }
});

export default apiClient;