import { useEffect, useState } from 'react'
import {
  obtenerEquipos,
  obtenerFacultades,
  consultarSesion,
  crearEquipo,
  modificarEquipo,
  eliminarEquipo
} from '../services/api'
import { useTorneo } from '../context/TorneoContext'
import './Equipos.css'

function Equipos() {
  const { idTorneo } = useTorneo()

  const [equipos, setEquipos] = useState([])
  const [facultades, setFacultades] = useState([])
  const [esAdministrador, setEsAdministrador] = useState(false)

  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')

  const [modalAbierto, setModalAbierto] = useState(false)
  const [equipoEditando, setEquipoEditando] = useState(null)
  const [guardando, setGuardando] = useState(false)
  const [errorFormulario, setErrorFormulario] = useState('')

  const [formulario, setFormulario] = useState({
    nombre: '',
    id_facultad: '',
    ci_capitan: '',
    numero_camiseta_capitan: ''
  })

  //cargamos los equipos del torneo seleccionado
  async function cargarEquipos() {
    try {
      setCargando(true)
      setError('')

      const datos = await obtenerEquipos(idTorneo)
      setEquipos(datos)
    } catch (error) {
      setError(error.message)
    } finally {
      setCargando(false)
    }
  }

  //consultamos quien inicio sesion
  async function cargarSesion() {
    try {
      const sesion = await consultarSesion()
      setEsAdministrador(sesion.rol === 'administrador')
    } catch {
      setEsAdministrador(false)
    }
  }

  //cargamos las facultades para el formulario
  async function cargarFacultades() {
    try {
      const datos = await obtenerFacultades()
      setFacultades(datos)
    } catch (error) {
      setError(error.message)
    }
  }

  useEffect(() => {
    if (idTorneo) {
      cargarEquipos()
    } else {
      setEquipos([])
      setCargando(false)
    }
  }, [idTorneo])

  useEffect(() => {
    cargarSesion()
  }, [])

  function abrirCrear() {
    setEquipoEditando(null)
    setFormulario({
      nombre: '',
      id_facultad: '',
      ci_capitan: '',
      numero_camiseta_capitan: ''
    })
    setErrorFormulario('')
    setMensaje('')
    setModalAbierto(true)
    cargarFacultades()
  }

  function abrirEditar(equipo) {
    setEquipoEditando(equipo)
    setFormulario({
      nombre: equipo.nombre,
      id_facultad: '',
      ci_capitan: '',
      numero_camiseta_capitan: ''
    })
    setErrorFormulario('')
    setMensaje('')
    setModalAbierto(true)
  }

  function cerrarModal() {
    setModalAbierto(false)
    setEquipoEditando(null)
    setErrorFormulario('')
  }

  function cambiarFormulario(evento) {
    const { name, value } = evento.target

    setFormulario({
      ...formulario,
      [name]: value
    })
  }

  //guardamos el equipo nuevo o los cambios del equipo
  async function guardarEquipo(evento) {
    evento.preventDefault()

    try {
      setGuardando(true)
      setErrorFormulario('')
      setMensaje('')

      if (equipoEditando) {
        await modificarEquipo(equipoEditando.id_equipo, {
          nombre: formulario.nombre
        })
        setMensaje('Equipo modificado correctamente.')
      } else {
        await crearEquipo({
          nombre: formulario.nombre,
          id_torneo: idTorneo,
          id_facultad: Number(formulario.id_facultad),
          ci_capitan: formulario.ci_capitan,
          numero_camiseta_capitan: Number(formulario.numero_camiseta_capitan)
        })
        setMensaje('Equipo creado correctamente.')
      }

      cerrarModal()
      await cargarEquipos()
    } catch (error) {
      setErrorFormulario(error.message)
    } finally {
      setGuardando(false)
    }
  }

  //eliminamos el equipo seleccionado
  async function borrarEquipo(equipo) {
    const confirmar = window.confirm(
      `¿Seguro que desea eliminar el equipo ${equipo.nombre}?`
    )

    if (!confirmar) return

    try {
      setError('')
      setMensaje('')

      await eliminarEquipo(equipo.id_equipo)
      setMensaje('Equipo eliminado correctamente.')
      await cargarEquipos()
    } catch (error) {
      setError(error.message)
    }
  }

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

        {esAdministrador && (
          <div className="jugadores-acciones">
            <button
              className="dashboard-action-button"
              onClick={abrirCrear}
            >
              + Nuevo equipo
            </button>
          </div>
        )}

        <div className="panel-divider" />

        {mensaje && (
          <p className="crud-mensaje">{mensaje}</p>
        )}

        {error && (
          <p className="matches-message matches-error">
            {error}
          </p>
        )}

        {cargando ? (
          <p className="matches-message">Cargando equipos...</p>
        ) : error && equipos.length === 0 ? (
          null
        ) : equipos.length === 0 ? (
          <p className="matches-message">
            No hay equipos registrados en este torneo.
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
                    {esAdministrador && <th>Acciones</th>}
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

                      {esAdministrador && (
                        <td>
                          <div className="crud-acciones">
                            <button
                              className="crud-boton-editar"
                              onClick={() => abrirEditar(equipo)}
                            >
                              Editar
                            </button>

                            <button
                              className="crud-boton-eliminar"
                              onClick={() => borrarEquipo(equipo)}
                            >
                              Eliminar
                            </button>
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

      {modalAbierto && (
        <div className="crud-modal-fondo">
          <div className="crud-modal">

            <div className="crud-modal-encabezado">
              <div>
                <h3>
                  {equipoEditando ? 'Modificar equipo' : 'Nuevo equipo'}
                </h3>
                <p>
                  {equipoEditando
                    ? 'Modificá el nombre del equipo.'
                    : 'Ingresá los datos del equipo y su capitán.'}
                </p>
              </div>

              <button
                className="crud-modal-cerrar"
                onClick={cerrarModal}
                type="button"
              >
                ×
              </button>
            </div>

            <form onSubmit={guardarEquipo}>
              <div className="crud-formulario-grid">

                <label>
                  Nombre del equipo
                  <input
                    type="text"
                    name="nombre"
                    value={formulario.nombre}
                    onChange={cambiarFormulario}
                    required
                  />
                </label>

                {!equipoEditando && (
                  <>
                    <label>
                      Facultad
                      <select
                        name="id_facultad"
                        value={formulario.id_facultad}
                        onChange={cambiarFormulario}
                        required
                      >
                        <option value="">Seleccionar facultad</option>
                        {facultades.map(facultad => (
                          <option
                            key={facultad.id_facultad}
                            value={facultad.id_facultad}
                          >
                            {facultad.nombre}
                          </option>
                        ))}
                      </select>
                    </label>

                    <label>
                      Cédula del capitán
                      <input
                        type="text"
                        name="ci_capitan"
                        value={formulario.ci_capitan}
                        onChange={cambiarFormulario}
                        maxLength="8"
                        required
                      />
                    </label>

                    <label>
                      Número de camiseta del capitán
                      <input
                        type="number"
                        name="numero_camiseta_capitan"
                        value={formulario.numero_camiseta_capitan}
                        onChange={cambiarFormulario}
                        min="1"
                        required
                      />
                    </label>
                  </>
                )}

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
                    : equipoEditando
                      ? 'Guardar cambios'
                      : 'Crear equipo'}
                </button>

                <button
                  type="button"
                  className="crud-boton-cancelar"
                  onClick={cerrarModal}
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

export default Equipos