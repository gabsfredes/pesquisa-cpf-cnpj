<template>
  <div>
    <h2>Página Principal</h2>
    <SearchForm />
    <button @click="logout">Sair</button>
  </div>
</template>

<script setup>
import SearchForm from '../components/SearchForm.vue'
import { useAuthStore } from '../store/auth'
const auth = useAuthStore()
const logout = () => {
  auth.logout()
  location.href = '/login'
}
</script>
