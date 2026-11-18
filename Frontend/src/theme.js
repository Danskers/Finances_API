import { useSyncExternalStore } from 'react'

const CLAVE = 'kaiba-tema'
const oyentes = new Set()

function leer() {
  try {
    return localStorage.getItem(CLAVE) === 'dark' ? 'dark' : 'light'
  } catch {
    return 'light'
  }
}

let tema = leer()

function aplicar() {
  document.documentElement.setAttribute('data-theme', tema)
}
aplicar()

export function cambiarTema(nuevo) {
  tema = nuevo
  try {
    localStorage.setItem(CLAVE, tema)
  } catch {
    // si el navegador bloquea el almacenamiento, el tema sigue funcionando en memoria
  }
  aplicar()
  oyentes.forEach((f) => f())
}

export function useTema() {
  const actual = useSyncExternalStore(
    (cb) => {
      oyentes.add(cb)
      return () => oyentes.delete(cb)
    },
    () => tema
  )
  return {
    tema: actual,
    esOscuro: actual === 'dark',
    alternar: () => cambiarTema(actual === 'dark' ? 'light' : 'dark'),
  }
}
