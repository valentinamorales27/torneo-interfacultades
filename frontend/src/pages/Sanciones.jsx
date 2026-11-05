
import { useEffect, useState } from 'react'
import { obtenerSanciones, crearSancion } from '../services/api'
import './Sanciones.css'

function Sanciones() {
  const [sanciones, setSanciones] = useState([])
  const [ciJugador, setCiJugador] = useState('')
  const [idTorneo, setIdTorneo] = useState('1')
  const [numeroFecha, setNumeroFecha] = useState('')
  const [cantidadFechas, setCantidadFechas] = useState('1')
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [cargando, setCargando] = useState(false)

  useEffect(() => {
    cargarSanciones()
  }, [])

  async function cargarSanciones() {
    try {
      setCargando(true)
      setError('')
      const datos = await obtenerSanciones()
      setSanciones(Array.isArray(datos) ? datos : datos.sanciones || [])
    } catch (error) {
      setError(error.message)
    } finally {
      setCargando(false)
    }
  }

  async function handleCrearSancion(e) {
    e.preventDefault()

    try {
      setError('')
      setMensaje('')

      await crearSancion({
        ci_jugador: ciJugador,
        id_torneo: Number(idTorneo),
        numero_fecha_inicio: Number(numeroFecha),
        cantidad_fechas: Number(cantidadFechas)
      })

      setCiJugador('')
      setNumeroFecha('')
      setCantidadFechas('1')
      setMensaje('Sanción registrada correctamente.')
      await cargarSanciones()
    } catch (error) {
      setError(error.message)
    }
  }

  return (
    <div className="sanciones-page">
      <div className="sanciones-header">
        <div>
          <h1>Sanciones</h1>
          <p>Consulta y registro de sanciones de jugadores.</p>
        </div>
      </div>

      {error && <div className="sanciones-alerta error">{error}</div>}
      {mensaje && <div className="sanciones-alerta exito">{mensaje}</div>}

      <section className="sanciones-panel">
        <h2>Registrar sanción disciplinaria</h2>

        <form className="sanciones-form" onSubmit={handleCrearSancion}>
          <div>
            <label>Cédula del jugador</label>
            <input
              type="text"
              value={ciJugador}
              onChange={(e) => setCiJugador(e.target.value)}
              placeholder="Ingresar cédula"
              required
            />
          </div>

          <div>
            <label>ID del torneo</label>
            <input
              type="number"
              min="1"
              value={idTorneo}
              onChange={(e) => setIdTorneo(e.target.value)}
              required
            />
          </div>

          <div>
            <label>Fecha desde la que se aplica</label>
            <input
              type="number"
              min="1"
              value={numeroFecha}
              onChange={(e) => setNumeroFecha(e.target.value)}
              placeholder="Número de fecha"
              required
            />
          </div>

          <div>
            <label>Cantidad de fechas</label>
            <input
              type="number"
              min="1"
              value={cantidadFechas}
              onChange={(e) => setCantidadFechas(e.target.value)}
              required
            />
          </div>

          <button type="submit">Registrar sanción</button>
        </form>
      </section>

      <section className="sanciones-panel">
        <div className="sanciones-titulo">
          <h2>Todas las sanciones</h2>
          <button onClick={cargarSanciones}>Actualizar</button>
        </div>

        {cargando ? (
          <p className="sanciones-vacio">Cargando sanciones...</p>
        ) : sanciones.length === 0 ? (
          <p className="sanciones-vacio">No hay sanciones registradas.</p>
        ) : (
          <div className="sanciones-tabla-contenedor">
            <table className="sanciones-tabla">
              <thead>
                <tr>
                  <th>Jugador</th>
                  <th>Cédula</th>
                  <th>Torneo</th>
                  <th>Motivo</th>
                  <th>Fecha de inicio</th>
                  <th>Fechas</th>
                </tr>
              </thead>
              <tbody>
                {sanciones.map((sancion) => (
                  <tr key={sancion.id_sancion}>
                    <td>{sancion.nombre} {sancion.apellido}</td>
                    <td>{sancion.ci_jugador}</td>
                    <td>{sancion.nombre_torneo || sancion.id_torneo}</td>
                    <td>{sancion.motivo}</td>
                    <td>{sancion.numero_fecha_inicio}</td>
                    <td>{sancion.cantidad_fechas}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}

export default Sanciones
