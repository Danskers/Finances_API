import { useEffect, useState } from 'react'
import { api } from '../services/api.js'
import { formatoCOP, formatoCOPCompacto } from '../utils/formatoMoneda.js'
import './Graficas.css'

const COLORES = ['#6d7be0', '#e4c766', '#fda4af', '#7dd3fc', '#4ade80', '#c084fc']

// Suma los gastos y deudas por categoría (las 5 mayores y el resto como "Otras").
function agruparPorCategoria(transacciones) {
  const mapa = {}
  for (const t of transacciones) {
    if (t.tipo !== 'gasto' && t.tipo !== 'deuda') continue
    const categoria = t.categoria || 'Sin categoría'
    mapa[categoria] = (mapa[categoria] || 0) + Number(t.monto || 0)
  }
  const ordenado = Object.entries(mapa)
    .map(([categoria, total]) => ({ categoria, total }))
    .sort((a, b) => b.total - a.total)

  if (ordenado.length <= 6) return ordenado
  const resto = ordenado.slice(5).reduce((suma, d) => suma + d.total, 0)
  return [...ordenado.slice(0, 5), { categoria: 'Otras', total: resto }]
}

function BarrasResumen({ resumen }) {
  const filas = [
    { nombre: 'Ingresos', valor: resumen.total_ingresos, clase: 'ingreso' },
    { nombre: 'Gastos', valor: resumen.total_gastos, clase: 'gasto' },
    { nombre: 'Límite de gasto', valor: resumen.monto_limite, clase: 'limite' },
  ]
  const maximo = Math.max(...filas.map((f) => Number(f.valor) || 0), 1)

  return (
    <div>
      {filas.map((f) => (
        <div className="grafica-fila" key={f.nombre}>
          <div className="grafica-fila-texto">
            <span>{f.nombre}</span>
            <span>{formatoCOP(f.valor)}</span>
          </div>
          <div className="grafica-pista">
            <div
              className={`grafica-relleno ${f.clase}`}
              style={{ width: `${((Number(f.valor) || 0) / maximo) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}

function Dona({ datos }) {
  const total = datos.reduce((suma, d) => suma + d.total, 0)
  if (total <= 0) {
    return <p className="grafica-vacia">Aún no tienes gastos este mes.</p>
  }

  const radio = 60
  const circunferencia = 2 * Math.PI * radio
  let acumulado = 0
  const segmentos = datos.map((d, i) => {
    const largo = (d.total / total) * circunferencia
    const segmento = {
      ...d,
      largo,
      desplazamiento: -acumulado,
      color: COLORES[i % COLORES.length],
      porcentaje: Math.round((d.total / total) * 100),
    }
    acumulado += largo
    return segmento
  })

  return (
    <div className="dona-contenedor">
      <svg viewBox="0 0 160 160" className="dona" role="img" aria-label="Gastos por categoría">
        <g transform="rotate(-90 80 80)">
          <circle cx="80" cy="80" r={radio} fill="none" stroke="var(--barra)" strokeWidth="28" />
          {segmentos.map((s) => (
            <circle
              key={s.categoria}
              cx="80"
              cy="80"
              r={radio}
              fill="none"
              stroke={s.color}
              strokeWidth="28"
              strokeDasharray={`${s.largo} ${circunferencia - s.largo}`}
              strokeDashoffset={s.desplazamiento}
            />
          ))}
        </g>
        <text x="80" y="76" textAnchor="middle" className="dona-etiqueta">Gastos</text>
        <text x="80" y="96" textAnchor="middle" className="dona-total">{formatoCOPCompacto(total)}</text>
      </svg>

      <ul className="leyenda">
        {segmentos.map((s) => (
          <li key={s.categoria}>
            <span className="leyenda-color" style={{ background: s.color }} />
            <span className="leyenda-nombre">{s.categoria}</span>
            <span className="leyenda-valor">{formatoCOP(s.total)}</span>
            <span className="leyenda-porcentaje">{s.porcentaje}%</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function Graficas() {
  const [resumen, setResumen] = useState(null)
  const [transacciones, setTransacciones] = useState([])
  const [error, setError] = useState(false)

  useEffect(() => {
    let activo = true
    Promise.all([api('/resumen'), api('/transacciones')])
      .then(([r, t]) => {
        if (!activo) return
        setResumen(r)
        setTransacciones(Array.isArray(t) ? t : [])
      })
      .catch(() => {
        if (activo) setError(true)
      })
    return () => { activo = false }
  }, [])

  return (
    <section className="graficas">
      <div className="graficas-cabecera">
        <h2>Gráficas del mes</h2>
        <p className="sub">Valores en pesos colombianos (COP).</p>
      </div>

      {error && (
        <div className="tarjeta">
          <p className="grafica-vacia">No se pudieron cargar las gráficas.</p>
        </div>
      )}

      {!error && !resumen && (
        <div className="tarjeta">
          <p className="grafica-vacia">Cargando gráficas...</p>
        </div>
      )}

      {!error && resumen && (
        <div className="graficas-rejilla">
          <div className="tarjeta">
            <h2>Ingresos, gastos y límite</h2>
            <BarrasResumen resumen={resumen} />
          </div>
          <div className="tarjeta">
            <h2>Gastos por categoría</h2>
            <Dona datos={agruparPorCategoria(transacciones)} />
          </div>
        </div>
      )}
    </section>
  )
}
