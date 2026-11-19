import { useEffect, useState } from 'react'
import TransactionCard from '../components/TransactionCard.jsx'
import { listarCuentas } from '../services/accountService.js'
import { crearTransaccion, eliminarTransaccion, listarTransacciones } from '../services/transactionService.js'
import { subirFactura } from '../services/storageService.js'

const vacio = { monto: '', tipo: 'gasto', categoria: '', cuenta_id: '' }

export default function Transactions() {
  const [txs, setTxs] = useState([])
  const [cuentas, setCuentas] = useState([])
  const [form, setForm] = useState(vacio)
  const [factura, setFactura] = useState(null)
  const [error, setError] = useState('')

  async function cargar() {
    try {
      const [t, c] = await Promise.all([listarTransacciones(), listarCuentas()])
      setTxs(t)
      setCuentas(c)
    } catch (err) {
      setError(err.message)
    }
  }
  useEffect(() => { cargar() }, [])

  const cambiar = (campo) => (e) => setForm({ ...form, [campo]: e.target.value })

  async function registrar(e) {
    e.preventDefault()
    setError('')
    try {
      const factura_url = factura ? (await subirFactura(factura)).url : null
      await crearTransaccion({ ...form, monto: Number(form.monto), cuenta_id: Number(form.cuenta_id), factura_url })
      setForm(vacio)
      setFactura(null)
      cargar()
    } catch (err) {
      setError(err.message)
    }
  }
  async function borrar(tx) {
    try { await eliminarTransaccion(tx.id); cargar() } catch (err) { setError(err.message) }
  }
  const nombreCuenta = (id) => cuentas.find((c) => c.id === id)?.nombre ?? '—'

  return (
    <>
      <h1 className="titulo">Transacciones</h1>
      {error && <p className="error" role="alert">{error}</p>}
      <div className="dos-col">
        <form className="tarjeta" onSubmit={registrar}>
          <h2>Nuevo movimiento</h2>
          <label>Monto<input type="number" min="1" value={form.monto} onChange={cambiar('monto')} required /></label>
          <label>Tipo
            <select value={form.tipo} onChange={cambiar('tipo')}>
              <option value="gasto">Gasto</option><option value="ingreso">Ingreso</option><option value="deuda">Deuda</option>
            </select>
          </label>
          <label>Categoría<input value={form.categoria} onChange={cambiar('categoria')} required /></label>
          <label>Cuenta
            <select value={form.cuenta_id} onChange={cambiar('cuenta_id')} required>
              <option value="" disabled>Elige una cuenta</option>
              {cuentas.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
            </select>
          </label>
          <label>Factura (opcional)<input type="file" accept="image/*,application/pdf" onChange={(e) => setFactura(e.target.files[0] ?? null)} /></label>
          <button type="submit" className="boton">Registrar movimiento</button>
        </form>
        <section className="tarjeta">
          <h2>Historial</h2>
          {txs.length === 0 ? <p className="sub">Todavía no hay movimientos.</p> : (
            <div className="tabla-scroll">
              <table>
                <thead><tr><th>Fecha</th><th>Categoría</th><th>Cuenta</th><th>Tipo</th><th className="derecha">Monto</th><th /></tr></thead>
                <tbody>{txs.map((t) => <TransactionCard key={t.id} tx={t} nombreCuenta={nombreCuenta(t.cuenta_id)} onEliminar={borrar} />)}</tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </>
  )
}
