
import './Planteles.css'
import { useEffect, useState } from 'react'

import { useTorneo } from '../context/TorneoContext'

import {
  obtenerEquipos,
  obtenerPlantel,
  agregarJugadorPlantel,
  quitarJugadorPlantel,
  modificarCamiseta,
  cambiarCapitan
} from '../services/api'

function Planteles() {
  const { idTorneo } = useTorneo()

  const [equipos, setEquipos] = useState([])
  const [idEquipo, setIdEquipo] = useState('')
  const [plantel, setPlantel] = useState([])

  const [cargandoEquipos, setCargandoEquipos] = useState(true)
  const [cargandoPlantel, setCargandoPlantel] = useState(false)

  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')

  const [ciJugador, setCiJugador] = useState('')
  const [numeroCamiseta, setNumeroCamiseta] = useState('')

  const [camisetasEditando, setCamisetasEditando] = useState({})

  const [procesando, setProcesando] = useState(false)

  const equipoSeleccionado = equipos.find(
    (equipo) => String(equipo.id_equipo) === String(idEquipo)
  )

  const ciCapitan = equipoSeleccionado?.ci_capitan

  //obtenemos los equipos del torneo seleccionado
  useEffect(() => {
    async function cargarEquipos() {
      try {
        setCargandoEquipos(true)
        setError('')
        setMensaje('')
        setEquipos([])
        setPlantel([])
        setIdEquipo('')

        const datos = await obtenerEquipos(idTorneo)

        setEquipos(datos)
      } catch (error) {
        console.error('Error al obtener los equipos:', error)
        setError(error.message)
      } finally {
        setCargandoEquipos(false)
      }
    }

    if (idTorneo) {
      cargarEquipos()
    }
  }, [idTorneo])

  //obtenemos los integrantes del equipo seleccionado
  useEffect(() => {
    async function cargarPlantel() {
      try {
        setCargandoPlantel(true)
        setError('')
        setMensaje('')
        setPlantel([])
        setCamisetasEditando({})

        const datos = await obtenerPlantel(idEquipo)

        setPlantel(datos)
      } catch (error) {
        console.error('Error al obtener el plantel:', error)
        setError(error.message)
      } finally {
        setCargandoPlantel(false)
      }
    }

    if (idEquipo) {
      cargarPlantel()
    } else {
      setPlantel([])
    }
  }, [idEquipo])

  //volvemos a consultar el plantel después de una modificación
  async function actualizarPlantel() {
    const datos = await obtenerPlantel(idEquipo)
    setPlantel(datos)
  }

  //agregamos un jugador al plantel
  async function manejarAgregarJugador(e) {
    e.preventDefault()

    setError('')
    setMensaje('')

    if (!/^\d{8}$/.test(ciJugador)) {
      setError('La CI debe tener exactamente 8 números')
      return
    }

    if (!numeroCamiseta || Number(numeroCamiseta) <= 0) {
      setError('Ingresá un número de camiseta positivo')
      return
    }

    try {
      setProcesando(true)

      const respuesta = await agregarJugadorPlantel(idEquipo, {
        ci_jugador: ciJugador,
        numero_camiseta: Number(numeroCamiseta)
      })

      setMensaje(respuesta.mensaje || 'Jugador agregado correctamente')

      setCiJugador('')
      setNumeroCamiseta('')

      await actualizarPlantel()
    } catch (error) {
      setError(error.message)
    } finally {
      setProcesando(false)
    }
  }

  //quitamos un jugador del plantel
  async function manejarQuitarJugador(ci) {
    const jugador = plantel.find(
      (item) => String(item.ci_jugador) === String(ci)
    )

    if (!jugador) return

    if (String(ci) === String(ciCapitan)) {
      setError('Primero tenés que designar otro capitán')
      return
    }

    if (plantel.length <= 5) {
      setError('El equipo debe tener al menos 5 jugadores')
      return
    }

    const confirmar = window.confirm(
      `¿Seguro que querés quitar a ${jugador.nombre} ${jugador.apellido} del plantel?`
    )

    if (!confirmar) return

    try {
      setProcesando(true)
      setError('')
      setMensaje('')

      const respuesta = await quitarJugadorPlantel(idEquipo, ci)

      setMensaje(respuesta.mensaje || 'Jugador quitado correctamente')

      await actualizarPlantel()
    } catch (error) {
      setError(error.message)
    } finally {
      setProcesando(false)
    }
  }

  //modificamos el número de camiseta
  async function manejarModificarCamiseta(ci) {
    const nuevoNumero = camisetasEditando[ci]

    if (!nuevoNumero || Number(nuevoNumero) <= 0) {
      setError('El número de camiseta debe ser positivo')
      return
    }

    try {
      setProcesando(true)
      setError('')
      setMensaje('')

      const respuesta = await modificarCamiseta(
        idEquipo,
        ci,
        Number(nuevoNumero)
      )

      setMensaje(respuesta.mensaje || 'Camiseta modificada correctamente')

      await actualizarPlantel()

      setCamisetasEditando({})
    } catch (error) {
      setError(error.message)
    } finally {
      setProcesando(false)
    }
  }

  //cambiamos el capitán por otro integrante del equipo
  async function manejarCambiarCapitan(ci) {
    const jugador = plantel.find(
      (item) => String(item.ci_jugador) === String(ci)
    )

    if (!jugador) return

    const confirmar = window.confirm(
      `¿Querés designar a ${jugador.nombre} ${jugador.apellido} como nuevo capitán?`
    )

    if (!confirmar) return

    try {
      setProcesando(true)
      setError('')
      setMensaje('')

      const respuesta = await cambiarCapitan(idEquipo, ci)

      setMensaje(respuesta.mensaje || 'Capitán cambiado correctamente')

      //actualizamos los equipos para obtener el nuevo capitán
      const datosEquipos = await obtenerEquipos(idTorneo)
      setEquipos(datosEquipos)

      await actualizarPlantel()
    } catch (error) {
      setError(error.message)
    } finally {
      setProcesando(false)
    }
  }

  return (
    <div className="planteles-pagina">

      <div className="planteles-encabezado">
        <div>
          <h2>Gestión de planteles</h2>
          <p>
            Administrá los integrantes, las camisetas y los capitanes de cada equipo.
          </p>
        </div>
      </div>

      {error && (
        <div className="planteles-mensaje planteles-error">
          {error}
        </div>
      )}

      {mensaje && (
        <div className="planteles-mensaje planteles-exito">
          {mensaje}
        </div>
      )}

      <section className="planteles-panel">

        <div className="planteles-panel-encabezado">
          <h3>Seleccionar equipo</h3>
          <p>Elegí el equipo cuyo plantel querés administrar.</p>
        </div>

        {cargandoEquipos ? (
          <p>Cargando equipos...</p>
        ) : equipos.length === 0 ? (
          <p>No hay equipos registrados para este torneo.</p>
        ) : (
          <select
            className="planteles-selector"
            value={idEquipo}
            onChange={(e) => {
              setIdEquipo(e.target.value)
              setError('')
              setMensaje('')
            }}
          >
            <option value="">Seleccioná un equipo</option>

            {equipos.map((equipo) => (
              <option
                key={equipo.id_equipo}
                value={equipo.id_equipo}
              >
                {equipo.nombre_equipo || equipo.nombre}
                {equipo.nombre_facultad || equipo.facultad
                  ? ` - ${equipo.nombre_facultad || equipo.facultad}`
                  : ''}
              </option>
            ))}
          </select>
        )}
      </section>

      {equipoSeleccionado && (
        <>
          <section className="planteles-panel planteles-resumen">

            <div>
              <small>Equipo seleccionado</small>
              <h3>
                {equipoSeleccionado.nombre_equipo || equipoSeleccionado.nombre}
              </h3>
            </div>

            <div>
              <small>Facultad</small>
              <strong>
                {equipoSeleccionado.nombre_facultad ||
                  equipoSeleccionado.facultad ||
                  'No especificada'}
              </strong>
            </div>

            <div>
              <small>Integrantes</small>
              <strong>{plantel.length} / 10</strong>
            </div>

            <div>
              <small>Capitán</small>
              <strong>{ciCapitan || 'No definido'}</strong>
            </div>

          </section>

          <section className="planteles-panel">

            <div className="planteles-panel-encabezado">
              <h3>Integrantes del equipo</h3>
              <p>
                Desde acá podés administrar los jugadores que forman parte del plantel.
              </p>
            </div>

            {cargandoPlantel ? (
              <p>Cargando integrantes...</p>
            ) : plantel.length === 0 ? (
              <p>Este equipo todavía no tiene integrantes registrados.</p>
            ) : (
              <div className="planteles-tabla-contenedor">
                <table className="planteles-tabla">
                  <thead>
                    <tr>
                      <th>Camiseta</th>
                      <th>Nombre</th>
                      <th>Apellido</th>
                      <th>CI</th>
                      <th>Tipo</th>
                      <th>Capitán</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>

                  <tbody>
                    {plantel.map((jugador) => {
                      const esCapitan =
                        String(jugador.ci_jugador) === String(ciCapitan)

                      return (
                        <tr key={jugador.ci_jugador}>

                          <td>
                            <div className="planteles-camiseta">
                              <input
                                type="number"
                                min="1"
                                value={
                                  camisetasEditando[jugador.ci_jugador] ??
                                  jugador.numero_camiseta
                                }
                                onChange={(e) =>
                                  setCamisetasEditando({
                                    ...camisetasEditando,
                                    [jugador.ci_jugador]: e.target.value
                                  })
                                }
                                disabled={procesando}
                              />

                              <button
                                className="planteles-boton-guardar"
                                onClick={() =>
                                  manejarModificarCamiseta(jugador.ci_jugador)
                                }
                                disabled={
                                  procesando ||
                                  camisetasEditando[jugador.ci_jugador] === undefined ||
                                  Number(camisetasEditando[jugador.ci_jugador]) ===
                                    Number(jugador.numero_camiseta)
                                }
                              >
                                Guardar
                              </button>
                            </div>
                          </td>

                          <td>{jugador.nombre}</td>
                          <td>{jugador.apellido}</td>
                          <td>{jugador.ci_jugador}</td>
                          <td>{jugador.tipo}</td>

                          <td>
                            {esCapitan ? (
                              <span className="planteles-etiqueta-capitan">
                                Capitán
                              </span>
                            ) : (
                              <button
                                className="planteles-boton-secundario"
                                onClick={() =>
                                  manejarCambiarCapitan(jugador.ci_jugador)
                                }
                                disabled={procesando}
                              >
                                Designar
                              </button>
                            )}
                          </td>

                          <td>
                            <button
                              className="planteles-boton-eliminar"
                              onClick={() =>
                                manejarQuitarJugador(jugador.ci_jugador)
                              }
                              disabled={
                                procesando ||
                                esCapitan ||
                                plantel.length <= 5
                              }
                              title={
                                esCapitan
                                  ? 'Primero designá otro capitán'
                                  : plantel.length <= 5
                                    ? 'El equipo debe tener al menos 5 jugadores'
                                    : 'Quitar jugador'
                              }
                            >
                              Quitar
                            </button>
                          </td>

                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}

          </section>

          <section className="planteles-panel">

            <div className="planteles-panel-encabezado">
              <h3>Agregar jugador</h3>
              <p>
                Ingresá la CI de un jugador registrado y asignale un número de camiseta.
              </p>
            </div>

            <form
              className="planteles-formulario"
              onSubmit={manejarAgregarJugador}
            >

              <div className="planteles-campo">
                <label htmlFor="ci-jugador">Cédula de identidad</label>
                <input
                  id="ci-jugador"
                  type="text"
                  inputMode="numeric"
                  maxLength="8"
                  placeholder="Ej. 12345678"
                  value={ciJugador}
                  onChange={(e) =>
                    setCiJugador(e.target.value.replace(/\D/g, '').slice(0, 8))
                  }
                  required
                />
              </div>

              <div className="planteles-campo">
                <label htmlFor="numero-camiseta">Número de camiseta</label>
                <input
                  id="numero-camiseta"
                  type="number"
                  min="1"
                  placeholder="Ej. 10"
                  value={numeroCamiseta}
                  onChange={(e) => setNumeroCamiseta(e.target.value)}
                  required
                />
              </div>

              <button
                type="submit"
                className="planteles-boton-agregar"
                disabled={procesando || plantel.length >= 10}
              >
                {procesando ? 'Procesando...' : 'Agregar jugador'}
              </button>

            </form>

            {plantel.length >= 10 && (
              <p className="planteles-ayuda">
                El equipo ya alcanzó el máximo de 10 integrantes.
              </p>
            )}

          </section>
        </>
      )}

    </div>
  )
}

export default Planteles
