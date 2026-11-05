import { useEffect, useState } from 'react'

import {
  obtenerEstadoPartidos,
  obtenerPartidosCanceladosPostergados,
  obtenerPromedioGoles,
  obtenerUsoCanchasTurnos,
  obtenerPartidosTorneo
} from '../services/api'

import ReporteTabla from '../components/ReporteTabla'

const ID_TORNEO = 1

function Partidos() {
  const [reportes, setReportes] = useState({
    estados: { datos: [], cargando: true, error: '' },
    cancelados: { datos: [], cargando: true, error: '' },
    promedio: { datos: [], cargando: true, error: '' },
    canchas: { datos: [], cargando: true, error: '' }
  })

  const [mostrarHistorial, setMostrarHistorial] = useState(false)
  const [partidos, setPartidos] = useState([])
  const [cargandoPartidos, setCargandoPartidos] = useState(false)
  const [errorPartidos, setErrorPartidos] = useState('')

  useEffect(() => {
    let activo = true

    async function cargarReportes() {
      const consultas = [
        ['estados', obtenerEstadoPartidos(ID_TORNEO)],
        ['cancelados', obtenerPartidosCanceladosPostergados(ID_TORNEO)],
        ['promedio', obtenerPromedioGoles(ID_TORNEO)],
        ['canchas', obtenerUsoCanchasTurnos(ID_TORNEO)]
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

  async function cargarHistorial() {
    try {
      setCargandoPartidos(true)
      setErrorPartidos('')

      const datos = await obtenerPartidosTorneo(ID_TORNEO)
      setPartidos(datos)
    } catch (error) {
      setErrorPartidos(error.message)
    } finally {
      setCargandoPartidos(false)
    }
  }

  async function alternarVista() {
    if (!mostrarHistorial && partidos.length === 0) {
      await cargarHistorial()
    }

    setMostrarHistorial(!mostrarHistorial)
  }

  return (
    <>
      <div className="dashboard-title-row">
        <div>
          <h2>Partidos</h2>
          <p>Estado, programación y estadísticas de los encuentros.</p>
        </div>
      </div>

      <div className="partidos-acciones">
        <button
          type="button"
          className="dashboard-action-button"
          onClick={alternarVista}
        >
          {mostrarHistorial ? 'Ver reportes' : 'Historial de partidos'}
        </button>
      </div>

      {mostrarHistorial ? (
        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <h3>Historial de partidos</h3>
              <p>Listado de los encuentros del torneo.</p>
            </div>
          </div>

          <div className="panel-divider" />

          {cargandoPartidos ? (
            <p className="matches-message">Cargando partidos...</p>
          ) : errorPartidos ? (
            <p className="matches-message matches-error">
              No se pudieron cargar los partidos: {errorPartidos}
            </p>
          ) : partidos.length === 0 ? (
            <p className="matches-message">
              No hay partidos registrados en este torneo.
            </p>
          ) : (
            <>
              <p className="equipos-contador">
                {partidos.length} partidos registrados
              </p>

              <div className="reporte-table-container">
                <table className="reporte-table">
                  <thead>
                    <tr>
                      <th>Número</th>
                      <th>Fecha del torneo</th>
                      <th>Día</th>
                      <th>Equipo local</th>
                      <th>Equipo visitante</th>
                      <th>Turno</th>
                      <th>Cancha</th>
                      <th>Complejo</th>
                      <th>Estado</th>
                    </tr>
                  </thead>

                  <tbody>
                    {partidos.map(partido => (
                      <tr key={partido.id_partido}>
                        <td>{partido.id_partido}</td>
                        <td>{partido.numero_fecha}</td>
                        <td>{partido.dia}</td>
                        <td>{partido.equipo_local}</td>
                        <td>{partido.equipo_visitante}</td>
                        <td>{partido.id_turno}</td>
                        <td>{partido.nombre_cancha}</td>
                        <td>{partido.id_complejo}</td>
                        <td>{partido.estado}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </section>
      ) : (
        <>
          <ReporteTabla
            titulo="Estado de los partidos"
            descripcion="Cantidad y porcentaje de partidos según su estado."
            columnas={[
              { key: 'estado', titulo: 'Estado' },
              { key: 'cantidad', titulo: 'Cantidad' },
              {
                key: 'porcentaje',
                titulo: 'Porcentaje',
                render: fila => `${fila.porcentaje}%`
              }
            ]}
            {...reportes.estados}
            mensajeVacio="No hay información sobre los partidos."
          />

          <ReporteTabla
            titulo="Partidos cancelados y postergados"
            descripcion="Encuentros que fueron cancelados o cambiaron su programación."
            columnas={[
              { key: 'id_partido', titulo: 'Partido' },
              { key: 'numero_fecha', titulo: 'Fecha' },
              { key: 'dia', titulo: 'Día' },
              { key: 'equipo_local', titulo: 'Equipo local' },
              { key: 'equipo_visitante', titulo: 'Equipo visitante' },
              { key: 'estado', titulo: 'Estado' },
              { key: 'hora_inicio', titulo: 'Hora' },
              { key: 'nombre_cancha', titulo: 'Cancha' },
              { key: 'complejo', titulo: 'Complejo' }
            ]}
            {...reportes.cancelados}
            mensajeVacio="No hay partidos cancelados ni postergados."
          />

          <ReporteTabla
            titulo="Promedio de goles por fecha"
            descripcion="Cantidad de goles y promedio de goles por partido en cada fecha."
            columnas={[
              { key: 'numero_fecha', titulo: 'Fecha' },
              { key: 'goles_totales', titulo: 'Goles totales' },
              { key: 'partidos_jugados', titulo: 'Partidos jugados' },
              {
                key: 'promedio_goles',
                titulo: 'Promedio',
                render: fila => Number(fila.promedio_goles).toFixed(2)
              }
            ]}
            {...reportes.promedio}
            mensajeVacio="Todavía no hay fechas con partidos disputados."
          />

          <ReporteTabla
            titulo="Uso de canchas y turnos"
            descripcion="Cantidad de partidos disputados en cada cancha y horario."
            columnas={[
              { key: 'nombre_cancha', titulo: 'Cancha' },
              { key: 'complejo', titulo: 'Complejo' },
              { key: 'hora_inicio', titulo: 'Hora de inicio' },
              { key: 'hora_fin', titulo: 'Hora de fin' },
              { key: 'partidos_jugados', titulo: 'Partidos jugados' }
            ]}
            {...reportes.canchas}
            mensajeVacio="Todavía no hay información de uso de canchas."
          />
        </>
      )}
    </>
  )
}

export default Partidos
