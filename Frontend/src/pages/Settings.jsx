import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { useTema, cambiarTema } from '../theme.js'
import { actualizarPerfil, eliminarPerfil } from '../services/perfilService.js'
import './Settings.css'

// Intenta leer el correo desde el token (si el token es un JWT).
function correoDelToken(token) {
  try {
    const parte = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    const datos = JSON.parse(atob(parte))
    const valor = String(datos.email || datos.sub || '')
    return valor.includes('@') ? valor : ''
  } catch {
    return ''
  }
}

export default function Settings() {
  const { token, cerrarSesion } = useAuth()
  const { tema } = useTema()
  const navigate = useNavigate()

  const correoOriginal = correoDelToken(token)
  const [email, setEmail] = useState(correoOriginal)
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [mostrar, setMostrar] = useState(false)
  const [aviso, setAviso] = useState(null)
  const [guardando, setGuardando] = useState(false)

  const [verEliminar, setVerEliminar] = useState(false)
  const [textoConfirmar, setTextoConfirmar] = useState('')
  const [eliminando, setEliminando] = useState(false)
  const [errorEliminar, setErrorEliminar] = useState('')

  const requisitos = [
    { texto: 'Al menos 6 caracteres', cumplido: password.length >= 6 },
    { texto: 'Al menos un número (0-9)', cumplido: /\d/.test(password) },
    { texto: 'Al menos una letra', cumplido: /\p{L}/u.test(password) },
    {
      texto: 'Al menos un símbolo (!, @, #, $, etc.)',
      cumplido: password.split('').some((c) => !/[\p{L}\p{N}\s]/u.test(c)),
    },
  ]
  const quiereCambiarPassword = password.length > 0
  const passwordValida = requisitos.every((r) => r.cumplido)
  const coinciden = password === confirmPassword

  async function guardar(e) {
    e.preventDefault()
    setAviso(null)

    if (quiereCambiarPassword && !passwordValida) {
      setAviso({ tipo: 'error', texto: 'La contraseña no cumple todos los requisitos.' })
      return
    }
    if (quiereCambiarPassword && !coinciden) {
      setAviso({ tipo: 'error', texto: 'Las contraseñas no coinciden.' })
      return
    }

    const datos = {}
    if (email.trim() && email.trim() !== correoOriginal) datos.email = email.trim()
    if (quiereCambiarPassword) datos.password = password

    if (Object.keys(datos).length === 0) {
      setAviso({ tipo: 'info', texto: 'No hay cambios para guardar.' })
      return
    }

    setGuardando(true)
    try {
      await actualizarPerfil(datos)
      setAviso({ tipo: 'ok', texto: 'Perfil actualizado correctamente.' })
      setPassword('')
      setConfirmPassword('')
    } catch (err) {
      setAviso({ tipo: 'error', texto: err.message })
    } finally {
      setGuardando(false)
    }
  }

  async function borrar() {
    setErrorEliminar('')
    setEliminando(true)
    try {
      await eliminarPerfil()
      cerrarSesion()
      navigate('/login')
    } catch (err) {
      setErrorEliminar(err.message)
      setEliminando(false)
    }
  }

  return (
    <div className="ajustes">
      <h1 className="titulo">Mi perfil</h1>

      <section className="tarjeta seccion-ajustes">
        <h2>Apariencia</h2>
        <p className="sub">Elige cómo quieres ver la aplicación.</p>
        <div className="selector-tema" role="group" aria-label="Tema">
          <button
            type="button"
            className={tema === 'light' ? 'opcion-tema activo' : 'opcion-tema'}
            onClick={() => cambiarTema('light')}
          >
            Claro
          </button>
          <button
            type="button"
            className={tema === 'dark' ? 'opcion-tema activo' : 'opcion-tema'}
            onClick={() => cambiarTema('dark')}
          >
            Oscuro
          </button>
        </div>
      </section>

      <form className="tarjeta seccion-ajustes" onSubmit={guardar}>
        <h2>Datos de la cuenta</h2>
        <p className="sub">Actualiza tu correo o cambia tu contraseña. Deja la contraseña vacía si no quieres cambiarla.</p>

        <label>
          Correo
          <input
            type="email"
            value={email}
            onChange={(e) => { setEmail(e.target.value); setAviso(null) }}
            placeholder="tucorreo@ejemplo.com"
          />
        </label>

        <label>
          Nueva contraseña
          <div className="campo-password">
            <input
              type={mostrar ? 'text' : 'password'}
              value={password}
              onChange={(e) => { setPassword(e.target.value); setAviso(null) }}
              autoComplete="new-password"
            />
            <button
              type="button"
              className="boton-ver-password"
              onClick={() => setMostrar(!mostrar)}
            >
              {mostrar ? 'Ocultar' : 'Mostrar'}
            </button>
          </div>
        </label>

        {quiereCambiarPassword && (
          <>
            <ul className="requisitos-ajustes">
              {requisitos.map((r) => (
                <li key={r.texto} className={r.cumplido ? 'req ok' : 'req'}>
                  {r.cumplido ? '✓' : '○'} {r.texto}
                </li>
              ))}
            </ul>

            <label>
              Confirmar nueva contraseña
              <input
                type={mostrar ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => { setConfirmPassword(e.target.value); setAviso(null) }}
                autoComplete="new-password"
              />
            </label>

            {confirmPassword.length > 0 && (
              <p className={coinciden ? 'req ok' : 'req mal'}>
                {coinciden ? '✓ Las contraseñas coinciden' : '✗ Las contraseñas no coinciden'}
              </p>
            )}
          </>
        )}

        {aviso && (
          <p className={`aviso ${aviso.tipo}`} role="alert">{aviso.texto}</p>
        )}

        <button type="submit" className="boton" disabled={guardando}>
          {guardando ? 'Guardando...' : 'Guardar cambios'}
        </button>
      </form>

      <section className="tarjeta seccion-ajustes zona-peligro">
        <h2>Eliminar perfil</h2>
        <p className="sub">
          Esta acción borra tu cuenta y no se puede deshacer.
        </p>

        {!verEliminar ? (
          <button type="button" className="boton-peligro" onClick={() => setVerEliminar(true)}>
            Eliminar mi perfil
          </button>
        ) : (
          <div className="confirmar-eliminar">
            <label>
              Escribe ELIMINAR para confirmar
              <input
                type="text"
                value={textoConfirmar}
                onChange={(e) => setTextoConfirmar(e.target.value)}
              />
            </label>

            {errorEliminar && <p className="aviso error" role="alert">{errorEliminar}</p>}

            <div className="fila-botones">
              <button
                type="button"
                className="boton-peligro"
                disabled={textoConfirmar !== 'ELIMINAR' || eliminando}
                onClick={borrar}
              >
                {eliminando ? 'Eliminando...' : 'Sí, eliminar definitivamente'}
              </button>
              <button
                type="button"
                className="link"
                onClick={() => { setVerEliminar(false); setTextoConfirmar(''); setErrorEliminar('') }}
              >
                Cancelar
              </button>
            </div>
          </div>
        )}
      </section>
    </div>
  )
}
