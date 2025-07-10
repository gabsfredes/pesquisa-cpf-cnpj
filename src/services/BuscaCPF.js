import axios from 'axios'
import { useAuthStore } from '../store/auth'
import { useConfigStore } from '../store/config'

export async function buscarCPF(cpf) {
  const config = useConfigStore()
  const auth = useAuthStore()

  const url = `${config.baseURL}/search_CPFdb?cpf=${cpf}`

  const res = await axios.get(url, {
    headers: {
      Authorization: `Bearer ${auth.token}`,
    },
  })

  return res.data
}
