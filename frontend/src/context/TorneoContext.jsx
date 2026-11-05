
import { createContext, useContext } from 'react'

export const TorneoContext = createContext(null)

//usamos esta funcion para acceder al torneo seleccionado desde cualquier pagina
export function useTorneo() {
  const contexto = useContext(TorneoContext)

  if (!contexto) {
    throw new Error('La pagina debe estar dentro de TorneoContext.Provider')
  }

  return contexto
}
