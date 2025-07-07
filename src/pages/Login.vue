<template>
  <div class="login-container">
    <form class="login-form" @submit.prevent="doLogin">
      <img src="/public/assets/logo-unipampa.jpg" alt="Logo" />
      <h2>Acesso ao Sistema</h2>
      <input v-model="username" type="text" placeholder="Usuário" required />
      <input v-model="password" type="password" placeholder="Senha" required />
      <button type="submit" :disabled="loading">
        {{ loading ? 'Carregando...' : 'Entrar' }}
      </button>

      <p v-if="error" class="error-msg">Usuário ou senha inválidos</p>
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
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: #f1f1f1;
  margin: 0;
}

.login-form {
  background: white;
  font-family: "Roboto", sans-serif;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
  width: fit-content;
  display: flex;
  flex-direction: column;
}

.login-form h2 {
  margin-bottom: 1.5rem;
  text-align: center;
  color: #333;
}

.login-form img {
  width: 150px;
  height: auto;
  background-size: cover;
  margin: 0 auto 0;
}

.login-form input {
  margin-bottom: 1rem;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #c7c7c7;
  border-radius: 6px;
}

.login-form button {
  background: #007bff;
  color: white;
  padding: 10px;
  font-size: 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.login-form button:hover {
  background: #0056b3;
}

.error-msg {
  color: red;
  text-align: center;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.login-form::after {
  content: "Sistema de Pesquisa de CPF e CNPJ - UNIPAMPA";
  display: block;
  text-align: center;
  color: #888;
  font-size: 0.9rem;
  margin-top: 2rem;
}
</style>
