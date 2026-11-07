import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import logo from '../assets/kaibacorp-logo.png'
import { useAuth } from '../context/AuthContext.jsx'

export default function Register() {
  const { registrar } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function enviar(e) {
    e.preventDefault()
    setError('')
    try {
      await registrar(email, password)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="pagina-auth">
      <img src={logo} alt="KaibaCorp" className="logo-auth" />
      <form className="tarjeta form-auth" onSubmit={enviar}>
        <h1>Crea tu cuenta</h1>
        <p className="sub">Empieza a controlar tus ingresos y gastos</p>
        <label>Correo
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>Contraseña (mínimo 6 caracteres)
          <input type="password" minLength={6} value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        {error && <p className="error" role="alert">{error}</p>}
        <button type="submit" className="boton">Crear cuenta</button>
        <p className="sub centro">¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link></p>
      </form>
    </div>
  )
}
