<template>
  <div class="padrao-container">
    <form class="padrao-form" @submit.prevent="doLogin">
      <img src="/public/assets/logo-unipampa.jpg" alt="Logo" />
      <h2>Acesso ao Sistema</h2>
      <label for="username">Usuário:</label>
      <input v-model="username" type="text" placeholder="Usuário" required />
      <label for="password">Senha:</label>
      <input v-model="password" type="password" placeholder="Senha" required />
      <button type="submit" :disabled="loading">
        {{ loading ? 'Carregando...' : 'Entrar' }}
      </button>

      <p v-if="error" class="error-msg">Usuário ou senha inválidos</p>
      <router-link to="/register">Não possui conta? Registrar</router-link>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const loading = ref(false)
const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const password = ref('')
const error = ref(false)

const doLogin = async () => {
  try {
    loading.value = true
    error.value = false
    await auth.login({ username: username.value, password: password.value })
    router.push('/')
  } catch (err) {
    error.value = true
  } finally {
    loading.value = false
  }
}
</script>
<style scoped>
a {
  display: block;
  text-align: center;
  color: #007bff;
  margin-top:0.2rem;
}
</style>