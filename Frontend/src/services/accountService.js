import { api } from './api.js'

export const listarCuentas = () => api('/cuentas')
export const crearCuenta = (nombre) => api('/cuentas', { method: 'POST', body: { nombre } })
export const renombrarCuenta = (id, nombre) => api(`/cuentas/${id}`, { method: 'PUT', body: { nombre } })
export const eliminarCuenta = (id) => api(`/cuentas/${id}`, { method: 'DELETE' })
