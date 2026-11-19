import { api } from './api.js'

export const listarTransacciones = (mes) => api(`/transacciones${mes ? `?mes=${mes}` : ''}`)
export const crearTransaccion = (data) => api('/transacciones', { method: 'POST', body: data })
export const eliminarTransaccion = (id) => api(`/transacciones/${id}`, { method: 'DELETE' })
export const obtenerResumen = (mes) => api(`/resumen${mes ? `?mes=${mes}` : ''}`)
export const fijarLimite = (mes, monto_limite) => api('/limites', { method: 'PUT', body: { mes, monto_limite } })
export const obtenerBalances = () => api('/balances')
