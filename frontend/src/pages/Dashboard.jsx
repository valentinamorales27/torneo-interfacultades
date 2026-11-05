import './Dashboard.css'
import { useEffect, useState } from 'react'

import { obtenerProximosPartidos } from '../services/api'
import { useTorneo } from '../context/TorneoContext'

// Componente encargado de dibujar los iconos
function Icon({ name }) {
  const paths = {
    home: <><path d="m3 10 9-7 9 7" /><path d="M5 9v12h14V9M9 21v-7h6v7" /></>,
    users: <><path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="10" cy="7" r="4" /><path d="M20 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" /></>,
    user: <><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></>,
    calendar: <><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M16 3v4M8 3v4M3 10h18M8 14h3M8 17h6" /></>,
    trophy: <><path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0V4Z" /><path d="M7 6H4v3a4 4 0 0 0 4 4M17 6h3v3a4 4 0 0 1-4 4" /></>,
    shield: <><path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z" /><path d="m9 12 2 2 4-4" /></>,
    ball: <><circle cx="12" cy="12" r="9" /><path d="m12 7 4 3-1.5 5h-5L8 10l4-3ZM12 7V3M16 10l4-1M14.5 15l2 4M9.5 15l-2 4M8 10l-4-1" /></>,
    info: <><circle cx="12" cy="12" r="9" /><path d="M12 11v5M12 8h.01" /></>,
    pin: <><path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z" /><circle cx="12" cy="10" r="2.5" /></>,
    arrow: <><path d="M5 12h14M13 6l6 6-6 6" /></>
  }

  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  )
}

// Formatea la fecha que devuelve Flask
function formatearFecha(fecha) {
  if (!fecha) return 'Fecha sin definir'

  const fechaObjeto = new Date(fecha)

  if (Number.isNaN(fechaObjeto.getTime())) {
    return fecha
  }

  return new Intl.DateTimeFormat('es-UY', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC'
  }).format(fechaObjeto)
}

// Muestra solamente horas y minutos
function formatearHora(hora) {
  if (!hora) return '--:--'

  return String(hora).slice(0, 5)
}

// Página de resumen del torneo
function Dashboard() {
  const { idTorneo, torneoSeleccionado } = useTorneo()

  const [partidos, setPartidos] = useState([])
  const [cargandoPartidos, setCargandoPartidos] = useState(true)
  const [errorPartidos, setErrorPartidos] = useState('')

  // Consultamos los próximos partidos del torneo seleccionado
  useEffect(() => {
    async function cargarPartidos() {
      try {
        setCargandoPartidos(true)
        setErrorPartidos('')
        setPartidos([])

        const datos = await obtenerProximosPartidos(idTorneo)

        setPartidos(datos)
      } catch (error) {
        console.error('Error al consultar los próximos partidos:', error)
        setErrorPartidos(error.message)
      } finally {
        setCargandoPartidos(false)
      }
    }

    if (idTorneo) {
      cargarPartidos()
    }
  }, [idTorneo])

  return (
    <>
      <div className="dashboard-title-row">
        <div>
          <h2>Resumen del torneo</h2>
          <p>
            Toda la información de la competencia, en un solo lugar.
          </p>
        </div>

        
      </div>

      <div className="dashboard-grid">

        {/* Próximos partidos */}
        <section
          className="dashboard-panel matches-panel"
          id="proximos-partidos"
        >
          <div className="panel-heading">
            <span className="panel-icon blue-light">
              <Icon name="calendar" />
            </span>

            <div>
              <h3>Próximos partidos</h3>
              <p>Consulta el calendario de encuentros.</p>
            </div>
          </div>

          <div className="panel-divider" />

          {cargandoPartidos ? (
            <p className="matches-message">
              Cargando próximos partidos...
            </p>
          ) : errorPartidos ? (
            <p className="matches-message matches-error">
              No se pudieron cargar los partidos: {errorPartidos}
            </p>
          ) : partidos.length === 0 ? (
            <div className="empty-matches">
              <div className="empty-field">
                <div className="field-center-line" />
                <div className="field-center-circle" />
              </div>

              <strong>No hay próximos partidos</strong>

              <p>
                Por el momento no hay encuentros programados para este torneo.
              </p>
            </div>
          ) : (
            <div className="matches-list">
              {partidos.map((partido) => (
                <article
                  className="match-card"
                  key={partido.id_partido}
                >
                  <div className="match-date">
                    <Icon name="calendar" />
                    <span>{formatearFecha(partido.dia)}</span>
                    <small>Fecha {partido.numero_fecha}</small>
                  </div>

                  <div className="match-teams">
                    <strong>{partido.equipo_local}</strong>
                    <span>VS</span>
                    <strong>{partido.equipo_visitante}</strong>
                  </div>

                  <div className="match-details">
                    <span>
                      {formatearHora(partido.hora_inicio)}
                      {' - '}
                      {formatearHora(partido.hora_fin)}
                    </span>

                    <span>
                      <Icon name="pin" />
                      {partido.nombre_cancha} · {partido.complejo}
                    </span>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        {/* Información del torneo */}
        <section
          className="dashboard-panel tournament-panel"
          id="informacion-torneo"
        >
          <div className="panel-heading">
            <span className="panel-icon green-light">
              <Icon name="info" />
            </span>

            <h3>Información del torneo</h3>
          </div>

          <div className="tournament-detail">
            <span className="detail-icon">
              <Icon name="trophy" />
            </span>

            <div>
              <small>Edición</small>
              <strong>{torneoSeleccionado?.nombre}</strong>
            </div>
          </div>

          <div className="tournament-detail">
            <span className="detail-icon">
              <Icon name="calendar" />
            </span>

            <div>
              <small>Período</small>
              <strong>
                {torneoSeleccionado?.anio} - {torneoSeleccionado?.semestre}° semestre
              </strong>
            </div>
          </div>

          <div className="tournament-detail">
            <span className="detail-icon">
              <Icon name="info" />
            </span>

            <div>
              <small>Estado</small>
              <strong>{torneoSeleccionado?.estado}</strong>
            </div>
          </div>

          <div className="tournament-detail">
            <span className="detail-icon">
              <Icon name="pin" />
            </span>

            <div>
              <small>Fechas</small>
              <strong>
                {formatearFecha(torneoSeleccionado?.fecha_inicio)}
                {' - '}
                {formatearFecha(torneoSeleccionado?.fecha_fin)}
              </strong>
            </div>
          </div>
        </section>

      </div>

      <p className="dashboard-hint">
        Seleccioná una pestaña para consultar cada sección del torneo.
      </p>
    </>
  )
}

export default Dashboard