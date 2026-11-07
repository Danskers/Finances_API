import { NavLink } from 'react-router-dom'
import logo from '../assets/kaibacorp-logo.png'
import { useAuth } from '../context/AuthContext.jsx'

const enlaces = [
  { to: '/', texto: 'Resumen' },
  { to: '/cuentas', texto: 'Cuentas' },
  { to: '/transacciones', texto: 'Transacciones' },
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
      <button type="button" className="link-salir" onClick={cerrarSesion}>Cerrar sesión</button>
    </aside>
  )
}
