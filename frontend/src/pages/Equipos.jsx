
import { useEffect, useState } from 'react'
import { obtenerEquipos } from '../services/api'
import './Equipos.css'

function Equipos() {
  const [equipos, setEquipos] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let activo = true

    async function cargarEquipos() {
      try {
        setCargando(true)
        setError('')

        const datos = await obtenerEquipos()

        if (activo) {
          setEquipos(datos)
        }
      } catch (error) {
        if (activo) {
          setError(error.message)
        }
      } finally {
        if (activo) {
          setCargando(false)
        }
      }
    }

    cargarEquipos()

    return () => {
      activo = false
    }
  }, [])

  return (
    <>
      <div className="dashboard-title-row">
        <div>
          <h2>Equipos</h2>
          <p>Equipos participantes del torneo y sus respectivos capitanes.</p>
        </div>
      </div>

      <section className="dashboard-panel equipos-panel">

        <div className="panel-heading">
          <div>
            <h3>Equipos registrados</h3>
            <p>Listado de equipos inscriptos en el torneo.</p>
          </div>
        </div>

        <div className="panel-divider" />

        {cargando ? (
          <p className="matches-message">Cargando equipos...</p>
        ) : error ? (
          <p className="matches-message matches-error">
            No se pudieron cargar los equipos: {error}
          </p>
        ) : equipos.length === 0 ? (
          <p className="matches-message">
            No hay equipos registrados.
          </p>
        ) : (
          <>
            <p className="equipos-contador">
              {equipos.length} equipos registrados
            </p>

            <div className="reporte-table-container">
              <table className="reporte-table">
                <thead>
                  <tr>
                    <th>Equipo</th>
                    <th>Facultad</th>
                    <th>Capitán</th>
                    <th>Cédula</th>
                    <th>Torneo</th>
                  </tr>
                </thead>

                <tbody>
                  {equipos.map(equipo => (
                    <tr key={equipo.id_equipo}>
                      <td className="equipo-nombre">
                        {equipo.nombre}
                      </td>

                      <td>{equipo.facultad}</td>

                      <td>
                        {equipo.nombre_capitan} {equipo.apellido_capitan}
                      </td>

                      <td>{equipo.ci_capitan}</td>

                      <td>{equipo.torneo}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

      </section>
    </>
  )
}

export default Equipos
