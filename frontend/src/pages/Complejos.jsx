
import { useEffect, useState } from 'react'
import './Dashboard.css'

import {
  obtenerComplejos,
  obtenerCanchas,
  crearComplejo,
  crearCancha,
  eliminarComplejo,
  eliminarCancha,
  modificarComplejo,
  modificarCancha
} from '../services/api'

import { useTorneo } from '../context/TorneoContext'


function Complejos() {
  const { rolUsuario } = useTorneo()
  const esAdministrador = rolUsuario === 'administrador'

  const [complejos, setComplejos] = useState([])
  const [canchas, setCanchas] = useState([])
  const [cargando, setCargando] = useState(true)
  const [guardando, setGuardando] = useState(false)

  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')

  const [mostrarComplejo, setMostrarComplejo] = useState(false)
  const [mostrarCancha, setMostrarCancha] = useState(false)

  const [nuevoComplejo, setNuevoComplejo] = useState({
    nombre: '',
    direccion: '',
    departamento: ''
  })

  const [nuevaCancha, setNuevaCancha] = useState({
    nombre_cancha: '',
    id_complejo: '',
    superficie: 'sintético',
    techada: false
  })

  const [complejoEditando, setComplejoEditando] = useState(null)
  const [canchaEditando, setCanchaEditando] = useState(null)

  const [datosComplejoEditar, setDatosComplejoEditar] = useState({
    nombre: '',
    direccion: '',
    departamento: ''
  })

  const [datosCanchaEditar, setDatosCanchaEditar] = useState({
    superficie: 'sintético',
    techada: false
  })



  async function cargarDatos() {
    const [datosComplejos, datosCanchas] = await Promise.all([
      obtenerComplejos(),
      obtenerCanchas()
    ])

    setComplejos(datosComplejos)
    setCanchas(datosCanchas)
  }


  useEffect(() => {
    async function cargar() {
      try {
        setCargando(true)
        await cargarDatos()
      } catch (error) {
        setError(error.message)
      } finally {
        setCargando(false)
      }
    }

    cargar()
  }, [])


  function cambiarComplejo(evento) {
    const { name, value } = evento.target

    setNuevoComplejo((anterior) => ({
      ...anterior,
      [name]: value
    }))
  }


  function cambiarCancha(evento) {
    const { name, value, type, checked } = evento.target

    setNuevaCancha((anterior) => ({
      ...anterior,
      [name]: type === 'checkbox' ? checked : value
    }))
  }


  async function guardarComplejo(evento) {
    evento.preventDefault()

    if (!esAdministrador || guardando) return

    try {
      setGuardando(true)
      setError('')
      setMensaje('')

      await crearComplejo(nuevoComplejo)
      await cargarDatos()

      setNuevoComplejo({
        nombre: '',
        direccion: '',
        departamento: ''
      })

      setMostrarComplejo(false)
      setMensaje('Complejo creado correctamente.')

    } catch (error) {
      setError(error.message)
    } finally {
      setGuardando(false)
    }
  }


  async function guardarCancha(evento) {
    evento.preventDefault()

    if (!esAdministrador || guardando) return

    try {
      setGuardando(true)
      setError('')
      setMensaje('')

      await crearCancha({
        ...nuevaCancha,
        id_complejo: Number(nuevaCancha.id_complejo)
      })

      await cargarDatos()

      setNuevaCancha({
        nombre_cancha: '',
        id_complejo: '',
        superficie: 'sintético',
        techada: false
      })

      setMostrarCancha(false)
      setMensaje('Cancha creada correctamente.')

    } catch (error) {
      setError(error.message)
    } finally {
      setGuardando(false)
    }
  }
  
  async function manejarEliminarComplejo(complejo) {
    if (!esAdministrador || guardando) return

    const confirmado = window.confirm(
      `¿Seguro que querés eliminar el complejo ${complejo.nombre}?`
    )

    if (!confirmado) return

    try {
      setGuardando(true)
      setError('')
      setMensaje('')

      await eliminarComplejo(complejo.id_complejo)
      await cargarDatos()

      setMensaje('Complejo eliminado correctamente.')
    } catch (error) {
      setError(error.message)
    } finally {
      setGuardando(false)
    }
  }

  async function manejarEliminarCancha(cancha) {
    if (!esAdministrador || guardando) return

    const confirmado = window.confirm(
      `¿Seguro que querés eliminar la cancha ${cancha.nombre_cancha}?`
    )

    if (!confirmado) return

    try {
      setGuardando(true)
      setError('')
      setMensaje('')

      await eliminarCancha(
        cancha.id_complejo,
        cancha.nombre_cancha
      )

      await cargarDatos()

      setMensaje('Cancha eliminada correctamente.')
    } catch (error) {
      setError(error.message)
    } finally {
      setGuardando(false)
    }
  }


  function comenzarEditarComplejo(complejo) {
    if (!esAdministrador) return

    setComplejoEditando(complejo)
    setDatosComplejoEditar({
      nombre: complejo.nombre,
      direccion: complejo.direccion,
      departamento: complejo.departamento
    })
    setError('')
    setMensaje('')
  }

  async function guardarEdicionComplejo(evento) {
    evento.preventDefault()
    if (!esAdministrador || guardando || !complejoEditando) return

    try {
      setGuardando(true)
      setError('')
      setMensaje('')

      await modificarComplejo(
        complejoEditando.id_complejo,
        datosComplejoEditar
      )

      await cargarDatos()
      setComplejoEditando(null)
      setMensaje('Complejo modificado correctamente.')
    } catch (error) {
      setError(error.message)
    } finally {
      setGuardando(false)
    }
  }

  function comenzarEditarCancha(cancha) {
    if (!esAdministrador) return

    setCanchaEditando(cancha)
    setDatosCanchaEditar({
      superficie: cancha.superficie,
      techada: Boolean(cancha.techada)
    })
    setError('')
    setMensaje('')
  }

  async function guardarEdicionCancha(evento) {
    evento.preventDefault()
    if (!esAdministrador || guardando || !canchaEditando) return

    try {
      setGuardando(true)
      setError('')
      setMensaje('')

      await modificarCancha(
        canchaEditando.id_complejo,
        canchaEditando.nombre_cancha,
        datosCanchaEditar
      )

      await cargarDatos()
      setCanchaEditando(null)
      setMensaje('Cancha modificada correctamente.')
    } catch (error) {
      setError(error.message)
    } finally {
      setGuardando(false)
    }
  }

  return (
    <div style={{ display: 'grid', gap: '24px' }}>

      {error && (
        <p style={{ color: '#b91c1c' }}>{error}</p>
      )}

      {mensaje && (
        <p style={{ color: '#047857' }}>{mensaje}</p>
      )}

      {/* COMPLEJOS */}
      <section className="dashboard-panel" style={{ padding: '28px' }}>

        <h2>Complejos deportivos</h2>
        <p>Listado de complejos disponibles para los partidos.</p>

        {esAdministrador && (
          <button
            type="button"
            onClick={() => {
              setMostrarComplejo(!mostrarComplejo)
              setError('')
              setMensaje('')
            }}
            style={{ marginTop: '20px' }}
          >
            + Nuevo complejo
          </button>
        )}

        {mostrarComplejo && esAdministrador && (
          <form
            onSubmit={guardarComplejo}
            style={{
              display: 'grid',
              gap: '12px',
              marginTop: '20px'
            }}
          >
            <h3>Crear complejo</h3>

            <label>
              Nombre
              <input
                name="nombre"
                value={nuevoComplejo.nombre}
                onChange={cambiarComplejo}
                required
                maxLength={100}
              />
            </label>

            <label>
              Dirección
              <input
                name="direccion"
                value={nuevoComplejo.direccion}
                onChange={cambiarComplejo}
                required
              />
            </label>

            <label>
              Departamento
              <input
                name="departamento"
                value={nuevoComplejo.departamento}
                onChange={cambiarComplejo}
                required
              />
            </label>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button type="submit" disabled={guardando}>
                {guardando ? 'Guardando...' : 'Crear complejo'}
              </button>

              <button
                type="button"
                disabled={guardando}
                onClick={() => setMostrarComplejo(false)}
              >
                Cancelar
              </button>
            </div>
          </form>
        )}

        <div style={{ marginTop: '24px', overflowX: 'auto' }}>
          {cargando ? (
            <p>Cargando complejos...</p>
          ) : complejos.length === 0 ? (
            <p>No hay complejos registrados.</p>
          ) : (
            <table style={{ width: '100%', textAlign: 'left' }}>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Dirección</th>
                  <th>Departamento</th>
                  {esAdministrador && <th>Acciones</th>}
                </tr>
              </thead>

              <tbody>
                {complejos.map((complejo) => (
                  <tr key={complejo.id_complejo}>
                    <td>{complejo.nombre}</td>
                    <td>{complejo.direccion}</td>
                    <td>{complejo.departamento}</td>                    
                    {esAdministrador && (
                      <td>
                        <button
                          type="button"
                          disabled={guardando}
                          onClick={() => comenzarEditarComplejo(complejo)}
                        >
                          Modificar
                        </button>

                        <button
                          type="button"
                          disabled={guardando}
                          onClick={() => manejarEliminarComplejo(complejo)}
                        >
                          Eliminar
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>


      {complejoEditando && esAdministrador && (
        <section className="dashboard-panel" style={{ padding: '28px' }}>
          <h3>Modificar complejo</h3>

          <form
            onSubmit={guardarEdicionComplejo}
            style={{ display: 'grid', gap: '12px', marginTop: '20px' }}
          >
            <label>
              Nombre
              <input
                value={datosComplejoEditar.nombre}
                onChange={(e) => setDatosComplejoEditar({
                  ...datosComplejoEditar,
                  nombre: e.target.value
                })}
                required
              />
            </label>

            <label>
              Dirección
              <input
                value={datosComplejoEditar.direccion}
                onChange={(e) => setDatosComplejoEditar({
                  ...datosComplejoEditar,
                  direccion: e.target.value
                })}
                required
              />
            </label>

            <label>
              Departamento
              <input
                value={datosComplejoEditar.departamento}
                onChange={(e) => setDatosComplejoEditar({
                  ...datosComplejoEditar,
                  departamento: e.target.value
                })}
                required
              />
            </label>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button type="submit" disabled={guardando}>
                Guardar cambios
              </button>

              <button
                type="button"
                disabled={guardando}
                onClick={() => setComplejoEditando(null)}
              >
                Cancelar
              </button>
            </div>
          </form>
        </section>
      )}

      {/* CANCHAS */}
      <section className="dashboard-panel" style={{ padding: '28px' }}>

        <h2>Canchas</h2>
        <p>Listado de canchas de los complejos deportivos.</p>

        {esAdministrador && (
          <button
            type="button"
            onClick={() => {
              setMostrarCancha(!mostrarCancha)
              setError('')
              setMensaje('')
            }}
            style={{ marginTop: '20px' }}
          >
            + Nueva cancha
          </button>
        )}

        {mostrarCancha && esAdministrador && (
          <form
            onSubmit={guardarCancha}
            style={{
              display: 'grid',
              gap: '12px',
              marginTop: '20px'
            }}
          >
            <h3>Crear cancha</h3>

            <label>
              Nombre de la cancha
              <input
                name="nombre_cancha"
                value={nuevaCancha.nombre_cancha}
                onChange={cambiarCancha}
                required
              />
            </label>

            <label>
              Complejo deportivo
              <select
                name="id_complejo"
                value={nuevaCancha.id_complejo}
                onChange={cambiarCancha}
                required
              >
                <option value="">Seleccionar complejo</option>

                {complejos.map((complejo) => (
                  <option
                    key={complejo.id_complejo}
                    value={complejo.id_complejo}
                  >
                    {complejo.nombre}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Superficie
              <select
                name="superficie"
                value={nuevaCancha.superficie}
                onChange={cambiarCancha}
              >
                <option value="sintético">Sintético</option>
                <option value="parquet">Parquet</option>
              </select>
            </label>

            <label>
              <input
                type="checkbox"
                name="techada"
                checked={nuevaCancha.techada}
                onChange={cambiarCancha}
              />
              Cancha techada
            </label>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                type="submit"
                disabled={guardando || complejos.length === 0}
              >
                {guardando ? 'Guardando...' : 'Crear cancha'}
              </button>

              <button
                type="button"
                disabled={guardando}
                onClick={() => setMostrarCancha(false)}
              >
                Cancelar
              </button>
            </div>
          </form>
        )}

        <div style={{ marginTop: '24px', overflowX: 'auto' }}>
          {cargando ? (
            <p>Cargando canchas...</p>
          ) : canchas.length === 0 ? (
            <p>No hay canchas registradas.</p>
          ) : (
            <table style={{ width: '100%', textAlign: 'left' }}>
              <thead>
                <tr>
                  <th>Cancha</th>
                  <th>Complejo</th>
                  <th>Superficie</th>
                  <th>Techada</th>
                  {esAdministrador && <th>Acciones</th>}
                </tr>
              </thead>

              <tbody>
                {canchas.map((cancha) => (
                  <tr
                    key={`${cancha.id_complejo}-${cancha.nombre_cancha}`}
                  >
                    <td>{cancha.nombre_cancha}</td>
                    <td>{cancha.nombre_complejo}</td>
                    <td>{cancha.superficie}</td>
                    <td>{Boolean(cancha.techada) ? 'Sí' : 'No'}</td>                   
                    {esAdministrador && (
                      <td>
                        <button
                          type="button"
                          disabled={guardando}
                          onClick={() => comenzarEditarCancha(cancha)}
                        >
                          Modificar
                        </button>

                        <button
                          type="button"
                          disabled={guardando}
                          onClick={() => manejarEliminarCancha(cancha)}
                        >
                          Eliminar
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

      </section>
      
      {canchaEditando && esAdministrador && (
        <section className="dashboard-panel" style={{ padding: '28px' }}>
          <h3>Modificar cancha: {canchaEditando.nombre_cancha}</h3>

          <form
            onSubmit={guardarEdicionCancha}
            style={{ display: 'grid', gap: '12px', marginTop: '20px' }}
          >
            <label>
              Superficie
              <select
                value={datosCanchaEditar.superficie}
                onChange={(e) => setDatosCanchaEditar({
                  ...datosCanchaEditar,
                  superficie: e.target.value
                })}
              >
                <option value="sintético">Sintético</option>
                <option value="parquet">Parquet</option>
              </select>
            </label>

            <label>
              <input
                type="checkbox"
                checked={datosCanchaEditar.techada}
                onChange={(e) => setDatosCanchaEditar({
                  ...datosCanchaEditar,
                  techada: e.target.checked
                })}
              />
              Cancha techada
            </label>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button type="submit" disabled={guardando}>
                Guardar cambios
              </button>

              <button
                type="button"
                disabled={guardando}
                onClick={() => setCanchaEditando(null)}
              >
                Cancelar
              </button>
            </div>
          </form>
        </section>
      )}

    </div>
  )
}

export default Complejos
