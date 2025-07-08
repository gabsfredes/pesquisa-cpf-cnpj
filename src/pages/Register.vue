<template>
  <div class="padrao-container">
    <form class="padrao-form" @submit.prevent="registrar">
      <img src="/public/assets/logo-unipampa.jpg" alt="Logo" />
      <h2>Cadastro de Usuário</h2>

      <label for="username">Usuário:</label>
      <input id="username" v-model="username" required />

      <label for="password">Senha:</label>
      <input id="password" type="password" v-model="password" required />

      <button type="submit" :disabled="loading">
        {{ loading ? 'Cadastrando...' : 'Cadastrar' }}
      </button>

      <p v-if="mensagem" :class="{ sucesso: sucesso, erro: !sucesso }">{{ mensagem }}</p>
      <router-link to="/login">Já possui conta? Fazer login</router-link>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useConfigStore } from '../store/config'

const username = ref('')
const password = ref('')
const mensagem = ref('')
const sucesso = ref(false)
const loading = ref(false)

const config = useConfigStore()

const registrar = async () => {
  mensagem.value = ''
  sucesso.value = false
  loading.value = true

  try {
    const res = await axios.post(`${config.baseURL}/register`, {
      username: username.value,
      password: password.value
    })

    mensagem.value = res.data.msg || 'Usuário registrado com sucesso.'
    sucesso.value = true
  } catch (err) {
    mensagem.value = err.response?.data?.msg || 'Erro ao registrar usuário.'
    sucesso.value = false
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.sucesso {
  color: green;
  margin-top: 0.5rem;
  text-align: center;
}

.erro {
  color: red;
  margin-top: 0.5rem;
  text-align: center;
}

a {
  display: block;
  text-align: center;
  color: #007bff;
  margin-top:0.2rem;
}
</style>
