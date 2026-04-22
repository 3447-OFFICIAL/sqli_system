import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('aegis_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = async (username, password) => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  const response = await api.post('/token', formData);
  localStorage.setItem('aegis_token', response.data.access_token);
  return response.data;
};

export const predict = async (query) => {
  const response = await api.post('/predict', { 
    query, 
    source_ip: '127.0.0.1',
    endpoint: '/api/v1/test' 
  });
  return response.data;
};

export const getLogs = async (limit = 20) => {
  const response = await api.get(`/logs?limit=${limit}`);
  return response.data;
};

export const WS_URL = 'ws://localhost:8000/ws/alerts';
