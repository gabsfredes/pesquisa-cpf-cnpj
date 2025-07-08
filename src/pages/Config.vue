<template>
  <div class="padrao-container">
    <form class="padrao-form" @submit.prevent="salvarConfiguracao">
      <img src="/public/assets/logo-unipampa.jpg" alt="Logo" />
      <h2>Configuração de Servidor</h2>

      <label for="ip">IP do Servidor:</label>
      <input id="ip" v-model="ip" placeholder="ex: 127.0.0.1" required />

      <label for="porta">Porta:</label>
      <input id="porta" v-model="porta" placeholder="ex: 5000" required />

      <button type="submit">Salvar e continuar</button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useConfigStore } from '../store/config'
import { useRouter } from 'vue-router'

const config = useConfigStore()
const router = useRouter()

const ip = ref(config.ip)
const porta = ref(config.porta)

onMounted(() => {
  if (config.configurado) {
    router.push('/login')
  }
})

const salvarConfiguracao = () => {
  config.setConfig(ip.value, porta.value)
  router.push('/login')
}
</script>
