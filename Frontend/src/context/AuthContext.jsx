import { createContext, useContext, useState } from 'react'
import { getToken, setToken } from '../services/api.js'
import * as auth from '../services/authService.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setTokenState] = useState(getToken())

  async function iniciarSesion(email, password) {
    const { access_token } = await auth.login(email, password)
    setToken(access_token)
    setTokenState(access_token)
  }
  async function registrar(email, password) {
    await auth.register(email, password)
    await iniciarSesion(email, password)
  }
  function cerrarSesion() {
    setToken(null)
    setTokenState(null)
  }

  return (
    <AuthContext.Provider value={{ token, iniciarSesion, registrar, cerrarSesion }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
