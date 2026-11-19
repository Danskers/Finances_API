
import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import logo from '../assets/kaibacorp-logo.png'
import { useAuth } from '../context/AuthContext.jsx'

export default function Login() {
  const { token, iniciarSesion } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  if (token) return <Navigate to="/" replace />

  async function enviar(e) {
    e.preventDefault()
    setError('')
    setCargando(true)

    try {
      await iniciarSesion(email, password)
      navigate('/')
    } catch (err) {
      setError(err.message)
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="pagina-auth">
      <img src={logo} alt="KaibaCorp" className="logo-auth" />

      <form className="tarjeta form-auth" onSubmit={enviar}>
        <h1>¡Bienvenido!</h1>
        <p className="sub">Inicia sesión para ver tus finanzas</p>

        <label>
          Correo
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </label>

        <label>
          Contraseña
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>

        {error && <p className="error" role="alert">{error}</p>}

        <button type="submit" className="boton" disabled={cargando}>
          {cargando ? 'Entrando...' : 'Entrar'}
        </button>

        <p className="sub centro">
          ¿Olvidaste tu cuenta?
          <br />
          <span>Contacta al administrador para recuperar el acceso.</span>
        </p>

        <p className="sub centro">
          ¿No tienes cuenta? <Link to="/registro">Regístrate</Link>
        </p>
      </form>
    </div>
  )
}
