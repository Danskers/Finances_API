
import { NavLink } from 'react-router-dom'
import logo from '../assets/kaibacorp-logo.png'
import { useAuth } from '../context/AuthContext.jsx'
import { useTema } from '../theme.js'
import './Sidebar.css'

const enlaces = [
  { to: '/', texto: 'Resumen' },
  { to: '/cuentas', texto: 'Cuentas' },
  { to: '/transacciones', texto: 'Transacciones' },
  { to: '/perfil', texto: 'Mi perfil' },
]

export default function Sidebar() {
  const { cerrarSesion } = useAuth()
  const { esOscuro, alternar } = useTema()

  return (
    <aside className="sidebar">

      <div className="sidebar-marca">
        <img
          src={logo}
          alt="KaibaCorp"
          className="sidebar-logo"
        />
      </div>

      <nav className="sidebar-nav" aria-label="Navegación principal">
        {enlaces.map((e) => (
          <NavLink
            key={e.to}
            to={e.to}
            end={e.to === '/'}
            className={({ isActive }) => isActive ? 'activo' : ''}
          >
            {e.texto}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-acciones">
        <button
          type="button"
          className="link-salir link-tema"
          onClick={alternar}
        >
          {esOscuro ? '☀️ Modo claro' : '🌙 Modo oscuro'}
        </button>

        <button
          type="button"
          className="link-salir"
          onClick={cerrarSesion}
        >
          ↪ Cerrar sesión
        </button>
      </div>

      <p className="sidebar-moneda">Moneda: peso colombiano (COP)</p>
    </aside>
  )
}
