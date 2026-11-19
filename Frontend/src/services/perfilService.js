// Conexión de la página "Mi perfil" con el auth-service.
// Rutas del backend: GET, PUT y DELETE /auth/me
import { getToken } from './api.js'

const BASE = import.meta.env.VITE_API_URL || ''
const RUTA_PERFIL = '/auth/me'

function mensajeDeError(estado, detalle) {
  if (estado === 400 && detalle) return detalle
  if (estado === 403) return 'La contraseña actual es incorrecta.'
  if (estado === 401) return 'Tu sesión expiró. Inicia sesión de nuevo.'
  if (estado === 404) return 'Esta función aún no está disponible en el servidor.'
  if (estado === 409) return 'Ese correo ya está en uso.'
  if (estado === 422) return 'Los datos enviados no son válidos.'
  if (estado >= 500) return 'Error del servidor. Intenta de nuevo más tarde.'
  return 'No se pudo completar la acción.'
}

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
    throw new Error(mensajeDeError(respuesta.status, detalle))
  }

  try {
    return await respuesta.json()
  } catch {
    return null
  }
}

export const obtenerPerfil = () => pedir('GET')
export const actualizarPerfil = (datos) => pedir('PUT', datos)
export const eliminarPerfil = () => pedir('DELETE')
