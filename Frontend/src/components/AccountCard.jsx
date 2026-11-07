export default function AccountCard({ cuenta, color = 0, balance, onRenombrar, onEliminar }) {
  return (
    <article className={`tarjeta cuenta color-${color % 3}`}>
      <div className="cuenta-cabecera">
        <h3>{cuenta.nombre}</h3>
        <p className="monto">{formatear(balance ?? 0)}</p>
      </div>
      <div className="cuenta-acciones">
        <button type="button" className="link" onClick={() => onRenombrar(cuenta)}>Cambiar nombre</button>
        <button type="button" className="link peligro" onClick={() => onEliminar(cuenta)}>Eliminar</button>
      </div>
    </article>
  )
}

export const formatear = (n) =>
  new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n)
