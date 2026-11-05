
import { useEffect, useState } from 'react'

import {
  obtenerEstadoPartidos,
  obtenerPartidosCanceladosPostergados,
  obtenerPromedioGoles,
  obtenerUsoCanchasTurnos,
  obtenerPartidosTorneo,
  obtenerEquipos,
  obtenerCanchas,
  obtenerTurnos,
  obtenerSesion,
  crearPartido,
  modificarPartido,
  eliminarPartido
} from '../services/api'

import ReporteTabla from '../components/ReporteTabla'
import { useTorneo } from '../context/TorneoContext'
import './Partidos.css'

function Partidos() {
  const { idTorneo } = useTorneo()

  const [rol, setRol] = useState('')
  const [mostrarHistorial, setMostrarHistorial] = useState(false)

  const [reportes, setReportes] = useState({
    estados: { datos: [], cargando: true, error: '' },
    cancelados: { datos: [], cargando: true, error: '' },
    promedio: { datos: [], cargando: true, error: '' },
    canchas: { datos: [], cargando: true, error: '' }
  })

  const [actualizarReportes, setActualizarReportes] = useState(0)

  const [partidos, setPartidos] = useState([])
  const [cargandoPartidos, setCargandoPartidos] = useState(false)
  const [errorPartidos, setErrorPartidos] = useState('')

  // Estados del modal y formulario
  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const [partidoEditando, setPartidoEditando] = useState(null)
  const [guardando, setGuardando] = useState(false)
  const [errorFormulario, setErrorFormulario] = useState('')

  const [equipos, setEquipos] = useState([])
  const [canchas, setCanchas] = useState([])
  const [turnos, setTurnos] = useState([])
  const [cargandoOpciones, setCargandoOpciones] = useState(false)

  const [formulario, setFormulario] = useState({
    numero_fecha: '',
    id_equipo_local: '',
    id_equipo_visitante: '',
    dia: '',
    id_turno: '',
    nombre_cancha: '',
    id_complejo: '',
    estado: 'programado'
  })

  // Obtenemos el rol del usuario que inició sesión
  useEffect(() => {
    async function cargarSesion() {
      try {
        const sesion = await obtenerSesion()
        setRol(sesion.rol)
      } catch (error) {
        setRol('')
      }
    }

    cargarSesion()
  }, [])

  // Obtenemos los reportes del torneo seleccionado
  useEffect(() => {
    let activo = true

    async function cargarReportes() {
      if (!idTorneo) return

      setReportes({
        estados: { datos: [], cargando: true, error: '' },
        cancelados: { datos: [], cargando: true, error: '' },
        promedio: { datos: [], cargando: true, error: '' },
        canchas: { datos: [], cargando: true, error: '' }
      })

      const consultas = [
        ['estados', obtenerEstadoPartidos(idTorneo)],
        ['cancelados', obtenerPartidosCanceladosPostergados(idTorneo)],
        ['promedio', obtenerPromedioGoles(idTorneo)],
        ['canchas', obtenerUsoCanchasTurnos(idTorneo)]
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
  }, [idTorneo, actualizarReportes])

  // Obtenemos el historial de partidos
  async function cargarHistorial() {
    if (!idTorneo) return

    try {
      setCargandoPartidos(true)
      setErrorPartidos('')

      const datos = await obtenerPartidosTorneo(idTorneo)
      setPartidos(datos)
    } catch (error) {
      setErrorPartidos(error.message)
    } finally {
      setCargandoPartidos(false)
    }
  }

  useEffect(() => {
    if (mostrarHistorial && idTorneo) {
      cargarHistorial()
    }
  }, [mostrarHistorial, idTorneo])

  // Cargamos los datos necesarios para los selectores
  async function cargarOpciones() {
    try {
      setCargandoOpciones(true)
      setErrorFormulario('')

      const [datosEquipos, datosCanchas, datosTurnos] = await Promise.all([
        obtenerEquipos(idTorneo),
        obtenerCanchas(),
        obtenerTurnos()
      ])

      setEquipos(datosEquipos)
      setCanchas(datosCanchas)
      setTurnos(datosTurnos)
    } catch (error) {
      setErrorFormulario(error.message)
    } finally {
      setCargandoOpciones(false)
    }
  }

  // Abrimos el modal para crear un partido
  async function abrirFormularioNuevo() {
    setPartidoEditando(null)

    setFormulario({
      numero_fecha: '',
      id_equipo_local: '',
      id_equipo_visitante: '',
      dia: '',
      id_turno: '',
      nombre_cancha: '',
      id_complejo: '',
      estado: 'programado'
    })

    setErrorFormulario('')
    setMostrarFormulario(true)

    await cargarOpciones()
  }

  // Abrimos el modal con los datos del partido seleccionado
  async function abrirFormularioEditar(partido) {
    setPartidoEditando(partido)

    setFormulario({
      numero_fecha: String(partido.numero_fecha),
      id_equipo_local: String(partido.id_equipo_local),
      id_equipo_visitante: String(partido.id_equipo_visitante),
      dia: String(partido.dia).slice(0, 10),
      id_turno: String(partido.id_turno),
      nombre_cancha: partido.nombre_cancha,
      id_complejo: String(partido.id_complejo),
      estado: partido.estado
    })

    setErrorFormulario('')
    setMostrarFormulario(true)

    await cargarOpciones()
  }

  // Cerramos el modal
  function cerrarFormulario() {
    if (guardando) return

    setMostrarFormulario(false)
    setPartidoEditando(null)
    setErrorFormulario('')
  }

  // Actualizamos los valores del formulario
  function cambiarCampo(evento) {
    const { name, value } = evento.target

    setFormulario(actual => ({
      ...actual,
      [name]: value
    }))
  }

  // Guardamos el partido nuevo o los cambios realizados
  async function guardarPartido(evento) {
    evento.preventDefault()

    setErrorFormulario('')

    if (!idTorneo) {
      setErrorFormulario('No hay un torneo seleccionado')
      return
    }

    if (
      !formulario.numero_fecha ||
      !formulario.id_equipo_local ||
      !formulario.id_equipo_visitante ||
      !formulario.dia ||
      !formulario.id_turno ||
      !formulario.nombre_cancha ||
      !formulario.id_complejo
    ) {
      setErrorFormulario('Completá todos los campos obligatorios')
      return
    }

    if (
      formulario.id_equipo_local === formulario.id_equipo_visitante
    ) {
      setErrorFormulario('Los equipos deben ser diferentes')
      return
    }

    const datos = {
      id_torneo: Number(idTorneo),
      numero_fecha: Number(formulario.numero_fecha),
      id_equipo_local: Number(formulario.id_equipo_local),
      id_equipo_visitante: Number(formulario.id_equipo_visitante),
      dia: formulario.dia,
      id_turno: Number(formulario.id_turno),
      nombre_cancha: formulario.nombre_cancha,
      id_complejo: Number(formulario.id_complejo),
      estado: formulario.estado
    }

    try {
      setGuardando(true)

      if (partidoEditando) {
        await modificarPartido(partidoEditando.id_partido, datos)
      } else {
        await crearPartido(datos)
      }

      setMostrarFormulario(false)
      setPartidoEditando(null)

      await cargarHistorial()
      setActualizarReportes(actual => actual + 1)

    } catch (error) {
      setErrorFormulario(error.message)
    } finally {
      setGuardando(false)
    }
  }

  // Eliminamos un partido programado
  async function borrarPartido(partido) {
    const confirmar = window.confirm(
      `¿Seguro que querés eliminar el partido entre ${partido.equipo_local} y ${partido.equipo_visitante}?`
    )

    if (!confirmar) return

    try {
      await eliminarPartido(partido.id_partido)
      await cargarHistorial()
      setActualizarReportes(actual => actual + 1)
    } catch (error) {
      setErrorPartidos(error.message)
    }
  }

  function alternarVista() {
    setMostrarHistorial(actual => !actual)
    setMostrarFormulario(false)
  }

  // Opciones permitidas para cambiar el estado
  function obtenerEstadosPermitidos(estadoActual) {
    if (estadoActual === 'programado') {
      return ['programado', 'jugado', 'postergado', 'cancelado']
    }

    if (estadoActual === 'postergado') {
      return ['postergado', 'programado', 'cancelado']
    }

    return [estadoActual]
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
          {mostrarHistorial ? 'Ver reportes' : 'Todos los partidos'}
        </button>
      </div>

      {mostrarHistorial ? (
        <section className="dashboard-panel">
          <div className="panel-heading partidos-panel-heading">
            <div>
              <h3>Historial de partidos</h3>
              <p>Listado de los encuentros del torneo.</p>
            </div>

            {rol === 'administrador' && (
              <button
                type="button"
                className="partidos-boton-principal"
                onClick={abrirFormularioNuevo}
              >
                + Nuevo partido
              </button>
            )}
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
                      {rol === 'administrador' && <th>Acciones</th>}
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

                        {rol === 'administrador' && (
                          <td>
                            <div className="partidos-tabla-acciones">
                              {!['jugado', 'cancelado'].includes(partido.estado) && (
                                <button
                                  type="button"
                                  className="partidos-boton-editar"
                                  onClick={() => abrirFormularioEditar(partido)}
                                >
                                  Modificar
                                </button>
                              )}

                              {partido.estado === 'programado' && (
                                <button
                                  type="button"
                                  className="partidos-boton-eliminar"
                                  onClick={() => borrarPartido(partido)}
                                >
                                  Eliminar
                                </button>
                              )}
                            </div>
                          </td>
                        )}
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

      {/* Modal para crear o modificar partidos */}
      {mostrarFormulario && rol === 'administrador' && (
        <div
          className="partidos-modal-fondo"
          onClick={cerrarFormulario}
        >
          <div
            className="partidos-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="titulo-modal-partido"
            onClick={evento => evento.stopPropagation()}
          >
            <div className="partidos-modal-encabezado">
              <div>
                <h3 id="titulo-modal-partido">
                  {partidoEditando ? 'Modificar partido' : 'Crear partido'}
                </h3>
                <p>
                  {partidoEditando
                    ? 'Modificá los datos del encuentro.'
                    : 'Completá los datos para registrar un nuevo encuentro.'}
                </p>
              </div>

              <button
                type="button"
                className="partidos-modal-cerrar"
                onClick={cerrarFormulario}
                disabled={guardando}
                aria-label="Cerrar"
              >
                ×
              </button>
            </div>

            {errorFormulario && (
              <p className="partidos-error">{errorFormulario}</p>
            )}

            {cargandoOpciones ? (
              <p>Cargando equipos, canchas y turnos...</p>
            ) : (
              <form onSubmit={guardarPartido}>
                <div className="partidos-form-grid">
                  <label>
                    Número de fecha
                    <input
                      type="number"
                      name="numero_fecha"
                      min="1"
                      value={formulario.numero_fecha}
                      onChange={cambiarCampo}
                      required
                    />
                  </label>

                  <label>
                    Día del partido
                    <input
                      type="date"
                      name="dia"
                      value={formulario.dia}
                      onChange={cambiarCampo}
                      required
                    />
                  </label>

                  <label>
                    Equipo local
                    <select
                      name="id_equipo_local"
                      value={formulario.id_equipo_local}
                      onChange={cambiarCampo}
                      required
                    >
                      <option value="">Seleccionar equipo</option>
                      {equipos.map(equipo => (
                        <option
                          key={equipo.id_equipo}
                          value={equipo.id_equipo}
                        >
                          {equipo.nombre}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Equipo visitante
                    <select
                      name="id_equipo_visitante"
                      value={formulario.id_equipo_visitante}
                      onChange={cambiarCampo}
                      required
                    >
                      <option value="">Seleccionar equipo</option>
                      {equipos.map(equipo => (
                        <option
                          key={equipo.id_equipo}
                          value={equipo.id_equipo}
                        >
                          {equipo.nombre}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Turno
                    <select
                      name="id_turno"
                      value={formulario.id_turno}
                      onChange={cambiarCampo}
                      required
                    >
                      <option value="">Seleccionar turno</option>
                      {turnos.map(turno => (
                        <option
                          key={turno.id_turno}
                          value={turno.id_turno}
                        >
                          {turno.hora_inicio} - {turno.hora_fin}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Cancha y complejo
                    <select
                      value={
                        formulario.nombre_cancha && formulario.id_complejo
                          ? JSON.stringify({
                              nombre: formulario.nombre_cancha,
                              complejo: formulario.id_complejo
                            })
                          : ''
                      }
                      onChange={evento => {
                        if (!evento.target.value) {
                          setFormulario(actual => ({
                            ...actual,
                            nombre_cancha: '',
                            id_complejo: ''
                          }))
                          return
                        }

                        const cancha = JSON.parse(evento.target.value)

                        setFormulario(actual => ({
                          ...actual,
                          nombre_cancha: cancha.nombre,
                          id_complejo: cancha.complejo
                        }))
                      }}
                      required
                    >
                      <option value="">Seleccionar cancha</option>
                      {canchas.map((cancha, indice) => (
                        <option
                          key={`${cancha.id_complejo}-${cancha.nombre_cancha}-${indice}`}
                          value={JSON.stringify({
                            nombre: cancha.nombre_cancha,
                            complejo: String(cancha.id_complejo)
                          })}
                        >
                          {cancha.nombre_cancha} - {cancha.nombre_complejo}
                        </option>
                      ))}
                    </select>
                  </label>

                  {partidoEditando && (
                    <label>
                      Estado
                      <select
                        name="estado"
                        value={formulario.estado}
                        onChange={cambiarCampo}
                      >
                        {obtenerEstadosPermitidos(partidoEditando.estado).map(estado => (
                          <option key={estado} value={estado}>
                            {estado}
                          </option>
                        ))}
                      </select>
                    </label>
                  )}
                </div>

                <div className="partidos-form-acciones">
                  <button
                    type="submit"
                    className="partidos-boton-principal"
                    disabled={guardando || cargandoOpciones}
                  >
                    {guardando
                      ? 'Guardando...'
                      : partidoEditando
                        ? 'Guardar cambios'
                        : 'Crear partido'}
                  </button>

                  <button
                    type="button"
                    className="partidos-boton-secundario"
                    onClick={cerrarFormulario}
                    disabled={guardando}
                  >
                    Cancelar
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </>
  )
}

export default Partidos
