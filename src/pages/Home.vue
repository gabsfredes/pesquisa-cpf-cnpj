<template>
  <div class="home-container">
    <header class="home-header">
      <div class="user-info">
        <span>Bem-vind@, {{ auth.username || 'usuário' }}</span>
      </div>
      <button @click="logout">Sair</button>
    </header>

    <main class="home-main">
      <SearchForm />
    </main>

    <footer class="home-footer">
      Trabalho da disciplina Redes de Computadores - UNIPAMPA
    </footer>
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

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f7f9fb;
  font-family: 'Roboto', sans-serif;
}

.home-header {
  background-color: #00a859;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.09);
}

.user-info {
  font-weight: bold;
}

.home-header button {
  background-color: #fff;
  color: #b80404;
  border: none;
  padding: 8px 16px;
  font-weight: bold;
  border-radius: 10px;
  font-size: 0.9rem;
  box-shadow: inset 0 2px 2px rgba(0,0,0,0.18);
  cursor: pointer;
  transition: background 0.3s;
}

.home-header button:hover {
  background-color: #e6e6e6;
}

.home-main {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: start;
  padding: 2rem;
}

.home-footer {
  background-color: #ddd;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.08);
  padding: 1rem;
  text-align: center;
  font-size: 0.95rem;
  color: #444;
}
</style>
