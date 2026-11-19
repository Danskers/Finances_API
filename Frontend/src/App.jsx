
import './theme.js'
import { Link, Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext.jsx'
import Sidebar from './components/Sidebar.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Accounts from './pages/Accounts.jsx'
import Transactions from './pages/Transactions.jsx'
import Settings from './pages/Settings.jsx'

// Footer general de la aplicación.
function Footer() {
  return (
    <footer className="footer">
      <div className="footer-superior">
        <div className="footer-marca">
          <h2>KaibaCorp</h2>
          <p>
            Administra tus finanzas personales de manera
            sencilla, organizada e inteligente.
          </p>
        </div>

        <nav className="footer-enlaces" aria-label="Navegación del pie de página">
          <Link to="/">Resumen</Link>
          <Link to="/cuentas">Cuentas</Link>
          <Link to="/transacciones">Transacciones</Link>
          <Link to="/perfil">Mi perfil</Link>
        </nav>
      </div>

      <div className="footer-inferior">
        <span>© {new Date().getFullYear()} KaibaCorp.</span>
        <span>Gestiona tu dinero, construye tu futuro.</span>
      </div>
    </footer>
  )
}

// Rutas privadas: sin token se redirige al login.
function Privado() {
  const { token } = useAuth()

  if (!token) return <Navigate to="/login" replace />

  return (
    <div className="app-shell">
      <Sidebar />

      <div className="contenido">
        <main className="contenido-principal">
          <Outlet />
        </main>

        <Footer />
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/registro" element={<Register />} />

      <Route element={<Privado />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/cuentas" element={<Accounts />} />
        <Route path="/transacciones" element={<Transactions />} />
        <Route path="/perfil" element={<Settings />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
