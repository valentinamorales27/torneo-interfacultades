
import { useEffect, useState } from 'react'
import {
  obtenerPartidos,
  obtenerPlanilla,
  agregarJugadorPlanilla,
  eliminarJugadorPlanilla,
  obtenerGoles,
  agregarGol,
  eliminarGol,
  obtenerTarjetas,
  agregarTarjeta,
  eliminarTarjeta
} from '../services/api'
import './Planillas.css'
import { useTorneo } from '../context/TorneoContext'

function Planillas() {
  const { idTorneo } = useTorneo()
  const [partidos, setPartidos] = useState([])
  const [idPartido, setIdPartido] = useState('')
  const [planilla, setPlanilla] = useState([])
  const [goles, setGoles] = useState([])
  const [tarjetas, setTarjetas] = useState([])

  const [ciJugador, setCiJugador] = useState('')
  const [minutoGol, setMinutoGol] = useState('')
  const [jugadorGol, setJugadorGol] = useState('')
  const [autogol, setAutogol] = useState(false)

  const [minutoTarjeta, setMinutoTarjeta] = useState('')
  const [jugadorTarjeta, setJugadorTarjeta] = useState('')
  const [colorTarjeta, setColorTarjeta] = useState('amarilla')

  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')

  // Cargar los partidos del torneo seleccionado
  useEffect(() => {
    async function cargarPartidos() {
      if (!idTorneo) {
        setPartidos([])
        setIdPartido('')
        setPlanilla([])
        setGoles([])
        setTarjetas([])
        return
      }

      try {
        setError('')
        setPartidos([])
        setIdPartido('')
        setPlanilla([])
        setGoles([])
        setTarjetas([])

        const datos = await obtenerPartidos(idTorneo)

        setPartidos(Array.isArray(datos) ? datos : datos.partidos || [])
      } catch (error) {
        setError(error.message)
      }
    }

    cargarPartidos()
  }, [idTorneo])

  // Cargar la información del partido seleccionado
  useEffect(() => {
    if (idPartido) {
      cargarDatosPartido()
    } else {
      setPlanilla([])
      setGoles([])
      setTarjetas([])
    }
  }, [idPartido])

  async function cargarPartidos() {
    try {
      const datos = await obtenerPartidos()
      setPartidos(Array.isArray(datos) ? datos : datos.partidos || [])
    } catch (error) {
      setError(error.message)
    }
  }

  async function cargarDatosPartido() {
    try {
      setCargando(true)
      setError('')
      const [datosPlanilla, datosGoles, datosTarjetas] = await Promise.all([
        obtenerPlanilla(idPartido),
        obtenerGoles(idPartido),
        obtenerTarjetas(idPartido)
      ])

      setPlanilla(Array.isArray(datosPlanilla) ? datosPlanilla : datosPlanilla.planilla || [])
      setGoles(Array.isArray(datosGoles) ? datosGoles : datosGoles.goles || [])
      setTarjetas(Array.isArray(datosTarjetas) ? datosTarjetas : datosTarjetas.tarjetas || [])
    } catch (error) {
      setError(error.message)
    } finally {
      setCargando(false)
    }
  }

  async function handleAgregarJugador(e) {
    e.preventDefault()
    try {
      setError('')
      setMensaje('')
      await agregarJugadorPlanilla(idPartido, ciJugador)
      setCiJugador('')
      setMensaje('Jugador agregado a la planilla.')
      await cargarDatosPartido()
    } catch (error) {
      setError(error.message)
    }
  }

  async function handleEliminarJugador(ci) {
    if (!window.confirm('¿Querés quitar este jugador de la planilla?')) return

    try {
      setError('')
      setMensaje('')
      await eliminarJugadorPlanilla(idPartido, ci)
      setMensaje('Jugador eliminado de la planilla.')
      await cargarDatosPartido()
    } catch (error) {
      setError(error.message)
    }
  }

  async function handleAgregarGol(e) {
    e.preventDefault()
    try {
      setError('')
      setMensaje('')
      await agregarGol(idPartido, {
        ci_jugador: jugadorGol,
        minuto: Number(minutoGol),
        autogol
      })
      setJugadorGol('')
      setMinutoGol('')
      setAutogol(false)
      setMensaje('Gol registrado.')
      await cargarDatosPartido()
    } catch (error) {
      setError(error.message)
    }
  }

  async function handleEliminarGol(idGol) {
    if (!window.confirm('¿Querés eliminar este gol?')) return

    try {
      setError('')
      await eliminarGol(idGol)
      setMensaje('Gol eliminado.')
      await cargarDatosPartido()
    } catch (error) {
      setError(error.message)
    }
  }

  async function handleAgregarTarjeta(e) {
    e.preventDefault()
    try {
      setError('')
      setMensaje('')
      await agregarTarjeta(idPartido, {
        ci_jugador: jugadorTarjeta,
        minuto: Number(minutoTarjeta),
        color: colorTarjeta
      })
      setJugadorTarjeta('')
      setMinutoTarjeta('')
      setColorTarjeta('amarilla')
      setMensaje('Tarjeta registrada.')
      await cargarDatosPartido()
    } catch (error) {
      setError(error.message)
    }
  }

  async function handleEliminarTarjeta(idTarjeta) {
    if (!window.confirm('¿Querés eliminar esta tarjeta?')) return

    try {
      setError('')
      await eliminarTarjeta(idTarjeta)
      setMensaje('Tarjeta eliminada.')
      await cargarDatosPartido()
    } catch (error) {
      setError(error.message)
    }
  }

  function nombreJugador(jugador) {
    return `${jugador.nombre || ''} ${jugador.apellido || ''}`.trim()
  }

  return (
    <div className="planillas-page">
      <div className="planillas-header">
        <div>
          <h1>Planillas</h1>
          <p>Administración de jugadores, goles y tarjetas de cada partido.</p>
        </div>
      </div>

      {error && <div className="planillas-alerta error">{error}</div>}
      {mensaje && <div className="planillas-alerta exito">{mensaje}</div>}

      <section className="planillas-panel">
        <label htmlFor="partido">Seleccionar partido</label>
        <select
          id="partido"
          value={idPartido}
          onChange={(e) => {
            setIdPartido(e.target.value)
            setError('')
            setMensaje('')
          }}
        >
          <option value="">Elegir un partido</option>
          {partidos.map((partido) => (
            <option key={partido.id_partido} value={partido.id_partido}>
              {partido.nombre_local || partido.equipo_local || `Equipo ${partido.id_equipo_local}`}
              {' vs. '}
              {partido.nombre_visitante || partido.equipo_visitante || `Equipo ${partido.id_equipo_visitante}`}
              {' - '}
              {partido.fecha || `Partido ${partido.id_partido}`}
            </option>
          ))}
        </select>
      </section>

      {!idPartido ? (
        <div className="planillas-vacio">Seleccioná un partido para consultar su planilla.</div>
      ) : cargando ? (
        <div className="planillas-vacio">Cargando información...</div>
      ) : (
        <>
          <section className="planillas-panel">
            <h2>Jugadores en la planilla</h2>

            <form className="planillas-form" onSubmit={handleAgregarJugador}>
              <input
                type="text"
                placeholder="Cédula del jugador"
                value={ciJugador}
                onChange={(e) => setCiJugador(e.target.value)}
                required
              />
              <button type="submit">Agregar jugador</button>
            </form>

            {planilla.length === 0 ? (
              <p className="planillas-vacio">Todavía no hay jugadores en esta planilla.</p>
            ) : (
              <div className="planillas-tabla-contenedor">
                <table className="planillas-tabla">
                  <thead>
                    <tr>
                      <th>Jugador</th>
                      <th>Cédula</th>
                      <th>Equipo</th>
                      <th>Camiseta</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {planilla.map((jugador) => (
                      <tr key={jugador.ci_jugador}>
                        <td>{nombreJugador(jugador)}</td>
                        <td>{jugador.ci_jugador}</td>
                        <td>{jugador.id_equipo}</td>
                        <td>{jugador.numero_camiseta ?? '-'}</td>
                        <td>
                          <button
                            className="planillas-boton eliminar"
                            onClick={() => handleEliminarJugador(jugador.ci_jugador)}
                          >
                            Quitar
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section className="planillas-panel">
            <h2>Goles</h2>

            <form className="planillas-form" onSubmit={handleAgregarGol}>
              <select
                value={jugadorGol}
                onChange={(e) => setJugadorGol(e.target.value)}
                required
              >
                <option value="">Seleccionar jugador</option>
                {planilla.map((jugador) => (
                  <option key={jugador.ci_jugador} value={jugador.ci_jugador}>
                    {nombreJugador(jugador)}
                  </option>
                ))}
              </select>

              <input
                type="number"
                min="0"
                placeholder="Minuto"
                value={minutoGol}
                onChange={(e) => setMinutoGol(e.target.value)}
                required
              />

              <label className="planillas-checkbox">
                <input
                  type="checkbox"
                  checked={autogol}
                  onChange={(e) => setAutogol(e.target.checked)}
                />
                Autogol
              </label>

              <button type="submit">Registrar gol</button>
            </form>

            {goles.length === 0 ? (
              <p className="planillas-vacio">No hay goles registrados.</p>
            ) : (
              <div className="planillas-tabla-contenedor">
                <table className="planillas-tabla">
                  <thead>
                    <tr>
                      <th>Jugador</th>
                      <th>Minuto</th>
                      <th>Tipo</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {goles.map((gol) => (
                      <tr key={gol.id_gol}>
                        <td>{nombreJugador(gol)}</td>
                        <td>{gol.minuto}'</td>
                        <td>{gol.autogol ? 'Autogol' : 'Gol'}</td>
                        <td>
                          <button
                            className="planillas-boton eliminar"
                            onClick={() => handleEliminarGol(gol.id_gol)}
                          >
                            Eliminar
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section className="planillas-panel">
            <h2>Tarjetas</h2>

            <form className="planillas-form" onSubmit={handleAgregarTarjeta}>
              <select
                value={jugadorTarjeta}
                onChange={(e) => setJugadorTarjeta(e.target.value)}
                required
              >
                <option value="">Seleccionar jugador</option>
                {planilla.map((jugador) => (
                  <option key={jugador.ci_jugador} value={jugador.ci_jugador}>
                    {nombreJugador(jugador)}
                  </option>
                ))}
              </select>

              <input
                type="number"
                min="0"
                placeholder="Minuto"
                value={minutoTarjeta}
                onChange={(e) => setMinutoTarjeta(e.target.value)}
                required
              />

              <select
                value={colorTarjeta}
                onChange={(e) => setColorTarjeta(e.target.value)}
              >
                <option value="amarilla">Amarilla</option>
                <option value="roja">Roja</option>
              </select>

              <button type="submit">Registrar tarjeta</button>
            </form>

            {tarjetas.length === 0 ? (
              <p className="planillas-vacio">No hay tarjetas registradas.</p>
            ) : (
              <div className="planillas-tabla-contenedor">
                <table className="planillas-tabla">
                  <thead>
                    <tr>
                      <th>Jugador</th>
                      <th>Minuto</th>
                      <th>Tarjeta</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {tarjetas.map((tarjeta) => (
                      <tr key={tarjeta.id_tarjeta}>
                        <td>{nombreJugador(tarjeta)}</td>
                        <td>{tarjeta.minuto}'</td>
                        <td>{tarjeta.color}</td>
                        <td>
                          <button
                            className="planillas-boton eliminar"
                            onClick={() => handleEliminarTarjeta(tarjeta.id_tarjeta)}
                          >
                            Eliminar
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  )
}

export default Planillas
