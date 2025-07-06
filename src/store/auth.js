import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    username: localStorage.getItem('username') || null,
  }),
  actions: {
    async login(credentials) {
      const res = await axios.post('http://26.124.13.39:5000/login', credentials)
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
    },
  },
})

