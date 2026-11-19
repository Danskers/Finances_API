import { api } from './api.js'

export const login = (email, password) => api('/auth/login', { method: 'POST', body: { email, password } })
export const register = (email, password) => api('/auth/register', { method: 'POST', body: { email, password } })
