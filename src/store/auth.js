import { defineStore } from 'pinia'
import axios from 'axios'
import { useConfigStore } from './config'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    username: localStorage.getItem('username') || null,
  }),
  actions: {
    async login(credentials) {
      const config = useConfigStore()
      if (!config.configurado) {
        throw new Error('IP e porta não configurados.')
      }

      const res = await axios.post(`${config.baseURL}/login`, credentials)
      this.token = res.data.access_token
      this.username = credentials.username
      localStorage.setItem('token', this.token)
      localStorage.setItem('username', this.username)
    },
    logout() {
      this.token = null
      this.username = null
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('ip')
      localStorage.removeItem('porta')
    },
  },
})
