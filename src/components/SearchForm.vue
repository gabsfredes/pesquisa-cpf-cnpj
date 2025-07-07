<template>
  <form class="search-form" @submit.prevent="search">
    <label for="busca">Busca por CPF ou CNPJ:</label>
    <div class="input-row">
      <input id="busca" v-model="value" placeholder="000.000.000-00 ou 00.000.000/0000-00" />
      <button type="submit" :disabled="loading">
        {{ loading ? 'Buscando...' : 'Pesquisar' }}
      </button>
    </div>

    <p v-if="loading" class="loading-msg">Carregando dados...</p>
    <p v-if="result?.erro" class="error-msg">{{ result.erro }}</p>

    <div v-if="result?.results?.length" class="search-result">
      <h3>Resultados:</h3>
      <table>
        <thead>
          <tr>
            <th>CPF / CNPJ</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in result.results" :key="index">
            <td>{{ item.cpf || item.cnpj }}</td>
            <td>
              <button @click="detalheSelecionado = item">Ver Detalhes</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal ou Seção Detalhes -->
    <div v-if="detalheSelecionado" class="detalhe-card">
      <h4>Detalhes</h4>
      <div v-for="(valor, chave) in detalheSelecionado" :key="chave" class="result-card">
        <div class="campo">{{ camposBonitos[chave] || chave }}</div>
        <div class="valor">
          <template v-if="chave === 'empresas_associadas' && Array.isArray(valor)">
            <div class="empresa-card" v-for="(empresa, idx) in valor" :key="idx">
              <div v-for="(v, k) in empresa" :key="k">
                <strong>{{ camposBonitos[k] || k }}:</strong> {{ formatarValor(k, v) }}
              </div>
            </div>
          </template>
          <template v-else>
            {{ formatarValor(chave, valor) }}
          </template>
        </div>

      </div>
      <button @click="detalheSelecionado = null" class="fechar">Fechar</button>
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
const loading = ref(false)
const detalheSelecionado = ref(null)

const camposBonitos = {
  nome: "Nome",
  cpf: "CPF",
  cnpj: "CNPJ",
  email: "E-mail",
  telefone: "Telefone",
  nasc: "Data de Nascimento",
  endereco: "Endereço",
  sexo: "Sexo",
  erro: "Erro",
  empresas_associadas: "Empresas Associadas"
}

function formatarValor(chave, valor) {
  if (!valor) return ''

  if (chave === 'cpf') {
    return valor.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4')
  }

  if (chave === 'cnpj') {
    return valor.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5')
  }

  if (chave.includes('nasc') && valor.length >= 10) {
    const data = new Date(valor)
    return data.toLocaleDateString('pt-BR')
  }

  // Empresas associadas — exibir como array de cartões
  if (chave === 'empresas_associadas' && Array.isArray(valor)) {
    return valor
  }

  if (Array.isArray(valor)) {
    return valor.length === 0 ? 'Nenhuma' : valor.join(', ')
  }

  return valor
}


function isValidCPF(cpf) {
  cpf = cpf.replace(/[^\d]+/g, '')
  if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false
  let soma = 0
  for (let i = 0; i < 9; i++) soma += parseInt(cpf.charAt(i)) * (10 - i)
  let resto = (soma * 10) % 11
  if (resto === 10 || resto === 11) resto = 0
  if (resto !== parseInt(cpf.charAt(9))) return false
  soma = 0
  for (let i = 0; i < 10; i++) soma += parseInt(cpf.charAt(i)) * (11 - i)
  resto = (soma * 10) % 11
  if (resto === 10 || resto === 11) resto = 0
  return resto === parseInt(cpf.charAt(10))
}

function isValidCNPJ(cnpj) {
  cnpj = cnpj.replace(/[^\d]+/g, '')
  if (cnpj.length !== 14 || /^(\d)\1+$/.test(cnpj)) return false
  let t = cnpj.length - 2,
    d = cnpj.substring(t),
    d1 = parseInt(d.charAt(0)),
    d2 = parseInt(d.charAt(1)),
    calc = x => {
      let n = 0,
        r = 2
      for (let i = x.length - 1; i >= 0; i--) {
        n += x.charAt(i) * r++
        if (r > 9) r = 2
      }
      return n
    }
  let dg1 = calc(cnpj.substring(0, t)) % 11
  dg1 = dg1 < 2 ? 0 : 11 - dg1
  if (dg1 !== d1) return false
  let dg2 = calc(cnpj.substring(0, t + 1)) % 11
  dg2 = dg2 < 2 ? 0 : 11 - dg2
  return dg2 === d2
}

const search = async () => {
  const clean = value.value.replace(/[^\d]+/g, '')
  const isCPF = clean.length === 11
  const isCNPJ = clean.length === 14

  result.value = null

  if (!isCPF && !isCNPJ) {
    result.value = { erro: 'Informe um CPF ou CNPJ com 11 ou 14 dígitos.' }
    return
  }

  if (isCPF && !isValidCPF(clean)) {
    result.value = { erro: 'CPF inválido.' }
    return
  }

  if (isCNPJ && !isValidCNPJ(clean)) {
    result.value = { erro: 'CNPJ inválido.' }
    return
  }

  try {
    loading.value = true
    const endpoint = isCPF
      ? `http://26.124.13.39:5000/search_CPFdb?cpf=${clean}`
      : `http://26.124.13.39:5000/search_CNPJdb?cnpj=${clean}`

    const res = await axios.get(endpoint, {
      headers: {
        Authorization: `Bearer ${auth.token}`,
      },
    })
    result.value = res.data
  } catch (err) {
    result.value = { erro: 'Erro ao consultar o CPF/CNPJ.' }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.search-form {
  background-color: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
  width: 90%;
  max-width: 1000px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.search-form label {
  font-weight: bold;
  color: #333;
}

.input-row {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.input-row input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
}

.input-row button {
  background: #007bff;
  color: white;
  padding: 12px 20px;
  font-size: 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.input-row button:hover {
  background: #0056b3;
}

.loading-msg {
  font-style: italic;
  color: #555;
  font-size: 0.95rem;
}

.error-msg {
  color: red;
  font-size: 0.95rem;
  margin-top: 0.5rem;
}

.search-result {
  width: 100%;
  margin-top: 1rem;
}

.result-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: #f9f9f9;
}

.result-card .campo {
  font-weight: bold;
  font-size: 1rem;
  color: #333;
  margin-bottom: 0.25rem;
}

.result-card .valor {
  font-size: 0.98rem;
  color: #555;
  word-wrap: break-word;
}

.search-result table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  font-size: 0.95rem;
}

.search-result th,
.search-result td {
  padding: 12px;
  border: 1px solid #ddd;
  text-align: left;
}

.search-result th {
  background: #f2f2f2;
  font-weight: bold;
}

.search-result button {
  background-color: #007bff;
  color: white;
  padding: 6px 12px;
  font-size: 0.9rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-result button:hover {
  background-color: #0056b3;
}

.detalhe-card {
  margin-top: 2rem;
  background: #fafafa;
  border: 1px solid #ddd;
  padding: 1.5rem;
  border-radius: 8px;
}

.fechar {
  margin-top: 1rem;
  background: #999;
  color: white;
  border: none;
  padding: 8px 16px;
  cursor: pointer;
  border-radius: 6px;
}

.fechar:hover {
  background: #666;
}

.empresa-card {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  padding: 0.75rem 1rem;
  margin: 0.5rem 0;
  border-radius: 6px;
}
</style>
