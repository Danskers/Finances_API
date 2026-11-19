import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// El frontend solo habla con el API Gateway (nginx, puerto 8080).
// El proxy evita problemas de CORS en desarrollo.
const GATEWAY = process.env.VITE_GATEWAY_URL || 'http://localhost:8080'
const rutas = ['/auth', '/cuentas', '/transacciones', '/resumen', '/limites', '/balances', '/uploads']

export default defineConfig({
  plugins: [react()],
  server: { proxy: Object.fromEntries(rutas.map((r) => [r, GATEWAY])) },
})
