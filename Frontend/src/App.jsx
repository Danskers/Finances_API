import './theme.js'
import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext.jsx'
import Sidebar from './components/Sidebar.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Accounts from './pages/Accounts.jsx'
import Transactions from './pages/Transactions.jsx'

// Rutas privadas: sin token se redirige al login.
function Privado() {
  const { token } = useAuth()
  if (!token) return <Navigate to="/login" replace />
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="contenido"><Outlet /></main>
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
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
