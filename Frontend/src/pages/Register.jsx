
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

  // Validaciones de contraseña en tiempo real
  const requisitos = [
    {
      texto: 'Al menos 6 caracteres',
      cumplido: password.length >= 6,
    },
    {
      texto: 'Al menos un número (0-9)',
      cumplido: /\d/.test(password),
    },
    {
      texto: 'Al menos una letra',
      cumplido: /\p{L}/u.test(password),
    },
    {
      texto: 'Al menos un símbolo (!, @, #, $, etc.)',
      cumplido: password.split('').some(
        caracter => !/[\p{L}\p{N}\s]/u.test(caracter)
      ),
    },
  ]

  const passwordValida = requisitos.every(
    requisito => requisito.cumplido
  )

  async function enviar(e) {
    e.preventDefault()
    setError('')

    if (!passwordValida) {
      setError('La contraseña no cumple todos los requisitos.')
      return
    }

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

        <p className="sub">
          Empieza a controlar tus ingresos y gastos
        </p>

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
            onChange={(e) => {
              setPassword(e.target.value)
              setError('')
            }}
            required
          />
        </label>

        <div className="requisitos-password" aria-live="polite">
          <p className="sub">La contraseña debe contener:</p>

          <ul>
            {requisitos.map((requisito, index) => (
              <li
                key={index}
                style={{
                  color: requisito.cumplido ? 'green' : 'gray',
                  listStyle: 'none',
                  marginBottom: '5px',
                }}
              >
                {requisito.cumplido ? '✓' : '○'} {requisito.texto}
              </li>
            ))}
          </ul>
        </div>

        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        <button
          type="submit"
          className="boton"
          disabled={!passwordValida}
        >
          Crear cuenta
        </button>

        <p className="sub centro">
          ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
        </p>
      </form>
    </div>
  )
}
