import { api } from './api.js'

// Sube una factura y devuelve { file_name, url, content_type, size }
export function subirFactura(archivo) {
  const formData = new FormData()
  formData.append('archivo', archivo)
  return api('/uploads', { method: 'POST', formData })
}
export const eliminarFactura = (fileName) => api(`/uploads/${fileName}`, { method: 'DELETE' })
