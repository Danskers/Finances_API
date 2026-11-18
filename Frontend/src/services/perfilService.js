// Conexión de la página "Mi perfil" con el auth-service.
// Si el backend usa otros nombres, solo se cambia aquí.
import { getToken } from './api.js'

const BASE = import.meta.env.VITE_API_URL || ''
const RUTA_PERFIL = '/auth/perfil'

async function pedir(metodo, cuerpo) {
  let respuesta
  try {
    respuesta = await fetch(`${BASE}${RUTA_PERFIL}`, {
      method: metodo,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getToken()}`,
      },
      body: cuerpo ? JSON.stringify(cuerpo) : undefined,
    })
  } catch {
    throw new Error('No se pudo conectar con el servidor.')
  }

  if (!respuesta.ok) {
    let detalle = ''
    try {
      const datos = await respuesta.json()
      detalle = typeof datos.detail === 'string' ? datos.detail : ''
    } catch {
      // la respuesta no traía JSON
    }
    throw new Error(detalle || 'No se pudo completar la acción.')
  }

  try {
    return await respuesta.json()
  } catch {
    return null
  }
}

export const actualizarPerfil = (datos) => pedir('PUT', datos)
export const eliminarPerfil = () => pedir('DELETE')
