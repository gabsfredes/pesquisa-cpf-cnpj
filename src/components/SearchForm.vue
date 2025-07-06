<template>
  <form @submit.prevent="search">
    <input v-model="value" placeholder="Digite CPF ou CNPJ" />
    <button type="submit">Pesquisar</button>
    <div v-if="result">
      <pre>{{ result }}</pre>
    </div>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../store/auth'

const value = ref('')
const result = ref(null)
const auth = useAuthStore()

const search = async () => {
  try {
    const res = await axios.post(
      'http://localhost:5000/search',
      { value: value.value },
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )
    result.value = res.data
  } catch (err) {
    alert('Erro na pesquisa')
  }
}
</script>
