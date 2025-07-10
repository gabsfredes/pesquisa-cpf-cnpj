<template>
  <div class="home-container">
    <header class="home-header">
      <div class="user-info">
        <span>Bem-vind@, {{ auth.username || 'usuário' }}</span>
      </div>
      <button @click="logout">Sair do sistema</button>
    </header>

    <main class="home-main">
      <BuscaDocumento />
    </main>

    <footer class="home-footer">
      Trabalho da disciplina Redes de Computadores - UNIPAMPA
    </footer>
  </div>
</template>

<script setup>
import { useAuthStore } from '../store/auth'
import BuscaDocumento from '../components/BuscaDocumento.vue'

const auth = useAuthStore()
const logout = () => {
  auth.logout()
  location.href = '/config'
}
</script>
