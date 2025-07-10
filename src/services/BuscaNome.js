import axios from 'axios'
import { useAuthStore } from '../store/auth'
import { useConfigStore } from '../store/config'

export async function buscarNome(name) {
  const config = useConfigStore()
  const auth = useAuthStore()

  const url = `${config.baseURL}/search_Name?name=${encodeURIComponent(name)}`

  const res = await axios.get(url, {
    headers: {
      Authorization: `Bearer ${auth.token}`,
    },
  })

  return res.data
}
