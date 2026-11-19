import { useEffect, useState } from 'react'
import { fijarLimite, obtenerResumen } from '../services/transactionService.js'
import { formatear } from '../components/AccountCard.jsx'

const mesActual = () => new Date().toISOString().slice(0, 7)

export default function Dashboard() {
  const [resumen, setResumen] = useState(null)
  const [limite, setLimite] = useState('')
  const [error, setError] = useState('')

  async function cargar() {
    try {
      setResumen(await obtenerResumen(mesActual()))
    } catch (err) {
      setError(err.message)
    }
  }
  useEffect(() => { cargar() }, [])

  async function guardarLimite(e) {
    e.preventDefault()
    try {
      await fijarLimite(mesActual(), Number(limite))
      setLimite('')
      cargar()
    } catch (err) {
      setError(err.message)
    }
  }

  if (error) return <p className="error" role="alert">{error}</p>
  if (!resumen) return <p className="claro">Cargando resumen…</p>

  const usado = resumen.monto_limite > 0 ? Math.min(100, (resumen.total_gastos / resumen.monto_limite) * 100) : 0

  return (
    <>
      <h1 className="titulo">Resumen de {resumen.mes}</h1>
      <div className="rejilla-3">
        <div className="tarjeta"><p className="etq">Ingresos</p><p className="monto pos">{formatear(resumen.total_ingresos)}</p></div>
        <div className="tarjeta"><p className="etq">Gastos</p><p className="monto neg">{formatear(resumen.total_gastos)}</p></div>
        <div className="tarjeta"><p className="etq">Disponible</p><p className="monto">{formatear(resumen.disponible)}</p></div>
      </div>
      <section className="tarjeta bloque">
        <h2>Límite de gasto del mes</h2>
        <p className="sub">Gastado {formatear(resumen.total_gastos)} de {formatear(resumen.monto_limite)}</p>
        <div className="barra"><div className="barra-relleno" style={{ width: `${usado}%` }} /></div>
        <form className="fila" onSubmit={guardarLimite}>
          <input type="number" min="0" placeholder="Nuevo límite" value={limite} onChange={(e) => setLimite(e.target.value)} required />
          <button type="submit" className="boton">Guardar límite</button>
        </form>
      </section>
    </>
  )
}
