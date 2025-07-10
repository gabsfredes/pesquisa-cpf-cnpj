import { defineStore } from 'pinia'
import axios from 'axios'
import { useConfigStore } from './config'

const api = axios.create();

api.interceptors.request.use(config => {
  const authStore = useAuthStore();
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    username: localStorage.getItem('username') || null,
  }),
  actions: {
    async login(credentials) {
      const config = useConfigStore();
      if (!config.configurado) {
        throw new Error('IP e porta não configurados.');
      }

      const res = await api.post(`${config.baseURL}/login`, credentials);
      this.token = res.data.access_token;
      this.username = credentials.username;
      localStorage.setItem('token', this.token);
      localStorage.setItem('username', this.username);
    },
    logout() {
      this.token = null;
      this.username = null;
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      localStorage.removeItem('ip'); 
      localStorage.removeItem('porta'); 
      const config = useConfigStore(); 
      config.clearConfig();
    },
    async validateToken() {
      const config = useConfigStore();
      if (!this.token || !config.configurado) {
        return false;
      }
      try {
        const res = await api.get(`${config.baseURL}/validate_token`);
        return res.data.msg === `Token válido. Usuário: ${this.username}` || res.status === 200;
      } catch (error) {
        if (error.response && error.response.status === 401) {
          this.logout();
        }
        return false;
      }
    },
  },
});