
import { useEffect, useState } from 'react'
import { useTorneo } from '../context/TorneoContext'

import {
  obtenerJugadoresFacultadTipo,
  obtenerJugadoresSinPlanilla,
  obtenerJugadoresMasPartidos,
  obtenerJugadores,
  crearJugador,
  modificarJugador,
  eliminarJugador
} from '../services/api'

import ReporteTabla from '../components/ReporteTabla'


const FORMULARIO_VACIO = {
  ci: '',
  nombre: '',
  apellido: '',
  email: '',
  fecha_nacimiento: '',
  tipo: 'grado',
  id_facultad: ''
}

function Jugadores() {
    const {idTorneo}=useTorneo();
  const [reportes, setReportes] = useState({
    facultad: { datos: [], cargando: true, error: '' },
    sinPlanilla: { datos: [], cargando: true, error: '' },
    masPartidos: { datos: [], cargando: true, error: '' }
  })

  const [mostrarTodos, setMostrarTodos] = useState(false)
  const [jugadores, setJugadores] = useState([])
  const [cargandoJugadores, setCargandoJugadores] = useState(false)
  const [errorJugadores, setErrorJugadores] = useState('')

  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const [modoEdicion, setModoEdicion] = useState(false)
  const [formulario, setFormulario] = useState(FORMULARIO_VACIO)

  const [guardando, setGuardando] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [errorFormulario, setErrorFormulario] = useState('')

    // Cargar reportes
  useEffect(() => {
    let activo = true

    async function cargarReportes() {
      if (!idTorneo) {
        setReportes({
          facultad: { datos: [], cargando: false, error: '' },
          sinPlanilla: { datos: [], cargando: false, error: '' },
          masPartidos: { datos: [], cargando: false, error: '' }
        })
        return
      }

      setReportes({
        facultad: { datos: [], cargando: true, error: '' },
        sinPlanilla: { datos: [], cargando: true, error: '' },
        masPartidos: { datos: [], cargando: true, error: '' }
      })

      const consultas = [
        ['facultad', obtenerJugadoresFacultadTipo(idTorneo)],
        ['sinPlanilla', obtenerJugadoresSinPlanilla(idTorneo)],
        ['masPartidos', obtenerJugadoresMasPartidos(idTorneo)]
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
  }, [idTorneo])

  // Obtener todos los jugadores
  async function cargarTodosLosJugadores() {
    try {
      setCargandoJugadores(true)
      setErrorJugadores('')

      const datos = await obtenerJugadores()
      setJugadores(datos)
    } catch (error) {
      setErrorJugadores(error.message)
    } finally {
      setCargandoJugadores(false)
    }
  }

  // Mostrar u ocultar el listado
  async function alternarVista() {
    if (!mostrarTodos && jugadores.length === 0) {
      await cargarTodosLosJugadores()
    }

    setMostrarTodos(!mostrarTodos)
    setMostrarFormulario(false)
    setMensaje('')
    setErrorFormulario('')
  }

  // Actualizar los campos del formulario
  function manejarCambio(evento) {
    const { name, value } = evento.target

    setFormulario({
      ...formulario,
      [name]: value
    })
  }

  // Abrir formulario para crear
  function abrirFormularioNuevo() {
    setFormulario(FORMULARIO_VACIO)
    setModoEdicion(false)
    setMostrarFormulario(true)
    setMensaje('')
    setErrorFormulario('')
  }

  // Abrir formulario para modificar
  function abrirFormularioEdicion(jugador) {
    setFormulario({
      ci: String(jugador.ci),
      nombre: jugador.nombre || '',
      apellido: jugador.apellido || '',
      email: jugador.email || '',
      fecha_nacimiento: jugador.fecha_nacimiento
        ? String(jugador.fecha_nacimiento).substring(0, 10)
        : '',
      tipo: jugador.tipo || 'grado',
      id_facultad: String(jugador.id_facultad)
    })

    setModoEdicion(true)
    setMostrarFormulario(true)
    setMensaje('')
    setErrorFormulario('')
  }

  // Cerrar formulario
  function cerrarFormulario() {
    setMostrarFormulario(false)
    setFormulario(FORMULARIO_VACIO)
    setErrorFormulario('')
  }

  // Crear o modificar jugador
  async function manejarSubmit(evento) {
    evento.preventDefault()

    try {
      setGuardando(true)
      setErrorFormulario('')
      setMensaje('')

      const datosJugador = {
        nombre: formulario.nombre.trim(),
        apellido: formulario.apellido.trim(),
        email: formulario.email.trim(),
        fecha_nacimiento: formulario.fecha_nacimiento,
        tipo: formulario.tipo,
        id_facultad: Number(formulario.id_facultad)
      }

      if (modoEdicion) {
        await modificarJugador(formulario.ci, datosJugador)
        setMensaje('Jugador modificado correctamente.')
      } else {
        await crearJugador({
          ci: formulario.ci.trim(),
          ...datosJugador
        })

        setMensaje('Jugador registrado correctamente.')
      }

      cerrarFormulario()
      await cargarTodosLosJugadores()
    } catch (error) {
      setErrorFormulario(error.message)
    } finally {
      setGuardando(false)
    }
  }

  // Eliminar jugador
  async function manejarEliminar(jugador) {
    const confirmar = window.confirm(
      `¿Estás seguro de que querés eliminar a ${jugador.nombre} ${jugador.apellido}?`
    )

    if (!confirmar) return

    try {
      setErrorJugadores('')
      setMensaje('')

      await eliminarJugador(jugador.ci)

      setMensaje('Jugador eliminado correctamente.')

      await cargarTodosLosJugadores()
    } catch (error) {
      setErrorJugadores(error.message)
    }
  }

  return (
    <>
      <div className="dashboard-title-row">
        <div>
          <h2>Jugadores</h2>
          <p>Información y estadísticas de los jugadores del torneo.</p>
        </div>
      </div>

      <div className="jugadores-acciones">
        <button
          type="button"
          className="dashboard-action-button"
          onClick={alternarVista}
        >
          {mostrarTodos ? 'Ver reportes' : 'Todos los jugadores'}
        </button>
      </div>

      {mostrarTodos ? (
        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <h3>Todos los jugadores</h3>
              <p>Listado y administración de los jugadores registrados.</p>
            </div>

            <button
              type="button"
              className="dashboard-action-button"
              onClick={abrirFormularioNuevo}
            >
              + Nuevo jugador
            </button>
          </div>

          <div className="panel-divider" />

          {mensaje && (
            <p className="crud-mensaje">{mensaje}</p>
          )}

          {cargandoJugadores ? (
            <p className="matches-message">Cargando jugadores...</p>
          ) : errorJugadores ? (
            <p className="matches-message matches-error">
              No se pudieron cargar los jugadores: {errorJugadores}
            </p>
          ) : jugadores.length === 0 ? (
            <p className="matches-message">
              No hay jugadores registrados.
            </p>
          ) : (
            <>
              <p className="equipos-contador">
                {jugadores.length} jugadores registrados
              </p>

              <div className="reporte-table-container">
                <table className="reporte-table">
                  <thead>
                    <tr>
                      <th>CI</th>
                      <th>Nombre</th>
                      <th>Apellido</th>
                      <th>Email</th>
                      <th>Fecha de nacimiento</th>
                      <th>Tipo</th>
                      <th>Facultad</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>

                  <tbody>
                    {jugadores.map(jugador => (
                      <tr key={jugador.ci}>
                        <td>{jugador.ci}</td>
                        <td>{jugador.nombre}</td>
                        <td>{jugador.apellido}</td>
                        <td>{jugador.email}</td>
                        <td>{jugador.fecha_nacimiento}</td>
                        <td>{jugador.tipo}</td>
                        <td>{jugador.facultad}</td>
                        <td>
                          <div className="crud-acciones">
                            <button
                              type="button"
                              className="crud-boton-editar"
                              onClick={() => abrirFormularioEdicion(jugador)}
                            >
                              Editar
                            </button>

                            <button
                              type="button"
                              className="crud-boton-eliminar"
                              onClick={() => manejarEliminar(jugador)}
                            >
                              Eliminar
                            </button>
                          </div>
                        </td>
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
            titulo="Jugadores sin planilla"
            descripcion="Jugadores inscriptos que todavía no participaron en ningún partido."
            columnas={[
              { key: 'ci', titulo: 'Cédula' },
              { key: 'nombre', titulo: 'Nombre' },
              { key: 'apellido', titulo: 'Apellido' },
              { key: 'tipo', titulo: 'Tipo' },
              { key: 'equipo', titulo: 'Equipo' }
            ]}
            {...reportes.sinPlanilla}
            mensajeVacio="Todos los jugadores registrados participaron en algún partido."
          />

          <ReporteTabla
            titulo="Jugadores con más partidos"
            descripcion="Ranking de jugadores según la cantidad de partidos disputados."
            columnas={[
              { key: 'ci', titulo: 'Cédula' },
              { key: 'nombre', titulo: 'Nombre' },
              { key: 'apellido', titulo: 'Apellido' },
              { key: 'equipo', titulo: 'Equipo' },
              { key: 'facultad', titulo: 'Facultad' },
              { key: 'partidos_disputados', titulo: 'Partidos' }
            ]}
            {...reportes.masPartidos}
            mensajeVacio="Todavía no hay partidos disputados."
          />

          <ReporteTabla
            titulo="Jugadores por facultad y tipo"
            descripcion="Distribución de los participantes según su facultad y categoría."
            columnas={[
              { key: 'facultad', titulo: 'Facultad' },
              { key: 'tipo', titulo: 'Tipo de jugador' },
              { key: 'cantidad_jugadores', titulo: 'Cantidad' }
            ]}
            {...reportes.facultad}
            mensajeVacio="No hay jugadores registrados para mostrar."
          />
        </>
      )}

      {/* MODAL DE CREACIÓN Y EDICIÓN */}
      {mostrarFormulario && (
        <div
          className="crud-modal-fondo"
          onClick={cerrarFormulario}
        >
          <div
            className="crud-modal"
            onClick={evento => evento.stopPropagation()}
          >
            <div className="crud-modal-encabezado">
              <div>
                <h3>
                  {modoEdicion ? 'Modificar jugador' : 'Registrar jugador'}
                </h3>
                <p>Completá los datos del jugador.</p>
              </div>

              <button
                type="button"
                className="crud-modal-cerrar"
                onClick={cerrarFormulario}
              >
                ×
              </button>
            </div>

            <form onSubmit={manejarSubmit}>
              <div className="crud-formulario-grid">

                <label>
                  Cédula
                  <input
                    type="text"
                    name="ci"
                    value={formulario.ci}
                    onChange={manejarCambio}
                    required
                    maxLength="8"
                    disabled={modoEdicion}
                  />
                </label>

                <label>
                  Nombre
                  <input
                    type="text"
                    name="nombre"
                    value={formulario.nombre}
                    onChange={manejarCambio}
                    required
                  />
                </label>

                <label>
                  Apellido
                  <input
                    type="text"
                    name="apellido"
                    value={formulario.apellido}
                    onChange={manejarCambio}
                    required
                  />
                </label>

                <label>
                  Email
                  <input
                    type="email"
                    name="email"
                    value={formulario.email}
                    onChange={manejarCambio}
                    required
                  />
                </label>

                <label>
                  Fecha de nacimiento
                  <input
                    type="date"
                    name="fecha_nacimiento"
                    value={formulario.fecha_nacimiento}
                    onChange={manejarCambio}
                    required
                  />
                </label>

                <label>
                  Tipo de jugador
                  <select
                    name="tipo"
                    value={formulario.tipo}
                    onChange={manejarCambio}
                    required
                  >
                    <option value="grado">Grado</option>
                    <option value="posgrado">Posgrado</option>
                    <option value="docente">Docente</option>
                    <option value="funcionario">Funcionario</option>
                  </select>
                </label>

                <label>
                  ID de facultad
                  <input
                    type="number"
                    name="id_facultad"
                    value={formulario.id_facultad}
                    onChange={manejarCambio}
                    min="1"
                    step="1"
                    required
                  />
                </label>

              </div>

              {errorFormulario && (
                <p className="crud-error">{errorFormulario}</p>
              )}

              <div className="crud-formulario-acciones">
                <button
                  type="submit"
                  className="dashboard-action-button"
                  disabled={guardando}
                >
                  {guardando
                    ? 'Guardando...'
                    : modoEdicion
                      ? 'Guardar cambios'
                      : 'Registrar jugador'}
                </button>

                <button
                  type="button"
                  className="crud-boton-cancelar"
                  onClick={cerrarFormulario}
                  disabled={guardando}
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  )
}

export default Jugadores
