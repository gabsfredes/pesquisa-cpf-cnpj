<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="doLogin">
      <input v-model="username" placeholder="Usuário" />
      <input v-model="password" type="password" placeholder="Senha" />
      <button type="submit">Entrar</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')

const doLogin = async () => {
  try {
    await auth.login({ username: username.value, password: password.value })
    router.push('/')
  } catch (err) {
    alert('Login falhou')
  }
}
</script>
