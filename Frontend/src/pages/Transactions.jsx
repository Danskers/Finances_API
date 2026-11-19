
import { useEffect, useMemo, useState } from 'react'
import TransactionCard from '../components/TransactionCard.jsx'
import { listarCuentas } from '../services/accountService.js'
import {
  crearTransaccion,
  eliminarTransaccion,
  listarTransacciones,
} from '../services/transactionService.js'
import {
  subirFactura,
  esperarSubida,
} from '../services/storageService.js'

const vacio = {
  monto: '',
  tipo: 'gasto',
  categoria: '',
  cuenta_id: '',
}

const FILTROS_INICIALES = {
  fechaDesde: '',
  fechaHasta: '',
  montoMin: '',
  montoMax: '',
  categoria: '',
  tipo: '',
  cuenta_id: '',
}

const CATEGORIAS = {
  gasto: [
    'Alimentación',
    'Transporte',
    'Vivienda',
    'Salud',
    'Educación',
    'Entretenimiento',
    'Compras',
    'Servicios',
    'Otros',
  ],
  ingreso: [
    'Salario',
    'Freelance',
    'Inversiones',
    'Ventas',
    'Regalos',
    'Otros',
  ],
  deuda: [
    'Préstamo',
    'Tarjeta de crédito',
    'Crédito educativo',
    'Otros',
  ],
}

const CATEGORIA_PERSONALIZADA = '__personalizada__'

export default function Transactions() {
  const [txs, setTxs] = useState([])
  const [cuentas, setCuentas] = useState([])
  const [form, setForm] = useState(vacio)
  const [factura, setFactura] = useState(null)
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)
  const [categoriaPersonalizada, setCategoriaPersonalizada] = useState(false)

  // Estados de los filtros
  const [mostrarFiltros, setMostrarFiltros] = useState(false)
  const [filtros, setFiltros] = useState(FILTROS_INICIALES)

  async function cargar() {
    try {
      const [t, c] = await Promise.all([
        listarTransacciones(),
        listarCuentas(),
      ])

      setTxs(t)
      setCuentas(c)
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    cargar()
  }, [])

  const cambiar = (campo) => (e) => {
    setForm(prev => ({
      ...prev,
      [campo]: e.target.value,
    }))
  }

  function cambiarTipo(e) {
    const tipo = e.target.value

    setForm(prev => ({
      ...prev,
      tipo,
      categoria: '',
    }))

    setCategoriaPersonalizada(false)
  }

  function cambiarCategoria(e) {
    const valor = e.target.value

    if (valor === CATEGORIA_PERSONALIZADA) {
      setCategoriaPersonalizada(true)

      setForm(prev => ({
        ...prev,
        categoria: '',
      }))
    } else {
      setCategoriaPersonalizada(false)

      setForm(prev => ({
        ...prev,
        categoria: valor,
      }))
    }
  }

  // Actualiza un filtro sin modificar los demás.
  function cambiarFiltro(campo, valor) {
    setFiltros(prev => ({
      ...prev,
      [campo]: valor,
    }))
  }

  // Categorías existentes en el historial.
  // Así también aparecen las categorías personalizadas.
  const categoriasDisponibles = useMemo(() => {
    return [...new Set(
      txs
        .map(tx => tx.categoria)
        .filter(Boolean)
    )].sort((a, b) => a.localeCompare(b))
  }, [txs])

  // Aplicación de los filtros sobre las transacciones cargadas.
  const transaccionesFiltradas = useMemo(() => {
    return txs.filter(tx => {
      const monto = Number(tx.monto)

      // La fecha se compara en formato YYYY-MM-DD.
      const fecha = String(tx.fecha ?? '').slice(0, 10)

      if (filtros.fechaDesde && fecha < filtros.fechaDesde) {
        return false
      }

      if (filtros.fechaHasta && fecha > filtros.fechaHasta) {
        return false
      }

      if (
        filtros.montoMin !== '' &&
        monto < Number(filtros.montoMin)
      ) {
        return false
      }

      if (
        filtros.montoMax !== '' &&
        monto > Number(filtros.montoMax)
      ) {
        return false
      }

      if (
        filtros.categoria &&
        tx.categoria !== filtros.categoria
      ) {
        return false
      }

      if (
        filtros.tipo &&
        tx.tipo !== filtros.tipo
      ) {
        return false
      }

      if (
        filtros.cuenta_id &&
        String(tx.cuenta_id) !== filtros.cuenta_id
      ) {
        return false
      }

      return true
    })
  }, [txs, filtros])

  function limpiarFiltros() {
    setFiltros(FILTROS_INICIALES)
  }

  async function registrar(e) {
    e.preventDefault()
    setError('')
    setEnviando(true)

    try {
      let factura_url = null

      // Si se seleccionó una factura, primero se procesa
      // mediante Storage Service y Celery.
      if (factura) {
        const subida = await subirFactura(factura)
        factura_url = await esperarSubida(subida.task_id)
      }

      // Cuando tenemos la URL, registramos la transacción.
      await crearTransaccion({
        ...form,
        monto: Number(form.monto),
        cuenta_id: Number(form.cuenta_id),
        factura_url,
      })

      // Limpiamos el formulario.
      setForm(vacio)
      setFactura(null)
      setCategoriaPersonalizada(false)

      // Actualizamos el historial.
      await cargar()

    } catch (err) {
      setError(err.message)
    } finally {
      setEnviando(false)
    }
  }

  async function borrar(tx) {
    try {
      await eliminarTransaccion(tx.id)
      await cargar()
    } catch (err) {
      setError(err.message)
    }
  }

  const nombreCuenta = (id) =>
    cuentas.find(c => c.id === id)?.nombre ?? '—'

  const filtrosActivos = Object.values(filtros).some(valor => valor !== '')

  return (
    <>
      <h1 className="titulo">Transacciones</h1>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      <div className="dos-col">

        {/* FORMULARIO DE REGISTRO */}
        <form className="tarjeta" onSubmit={registrar}>
          <h2>Nuevo movimiento</h2>

          <label>
            Monto
            <input
              type="number"
              min="1"
              value={form.monto}
              onChange={cambiar('monto')}
              required
              disabled={enviando}
            />
          </label>

          <label>
            Tipo
            <select
              value={form.tipo}
              onChange={cambiarTipo}
              disabled={enviando}
            >
              <option value="gasto">Gasto</option>
              <option value="ingreso">Ingreso</option>
              <option value="deuda">Deuda</option>
            </select>
          </label>

          {/* SELECTOR DE CATEGORÍAS */}
          <label>
            Categoría
            <select
              value={
                categoriaPersonalizada
                  ? CATEGORIA_PERSONALIZADA
                  : form.categoria
              }
              onChange={cambiarCategoria}
              required
              disabled={enviando}
            >
              <option value="" disabled>
                Selecciona una categoría
              </option>

              {CATEGORIAS[form.tipo].map(categoria => (
                <option key={categoria} value={categoria}>
                  {categoria}
                </option>
              ))}

              <option value={CATEGORIA_PERSONALIZADA}>
                Personalizada
              </option>
            </select>
          </label>

          {/* CATEGORÍA PERSONALIZADA */}
          {categoriaPersonalizada && (
            <label>
              Nombre de la categoría
              <input
                type="text"
                placeholder="Ej. Mascotas, Viajes, Gimnasio..."
                value={form.categoria}
                onChange={cambiar('categoria')}
                required
                disabled={enviando}
              />
            </label>
          )}

          <label>
            Cuenta
            <select
              value={form.cuenta_id}
              onChange={cambiar('cuenta_id')}
              required
              disabled={enviando}
            >
              <option value="" disabled>
                Elige una cuenta
              </option>

              {cuentas.map(c => (
                <option key={c.id} value={c.id}>
                  {c.nombre}
                </option>
              ))}
            </select>
          </label>

          <label>
            Factura (opcional)
            <input
              type="file"
              accept="image/*,application/pdf"
              onChange={e => setFactura(e.target.files[0] ?? null)}
              disabled={enviando}
            />
          </label>

          <button
            type="submit"
            className="boton"
            disabled={enviando}
          >
            {enviando
              ? 'Procesando movimiento...'
              : 'Registrar movimiento'}
          </button>
        </form>

        {/* HISTORIAL DE TRANSACCIONES */}
        <section className="tarjeta">
          <h2>Historial</h2>

          {/* BOTÓN PARA MOSTRAR U OCULTAR FILTROS */}
          <button
            type="button"
            className="boton"
            onClick={() => setMostrarFiltros(prev => !prev)}
          >
            {mostrarFiltros ? 'Ocultar filtros' : 'Filtrar movimientos'}
            {filtrosActivos ? ' •' : ''}
          </button>

          {/* PANEL DE FILTROS */}
          {mostrarFiltros && (
            <div
              className="panel-filtros"
              style={{
                marginTop: '20px',
                marginBottom: '20px',
                padding: '18px',
                border: '1px solid var(--borde)',
                borderRadius: '12px',
              }}
            >
              <h3>Buscar movimientos</h3>

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
                  gap: '15px',
                }}
              >
                <label>
                  Fecha desde
                  <input
                    type="date"
                    value={filtros.fechaDesde}
                    onChange={e => cambiarFiltro('fechaDesde', e.target.value)}
                  />
                </label>

                <label>
                  Fecha hasta
                  <input
                    type="date"
                    value={filtros.fechaHasta}
                    min={filtros.fechaDesde || undefined}
                    onChange={e => cambiarFiltro('fechaHasta', e.target.value)}
                  />
                </label>

                <label>
                  Monto mínimo
                  <input
                    type="number"
                    min="0"
                    placeholder="Ej. 50000"
                    value={filtros.montoMin}
                    onChange={e => cambiarFiltro('montoMin', e.target.value)}
                  />
                </label>

                <label>
                  Monto máximo
                  <input
                    type="number"
                    min="0"
                    placeholder="Ej. 500000"
                    value={filtros.montoMax}
                    onChange={e => cambiarFiltro('montoMax', e.target.value)}
                  />
                </label>

                <label>
                  Categoría
                  <select
                    value={filtros.categoria}
                    onChange={e => cambiarFiltro('categoria', e.target.value)}
                  >
                    <option value="">Todas las categorías</option>

                    {categoriasDisponibles.map(categoria => (
                      <option key={categoria} value={categoria}>
                        {categoria}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Tipo de movimiento
                  <select
                    value={filtros.tipo}
                    onChange={e => cambiarFiltro('tipo', e.target.value)}
                  >
                    <option value="">Todos los tipos</option>
                    <option value="gasto">Gasto</option>
                    <option value="ingreso">Ingreso</option>
                    <option value="deuda">Deuda</option>
                  </select>
                </label>

                <label>
                  Cuenta
                  <select
                    value={filtros.cuenta_id}
                    onChange={e => cambiarFiltro('cuenta_id', e.target.value)}
                  >
                    <option value="">Todas las cuentas</option>

                    {cuentas.map(cuenta => (
                      <option key={cuenta.id} value={cuenta.id}>
                        {cuenta.nombre}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <button
                type="button"
                className="boton"
                onClick={limpiarFiltros}
              >
                Limpiar filtros
              </button>
            </div>
          )}

          {/* CONTADOR DE RESULTADOS */}
          <p className="sub">
            Mostrando {transaccionesFiltradas.length} de {txs.length} movimientos
          </p>

          {txs.length === 0 ? (
            <p className="sub">
              Todavía no hay movimientos.
            </p>
          ) : transaccionesFiltradas.length === 0 ? (
            <p className="sub">
              No se encontraron movimientos con esos filtros.
            </p>
          ) : (
            <div className="tabla-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Categoría</th>
                    <th>Cuenta</th>
                    <th>Tipo</th>
                    <th className="derecha">Monto</th>
                    <th />
                  </tr>
                </thead>

                <tbody>
                  {transaccionesFiltradas.map(t => (
                    <TransactionCard
                      key={t.id}
                      tx={t}
                      nombreCuenta={nombreCuenta(t.cuenta_id)}
                      onEliminar={borrar}
                    />
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

      </div>
    </>
  )
}
