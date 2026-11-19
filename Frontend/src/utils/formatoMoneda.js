// Formato de moneda colombiana (COP): $ 1.250.000, sin decimales.
const completo = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
})

const compacto = new Intl.NumberFormat('es-CO', {
  notation: 'compact',
  maximumFractionDigits: 1,
})

export const formatoCOP = (valor) => completo.format(Number(valor) || 0)
export const formatoCOPCompacto = (valor) => `$ ${compacto.format(Number(valor) || 0)}`
