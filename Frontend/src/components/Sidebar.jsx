import { NavLink } from 'react-router-dom'
import logo from '../assets/kaibacorp-logo.png'
import { useAuth } from '../context/AuthContext.jsx'
import './Sidebar.css'

const enlaces = [
  { to: '/', texto: 'Resumen' },
  { to: '/cuentas', texto: 'Cuentas' },
  { to: '/transacciones', texto: 'Transacciones' },
  { to: '/perfil', texto: 'Mi perfil' },
]

export default function Sidebar() {
  const { cerrarSesion } = useAuth()

  return (
    <aside className="sidebar">
      <img src={logo} alt="KaibaCorp" className="sidebar-logo" />

      <nav>
        {enlaces.map((e) => (
          <NavLink key={e.to} to={e.to} end={e.to === '/'} className={({ isActive }) => (isActive ? 'activo' : '')}>
            {e.texto}
          </NavLink>
        ))}
      </nav>

      <button type="button" className="sidebar-salir" onClick={cerrarSesion}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
          <polyline points="16 17 21 12 16 7" />
          <line x1="21" y1="12" x2="9" y2="12" />
        </svg>
        Cerrar sesión
      </button>

      <p className="sidebar-moneda">Moneda: peso colombiano (COP)</p>
    </aside>
  )
}
