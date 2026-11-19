
import { useEffect, useState } from 'react'
import {
  fijarLimite,
  obtenerResumen,
  listarTransacciones,
} from '../services/transactionService.js'
import { formatear } from '../components/AccountCard.jsx'

const mesActual = () => {
  const fecha = new Date()
  return `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`
}

const obtenerUltimosMeses = () => {
  const meses = []
  const hoy = new Date()

  for (let i = 5; i >= 0; i--) {
    const fecha = new Date(hoy.getFullYear(), hoy.getMonth() - i, 1)
    const clave = `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`

    meses.push({
      clave,
      nombre: fecha.toLocaleDateString('es-CO', { month: 'short' }),
    })
  }

  return meses
}

export default function Dashboard() {
  const [resumen, setResumen] = useState(null)
  const [transacciones, setTransacciones] = useState([])
  const [limite, setLimite] = useState('')
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(true)

  async function cargar() {
    try {
      setError('')

      const [datosResumen, datosTransacciones] = await Promise.all([
        obtenerResumen(mesActual()),
        listarTransacciones(),
      ])

      setResumen(datosResumen)
      setTransacciones(datosTransacciones)
    } catch (err) {
      setError(err.message)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar()
  }, [])

  async function guardarLimite(e) {
    e.preventDefault()

    try {
      await fijarLimite(mesActual(), Number(limite))
      setLimite('')
      await cargar()
    } catch (err) {
      setError(err.message)
    }
  }

  if (cargando) {
    return <p className="claro">Cargando estadísticas...</p>
  }

  if (error) {
    return <p className="error" role="alert">{error}</p>
  }

  if (!resumen) return null

  // Transacciones correspondientes al mes actual.
  const movimientosMes = transacciones.filter(tx =>
    String(tx.fecha ?? '').slice(0, 7) === mesActual()
  )

  const gastosMes = movimientosMes.filter(tx => tx.tipo === 'gasto')
  const ingresosMes = movimientosMes.filter(tx => tx.tipo === 'ingreso')

  const totalGastos = gastosMes.reduce(
    (total, tx) => total + Number(tx.monto || 0), 0
  )

  const promedioGastos = gastosMes.length
    ? totalGastos / gastosMes.length
    : 0

  const gastoMayor = gastosMes.reduce(
    (mayor, tx) => Math.max(mayor, Number(tx.monto || 0)), 0
  )

  const usado = resumen.monto_limite > 0
    ? Math.min(100, (resumen.total_gastos / resumen.monto_limite) * 100)
    : 0

  // Agrupar gastos por categoría.
  const categorias = {}

  gastosMes.forEach(tx => {
    const categoria = tx.categoria || 'Sin categoría'
    categorias[categoria] = (categorias[categoria] || 0) + Number(tx.monto || 0)
  })

  const gastosPorCategoria = Object.entries(categorias)
    .map(([nombre, monto]) => ({ nombre, monto }))
    .sort((a, b) => b.monto - a.monto)

  const mayorCategoria = Math.max(
    ...gastosPorCategoria.map(c => c.monto),
    1
  )

  // Agrupar ingresos y gastos de los últimos seis meses.
  const meses = obtenerUltimosMeses()

  const datosMensuales = meses.map(mes => {
    const movimientos = transacciones.filter(
      tx => String(tx.fecha ?? '').slice(0, 7) === mes.clave
    )

    return {
      ...mes,
      ingresos: movimientos
        .filter(tx => tx.tipo === 'ingreso')
        .reduce((suma, tx) => suma + Number(tx.monto || 0), 0),
      gastos: movimientos
        .filter(tx => tx.tipo === 'gasto')
        .reduce((suma, tx) => suma + Number(tx.monto || 0), 0),
    }
  })

  const mayorValorMensual = Math.max(
    ...datosMensuales.flatMap(m => [m.ingresos, m.gastos]),
    1
  )

  return (
    <>
      <h1 className="titulo">Resumen de {resumen.mes}</h1>

      {/* INDICADORES PRINCIPALES */}
      <div className="rejilla-3">
        <div className="tarjeta">
          <p className="etq">Ingresos</p>
          <p className="monto pos">{formatear(resumen.total_ingresos)}</p>
        </div>

        <div className="tarjeta">
          <p className="etq">Gastos</p>
          <p className="monto neg">{formatear(resumen.total_gastos)}</p>
        </div>

        <div className="tarjeta">
          <p className="etq">Disponible</p>
          <p className="monto">{formatear(resumen.disponible)}</p>
        </div>
      </div>

      {/* ESTADÍSTICAS ADICIONALES */}
      <h2 className="titulo">Estadísticas del mes</h2>

      <div className="rejilla-3">
        <div className="tarjeta">
          <p className="etq">Movimientos registrados</p>
          <p className="monto">{movimientosMes.length}</p>
        </div>

        <div className="tarjeta">
          <p className="etq">Promedio por gasto</p>
          <p className="monto">{formatear(promedioGastos)}</p>
        </div>

        <div className="tarjeta">
          <p className="etq">Gasto más alto</p>
          <p className="monto neg">{formatear(gastoMayor)}</p>
        </div>
      </div>

      {/* LÍMITE DE GASTOS */}
      <section className="tarjeta bloque">
        <h2>Límite de gasto del mes</h2>

        <p className="sub">
          Gastado {formatear(resumen.total_gastos)} de {formatear(resumen.monto_limite)}
        </p>

        <div className="barra">
          <div
            className="barra-relleno"
            style={{ width: `${usado}%` }}
          />
        </div>

        <p className="sub">{usado.toFixed(1)}% del límite utilizado</p>

        <form className="fila" onSubmit={guardarLimite}>
          <input
            type="number"
            min="0"
            placeholder="Nuevo límite"
            value={limite}
            onChange={(e) => setLimite(e.target.value)}
            required
          />

          <button type="submit" className="boton">
            Guardar límite
          </button>
        </form>
      </section>

      {/* GRÁFICO DE INGRESOS Y GASTOS */}
      <section className="tarjeta bloque">
        <h2>Ingresos vs. gastos</h2>
        <p className="sub">Comparación de los últimos seis meses</p>

        <div className="grafico-meses">
          {datosMensuales.map(mes => (
            <div className="columna-mes" key={mes.clave}>
              <div className="barras-mes">
                <div
                  className="barra-grafico ingreso-grafico"
                  title={`Ingresos: ${formatear(mes.ingresos)}`}
                  style={{
                    height: `${Math.max(2, (mes.ingresos / mayorValorMensual) * 100)}%`,
                  }}
                />

                <div
                  className="barra-grafico gasto-grafico"
                  title={`Gastos: ${formatear(mes.gastos)}`}
                  style={{
                    height: `${Math.max(2, (mes.gastos / mayorValorMensual) * 100)}%`,
                  }}
                />
              </div>

              <span>{mes.nombre}</span>
            </div>
          ))}
        </div>

        <div className="leyenda-grafico">
          <span><i className="punto-ingreso" /> Ingresos</span>
          <span><i className="punto-gasto" /> Gastos</span>
        </div>
      </section>

      {/* DISTRIBUCIÓN POR CATEGORÍAS */}
      <section className="tarjeta bloque">
        <h2>Gastos por categoría</h2>
        <p className="sub">Distribución de tus gastos del mes actual</p>

        {gastosPorCategoria.length === 0 ? (
          <p className="sub">Todavía no hay gastos registrados este mes.</p>
        ) : (
          <div className="categorias-grafico">
            {gastosPorCategoria.map(categoria => (
              <div className="categoria-estadistica" key={categoria.nombre}>
                <div className="categoria-info">
                  <span>{categoria.nombre}</span>
                  <strong>{formatear(categoria.monto)}</strong>
                </div>

                <div className="barra">
                  <div
                    className="barra-relleno"
                    style={{
                      width: `${(categoria.monto / mayorCategoria) * 100}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </>
  )
}
