// Cliente único: TODAS las peticiones pasan por el API Gateway.
const TOKEN_KEY = 'finanzas_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (t) => (t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY))

export async function api(ruta, { method = 'GET', body, formData } = {}) {
  const headers = {}
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  if (body) headers['Content-Type'] = 'application/json'

  const res = await fetch(ruta, {
    method,
    headers,
    body: formData ?? (body ? JSON.stringify(body) : undefined),
  })

  if (res.status === 204) return null
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    const detalle = data?.detail

    const mensaje = Array.isArray(detalle)
      ? detalle.map(error => error.msg).join(', ')
      : typeof detalle === 'string'
        ? detalle
        : 'No se pudo completar la acción.'

    throw new Error(mensaje)
  }
  return data
}
