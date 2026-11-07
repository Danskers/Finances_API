import { formatear } from './AccountCard.jsx'

export default function TransactionCard({ tx, nombreCuenta, onEliminar }) {
  const ingreso = tx.tipo === 'ingreso'
  return (
    <tr>
      <td>{new Date(tx.fecha).toLocaleDateString('es-CO')}</td>
      <td>{tx.categoria}{tx.subcategoria ? ` · ${tx.subcategoria}` : ''}</td>
      <td>{nombreCuenta}</td>
      <td><span className={`etiqueta ${tx.tipo}`}>{tx.tipo}</span></td>
      <td className={`derecha monto-fila ${ingreso ? 'pos' : 'neg'}`}>
        {ingreso ? '+' : '-'}{formatear(tx.monto)}
      </td>
      <td className="derecha">
        {tx.factura_url && <a href={tx.factura_url} target="_blank" rel="noreferrer">Factura</a>}{' '}
        <button type="button" className="link peligro" onClick={() => onEliminar(tx)}>Borrar</button>
      </td>
    </tr>
  )
}
