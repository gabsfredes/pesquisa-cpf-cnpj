<template>
    <div class="search-form">
        <h2>Busca por nome, CPF ou CNPJ</h2>
        <form @submit.prevent="buscarDocumento">
            <div class="input-row">
                <input v-model="documento" placeholder="Digite aqui..." required />
                <button type="submit" :disabled="loading">
                    {{ loading ? 'Pesquisando...' : 'Buscar' }}
                </button>
            </div>
        </form>

        <div v-if="loading" class="loading-msg">Carregando...</div>
        <div v-if="erro" class="error-msg">{{ erro }}</div>

        <div v-if="resultados.length" class="search-result">
            <table>
                <thead>
                    <tr>
                        <th>Resultado</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    <template v-for="(item, index) in resultados" :key="index">
                        <tr>
                            <td>
                                <span v-if="lastSearchType === 'cpf'">{{ item.cpf }}</span>
                                <span v-else-if="lastSearchType === 'cnpj'">{{ item.cnpj_buscado }}</span>
                                <span v-else-if="lastSearchType === 'nome'">{{ item.nome }}</span>
                            </td>
                            <td>
                                <button @click="toggleDetalhes(index)">
                                    {{ item.exibirDetalhes ? 'Ocultar' : 'Ver detalhes' }}
                                </button>
                            </td>
                        </tr>

                        <tr v-if="item.exibirDetalhes">
                            <td colspan="2">
                                <div class="detalhe-card">
                                    <!-- Exibição de dados da empresa (se for CNPJ) -->
                                    <div v-if="item.cnpj_buscado">
                                        <p><strong>Razão Social:</strong> {{ item.razao_social }}</p>
                                        <p><strong>Capital Social:</strong> R$ {{ item.capital_social.toLocaleString()
                                            }}</p>
                                        <p><strong>Natureza Jurídica:</strong> {{ item.natureza_juridica }}</p>
                                        <p><strong>Porte da Empresa:</strong> {{ item.porte_empresa }}</p>

                                        <div v-if="item.socios?.length">
                                            <button @click="toggleSocios(index)">
                                                {{ item.exibirSocios ? 'Ocultar sócios' : 'Ver sócios' }}
                                            </button>

                                            <div v-if="item.exibirSocios" style="margin-top: 1rem;">
                                                <ul>
                                                    <li v-for="(socio, i) in item.socios" :key="i" class="empresa-card">
                                                        <p><strong>Nome do Sócio:</strong> {{ socio.nome_socio }}</p>
                                                        <p><strong>CPF/CNPJ:</strong> {{ socio.cnpj_cpf_socio }}</p>
                                                        <p><strong>Data de Entrada:</strong> {{
                                                            formatarData(socio.data_entrada_sociedade) }}</p>
                                                        <p><strong>Qualificação:</strong> {{
                                                            socio.qualificacao_socio_descricao }}</p>
                                                        <p v-if="socio.nome_representante_legal"><strong>Representante
                                                                Legal:</strong> {{ socio.nome_representante_legal }}</p>
                                                        <p>
                                                            <strong>Sexo: </strong>
                                                            <span v-if="socio.sexo === 'M'">Masculino</span>
                                                            <span v-else-if="socio.sexo === 'F'">Feminino</span>
                                                            <span v-else>Não aplicável</span>
                                                        </p>
                                                    </li>
                                                </ul>
                                            </div>
                                        </div>

                                        <div v-else>
                                            <p><em>Sem sócios cadastrados</em></p>
                                        </div>
                                    </div>

                                    <!-- Se for CPF -->
                                    <div v-else>
                                        <p><strong>Nome:</strong> {{ item.nome }}</p>
                                        <p><strong>Data de nascimento:</strong> {{ formatarData(item.nasc) }}</p>
                                        <p><strong>Sexo: </strong> {{ item.sexo }}</p>

                                        <div v-if="item.empresas_associadas?.length">
                                            <button @click="toggleEmpresas(index)">
                                                {{ item.exibirEmpresas ? 'Ocultar empresas' : 'Ver empresas associadas'
                                                }}
                                            </button>

                                            <div v-if="item.exibirEmpresas" style="margin-top: 1rem;">
                                                <ul>
                                                    <li v-for="(empresa, i) in item.empresas_associadas" :key="i"
                                                        class="empresa-card">
                                                        <p><strong>Razão Social:</strong> {{ empresa.razao_social }}</p>
                                                        <p><strong>CNPJ:</strong> {{ empresa.cnpj }}</p>
                                                        <p><strong>Capital Social:</strong> R$ {{
                                                            empresa.capital_social.toLocaleString() }}</p>
                                                        <p><strong>Data de Entrada:</strong> {{
                                                            formatarData(empresa.data_entrada_sociedade) }}</p>
                                                        <p><strong>Natureza Jurídica:</strong> {{
                                                            empresa.natureza_juridica }}</p>
                                                        <p><strong>Qualificação:</strong> {{ empresa.qualificacao_socio
                                                            }}</p>
                                                    </li>
                                                </ul>
                                            </div>
                                        </div>

                                        <div v-else>
                                            <p><em>Sem empresas associadas</em></p>
                                        </div>
                                    </div>
                                </div>
                            </td>
                        </tr>
                    </template>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { buscarCPF } from '../services/BuscaCPF'
import { buscarCNPJ } from '../services/BuscaCNPJ'
import { buscarNome } from '../services/BuscaNome'
import { isValidCPF, isValidCNPJ } from '../utils/validators'

const documento = ref('')
const resultados = ref([])
const erro = ref(null)
const loading = ref(false)
const lastSearchType = ref(null)

const buscarDocumento = async () => {
    erro.value = null
    resultados.value = []
    loading.value = true

    const doc = documento.value.replace(/\D/g, '')
    const originalInput = documento.value.trim()

    try {
        let data
        if (doc.length === 11) {
            if (!isValidCPF(doc)) { 
                erro.value = 'CPF inválido. Por favor, verifique os dígitos e tente novamente.';
                return; 
            }
            data = await buscarCPF(doc)
            lastSearchType.value = 'cpf'
        } else if (doc.length === 14) {
            if (!isValidCNPJ(doc)) { 
                erro.value = 'CNPJ inválido. Por favor, verifique os dígitos e tente novamente.';
                return;
            }
            data = await buscarCNPJ(doc)
            lastSearchType.value = 'cnpj'
        } else if (originalInput.length > 0) {
            if (/^[A-Za-zÀ-ÿ\s%]+$/.test(originalInput)) {
                data = await buscarNome(originalInput)
                lastSearchType.value = 'nome'
            } else {
                erro.value = 'Digite um nome válido (apenas letras, espaços ou %) ou um CPF/CNPJ válido.'
                return
            }
        } else {
            erro.value = 'Documento inválido. Use um CPF, CNPJ ou nome válido.'
            return
        }

        // Handle cases where the backend returns no results for a valid search
        if (data && (Array.isArray(data.results) && data.results.length === 0 || !data.results && !Array.isArray(data))) {
            erro.value = 'Nenhum resultado encontrado para o documento informado.';
            return;
        }

        // Se for resultado de CPF
        if (data.results) {
            resultados.value = data.results.map(item => ({
                ...item,
                exibirDetalhes: false,
                exibirEmpresas: false
            }))

        } else {
            resultados.value = [data]
        }

    } catch (e) {
        erro.value = 'Erro ao buscar os dados. Verifique o documento e tente novamente.'
    } finally {
        loading.value = false
    }
}


const formatarData = (raw) => {
    if (!raw || raw.length < 8) return raw

    // Se for no formato "20060323" → retorna "23/03/2006"
    if (/^\d{8}$/.test(raw)) {
        return `${raw.slice(6, 8)}/${raw.slice(4, 6)}/${raw.slice(0, 4)}`
    }

    // Se for formato ISO (ex: 1977-07-29) → retorna "29/07/1977"
    if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
        const [ano, mes, dia] = raw.split('-')
        return `${dia}/${mes}/${ano}`
    }

    return raw // fallback se vier em outro formato
}

const toggleDetalhes = (index) => {
    const item = resultados.value[index]
    item.exibirDetalhes = !item.exibirDetalhes
    if (!item.exibirDetalhes) {
        item.exibirEmpresas = false
        item.exibirSocios = false
    }
}

const toggleEmpresas = (index) => {
    resultados.value[index].exibirEmpresas = !resultados.value[index].exibirEmpresas
}

const toggleSocios = (index) => {
    resultados.value[index].exibirSocios = !resultados.value[index].exibirSocios
}

</script>
