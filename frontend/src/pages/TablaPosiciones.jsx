
import './TablaPosiciones.css'

import { useEffect, useState } from 'react'
import { obtenerTablaPosiciones } from '../services/api'
import { useTorneo } from '../context/TorneoContext'

function TablaPosiciones() {
  const { idTorneo } = useTorneo()

  const [tablaPosiciones, setTablaPosiciones] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  // Consultamos la tabla de posiciones del torneo seleccionado
  useEffect(() => {
    async function cargarTabla() {
      if (!idTorneo) {
        setTablaPosiciones([])
        setCargando(false)
        return
      }

      try {
        setCargando(true)
        setError('')
        setTablaPosiciones([])

        const datos = await obtenerTablaPosiciones(idTorneo)

        setTablaPosiciones(Array.isArray(datos) ? datos : [])
      } catch (error) {
        console.error('Error al consultar la tabla:', error)
        setError(error.message)
      } finally {
        setCargando(false)
      }
    }

    cargarTabla()
  }, [idTorneo])

  return (
    <>
      <div className="dashboard-title-row">
        <div>
          <h2>Tabla de posiciones</h2>
          <p>
            Clasificación actual de los equipos del torneo.
          </p>
        </div>
      </div>

      <section className="dashboard-panel standings-panel">
        <div className="panel-heading">
          <span className="panel-icon green-light">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0V4Z" />
              <path d="M7 6H4v3a4 4 0 0 0 4 4M17 6h3v3a4 4 0 0 0-4 4" />
            </svg>
          </span>

          <div>
            <h3>Clasificación general</h3>
            <p>Posiciones de los equipos participantes.</p>
          </div>
        </div>

        <div className="panel-divider" />

        {cargando ? (
          <p className="matches-message">
            Cargando tabla de posiciones...
          </p>
        ) : error ? (
          <p className="matches-message matches-error">
            No se pudo cargar la tabla: {error}
          </p>
        ) : tablaPosiciones.length === 0 ? (
          <p className="matches-message">
            Todavía no hay equipos registrados en este torneo.
          </p>
        ) : (
          <div className="standings-table-container">
            <table className="standings-table">
              <thead>
                <tr>
                  <th>Pos.</th>
                  <th>Equipo</th>
                  <th>PJ</th>
                  <th>PG</th>
                  <th>PE</th>
                  <th>PP</th>
                  <th>GF</th>
                  <th>GC</th>
                  <th>DG</th>
                  <th>Pts.</th>
                </tr>
              </thead>

              <tbody>
                {tablaPosiciones.map((equipo, indice) => (
                  <tr key={equipo.id_equipo}>
                    <td>{indice + 1}</td>

                    <td className="standings-team">
                      {equipo.equipo}
                    </td>

                    <td>{equipo.pj}</td>
                    <td>{equipo.pg}</td>
                    <td>{equipo.pe}</td>
                    <td>{equipo.pp}</td>
                    <td>{equipo.gf}</td>
                    <td>{equipo.gc}</td>
                    <td>{equipo.dg}</td>

                    <td className="standings-points">
                      {equipo.puntos}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  )
}

export default TablaPosiciones
