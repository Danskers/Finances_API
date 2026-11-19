import { useEffect, useState } from 'react'
import AccountCard from '../components/AccountCard.jsx'
import { crearCuenta, eliminarCuenta, listarCuentas, renombrarCuenta } from '../services/accountService.js'
import { obtenerBalances } from '../services/transactionService.js'

export default function Accounts() {
  const [cuentas, setCuentas] = useState([])
  const [balances, setBalances] = useState({})
  const [nombre, setNombre] = useState('')
  const [error, setError] = useState('')

  async function cargar() {
    try {
      setCuentas(await listarCuentas())
      const b = await obtenerBalances().catch(() => [])
      setBalances(Object.fromEntries(b.map((x) => [x.cuenta_id, x.balance])))
    } catch (err) {
      setError(err.message)
    }
  }
  useEffect(() => { cargar() }, [])

  async function crear(e) {
    e.preventDefault()
    try {
      await crearCuenta(nombre)
      setNombre('')
      cargar()
    } catch (err) {
      setError(err.message)
    }
  }
  async function renombrar(c) {
    const nuevo = window.prompt('Nuevo nombre de la cuenta', c.nombre)
    if (!nuevo) return
    try { await renombrarCuenta(c.id, nuevo); cargar() } catch (err) { setError(err.message) }
  }
  async function eliminar(c) {
    if (!window.confirm(`¿Eliminar la cuenta "${c.nombre}"?`)) return
    try { await eliminarCuenta(c.id); cargar() } catch (err) { setError(err.message) }
  }

  return (
    <>
      <h1 className="titulo">Mis cuentas</h1>
      {error && <p className="error" role="alert">{error}</p>}
      <form className="fila bloque" onSubmit={crear}>
        <input placeholder="Nombre de la cuenta, por ejemplo Ahorros" value={nombre} onChange={(e) => setNombre(e.target.value)} required />
        <button type="submit" className="boton">Crear cuenta</button>
      </form>
      {cuentas.length === 0 && <p className="claro">Aún no tienes cuentas. Crea la primera para registrar movimientos.</p>}
      <div className="rejilla-3">
        {cuentas.map((c, i) => (
          <AccountCard key={c.id} cuenta={c} color={i} balance={balances[c.id]} onRenombrar={renombrar} onEliminar={eliminar} />
        ))}
      </div>
    </>
  )
}
