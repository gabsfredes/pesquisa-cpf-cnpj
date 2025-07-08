<template>
  <div class="padrao-container">
    <form class="padrao-form" @submit.prevent="salvarConfiguracao">
      <img src="/public/assets/logo-unipampa.jpg" alt="Logo" />
      <h2>Configuração de Servidor</h2>

      <label for="ip">IP do Servidor:</label>
      <input id="ip" v-model="ip" placeholder="ex: 127.0.0.1" required />

      <label for="porta">Porta:</label>
      <input id="porta" v-model="porta" placeholder="ex: 5000" required />

      <button type="submit" :disabled="loading">
        {{ loading ? 'Testando conexão...' : 'Conectar ao servidor' }}
      </button>

      <p v-if="mensagem" :class="sucesso ? 'sucesso' : 'erro'">{{ mensagem }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useConfigStore } from '../store/config'
import { useRouter } from 'vue-router'
import axios from 'axios'

const config = useConfigStore()
const router = useRouter()

const ip = ref(config.ip)
const porta = ref(config.porta)

const mensagem = ref('')
const sucesso = ref(false)
const loading = ref(false)

onMounted(() => {
  if (config.configurado) {
    router.push('/login')
  }
})

const salvarConfiguracao = async () => {
  mensagem.value = ''
  sucesso.value = false
  loading.value = true

  const testURL = `http://${ip.value}:${porta.value}/ping`

  try {
    const res = await axios.get(testURL, { timeout: 6000 })

    if (res.data.status === 'ok') {
      config.setConfig(ip.value, porta.value)
      sucesso.value = true
      mensagem.value = 'Conexão bem-sucedida. Redirecionando...'
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else {
      mensagem.value = 'O servidor respondeu, mas com erro inesperado.'
    }
  } catch (err) {
    mensagem.value = 'Não foi possível conectar ao servidor informado.'
  } finally {
    loading.value = false
  }
}
</script>
