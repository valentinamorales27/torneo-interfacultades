
import { useEffect, useState } from 'react'

import {
  obtenerFairPlay,
  obtenerSancionesEquipo
} from '../services/api'

import ReporteTabla from '../components/ReporteTabla'

const ID_TORNEO = 1

function FairPlay() {
  const [reportes, setReportes] = useState({
    fairPlay: { datos: [], cargando: true, error: '' },
    sanciones: { datos: [], cargando: true, error: '' }
  })

  useEffect(() => {
    let activo = true

    async function cargarReportes() {
      const consultas = [
        ['fairPlay', obtenerFairPlay(ID_TORNEO)],
        ['sanciones', obtenerSancionesEquipo(ID_TORNEO)]
      ]

      const resultados = await Promise.all(
        consultas.map(async ([nombre, consulta]) => {
          try {
            const datos = await consulta

            return [
              nombre,
              { datos, cargando: false, error: '' }
            ]
          } catch (error) {
            return [
              nombre,
              { datos: [], cargando: false, error: error.message }
            ]
          }
        })
      )

      if (activo) {
        setReportes(Object.fromEntries(resultados))
      }
    }

    cargarReportes()

    return () => {
      activo = false
    }
  }, [])

  return (
    <>
      <div className="dashboard-title-row">
        <div>
          <h2>Fair Play</h2>
          <p>Clasificación disciplinaria y sanciones de los equipos.</p>
        </div>
      </div>

      <ReporteTabla
        titulo="Clasificación Fair Play"
        descripcion="Puntos disciplinarios acumulados por equipo. Menor puntaje significa mejor Fair Play."
        columnas={[
          { key: 'equipo', titulo: 'Equipo' },
          { key: 'puntos_fair_play', titulo: 'Puntos disciplinarios' }
        ]}
        {...reportes.fairPlay}
        mensajeVacio="Todavía no hay información de Fair Play."
      />

      <ReporteTabla
        titulo="Sanciones por equipo"
        descripcion="Cantidad de sanciones registradas según el equipo y el motivo."
        columnas={[
          { key: 'equipo', titulo: 'Equipo' },
          { key: 'motivo', titulo: 'Motivo' },
          { key: 'cantidad_sanciones', titulo: 'Cantidad de sanciones' }
        ]}
        {...reportes.sanciones}
        mensajeVacio="No hay sanciones registradas."
      />
    </>
  )
}

export default FairPlay
