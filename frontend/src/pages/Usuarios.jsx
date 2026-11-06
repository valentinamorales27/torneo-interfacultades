
import { useEffect, useState } from 'react'
import {
  obtenerPlanilleros,
  crearPlanillero,
  eliminarPlanillero
} from '../services/api'

function Usuarios() {
  const [planilleros, setPlanilleros] = useState([])
  const [correo, setCorreo] = useState('')
  const [contraseña, setContraseña] = useState('')
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [cargando, setCargando] = useState(true)
  const [guardando, setGuardando] = useState(false)

  async function cargarPlanilleros() {
    try {
      setError('')
      const datos = await obtenerPlanilleros()
      setPlanilleros(datos)
    } catch (error) {
      setError(error.message)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargarPlanilleros()
  }, [])

  async function manejarCrear(evento) {
    evento.preventDefault()
    setError('')
    setMensaje('')
    setGuardando(true)

    try {
      await crearPlanillero({ correo, contraseña })
      setCorreo('')
      setContraseña('')
      setMensaje('Planillero creado correctamente')
      await cargarPlanilleros()
    } catch (error) {
      setError(error.message)
    } finally {
      setGuardando(false)
    }
  }

  async function manejarEliminar(correoPlanillero) {
    if (!window.confirm(`¿Eliminar al planillero ${correoPlanillero}?`)) {
      return
    }

    setError('')
    setMensaje('')

    try {
      await eliminarPlanillero(correoPlanillero)
      setMensaje('Planillero eliminado correctamente')
      await cargarPlanilleros()
    } catch (error) {
      setError(error.message)
    }
  }

  return (
    <div className="dashboard-panel" style={{ padding: '28px' }}>
      <h2>Administración de planilleros</h2>
      <p>Desde acá podés crear y administrar las cuentas de los planilleros.</p>

      <form onSubmit={manejarCrear} style={{ marginTop: '24px' }}>
        <h3>Nuevo planillero</h3>

        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <input
            type="email"
            placeholder="Correo electrónico"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            required
            maxLength={50}
          />

          <input
            type="password"
            placeholder="Contraseña (mínimo 8 caracteres)"
            value={contraseña}
            onChange={(e) => setContraseña(e.target.value)}
            required
            minLength={8}
            maxLength={128}
          />

          <button type="submit" disabled={guardando}>
            {guardando ? 'Creando...' : 'Crear planillero'}
          </button>
        </div>
      </form>

      {error && <p style={{ color: '#b91c1c' }}>{error}</p>}
      {mensaje && <p style={{ color: '#047857' }}>{mensaje}</p>}

      <h3 style={{ marginTop: '32px' }}>Planilleros registrados</h3>

      {cargando ? (
        <p>Cargando planilleros...</p>
      ) : planilleros.length === 0 ? (
        <p>No hay planilleros registrados.</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', marginTop: '16px' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left' }}>Correo</th>
                <th style={{ textAlign: 'left' }}>Rol</th>
                <th style={{ textAlign: 'left' }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {planilleros.map((planillero) => (
                <tr key={planillero.correo}>
                  <td>{planillero.correo}</td>
                  <td>{planillero.rol}</td>
                  <td>
                    <button
                      type="button"
                      onClick={() => manejarEliminar(planillero.correo)}
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
    </div>
  )
}

export default Usuarios
