<template>
  <form class="search-form" @submit.prevent>
    <div class="search-helpers">
      <label for="busca">Busca por nome de pessoa física ou CPF ou CNPJ.</label>
        <span class="info">
          Você pode buscar por CPF, CNPJ ou nome de pessoa física. Não é necessário informar caracteres especiais nem
          nome completo.
        </span>
    </div>

    <div class="input-row">
      <input id="busca" v-model="value" placeholder="Informe aqui a sua busca" />
      <button type="submit" :disabled="loading" @click="novaBusca">
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
import { useConfigStore } from '../store/config'
import { isValidCPF, isValidCNPJ } from '../utils/validators'
import { nextTick } from 'vue'

const value = ref('')
const result = ref(null)
const auth = useAuthStore()
const loading = ref(false)
const detalheSelecionado = ref(null)
const config = useConfigStore()


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

const novaBusca = async () => {
  detalheSelecionado.value = null
  await nextTick()         // aguarda DOM reagir ao fechamento do modal
  await search()           // agora roda a busca
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

const search = async () => {
  detalheSelecionado.value = null
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
      ? `${config.baseURL}/search_CPFdb?cpf=${clean}`
      : `${config.baseURL}/search_CNPJdb?cnpj=${clean}`

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
