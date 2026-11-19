
import { api } from './api.js'

// Envía la factura al Storage Service.
// Devuelve inicialmente un task_id y el estado pending.
export function subirFactura(archivo) {
  const formData = new FormData()
  formData.append('archivo', archivo)

  return api('/uploads', {
    method: 'POST',
    formData,
  })
}

// Consulta el estado de procesamiento de una factura.
export function consultarSubida(taskId) {
  return api(`/uploads/${taskId}`)
}

// Espera hasta que Celery termine de procesar la factura.
export async function esperarSubida(taskId, intervalo = 1500, tiempoMaximo = 60000) {
  const inicio = Date.now()

  while (Date.now() - inicio < tiempoMaximo) {
    const resultado = await consultarSubida(taskId)

    if (resultado.status === 'completed') {
      if (!resultado.url) {
        throw new Error('La factura terminó de procesarse, pero no se recibió su URL.')
      }

      return resultado.url
    }

    if (resultado.status === 'failed') {
      throw new Error(resultado.error || 'No fue posible procesar la factura.')
    }

    if (!['pending', 'processing'].includes(resultado.status)) {
      throw new Error(`Estado de subida inesperado: ${resultado.status}`)
    }

    await new Promise(resolve => setTimeout(resolve, intervalo))
  }

  throw new Error('La subida tardó demasiado. Consulta el estado de la factura antes de volver a intentarlo.')
}

export const eliminarFactura = (fileName) =>
  api(`/uploads/${fileName}`, { method: 'DELETE' })
