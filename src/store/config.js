import { defineStore } from 'pinia'

export const useConfigStore = defineStore('config', {
  state: () => ({
    ip: localStorage.getItem('ip') || '',
    porta: localStorage.getItem('porta') || '',
  }),
  getters: {
    baseURL: (state) => `http://${state.ip}:${state.porta}`,
    configurado: (state) => !!state.ip && !!state.porta,
  },
  actions: {
    setConfig(ip, porta) {
      this.ip = ip
      this.porta = porta
      localStorage.setItem('ip', ip)
      localStorage.setItem('porta', porta)
    },
    clearConfig() {
      this.ip = ''
      this.porta = ''
      localStorage.removeItem('ip')
      localStorage.removeItem('porta')
    }
  },
})
