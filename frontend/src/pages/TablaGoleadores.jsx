
import { useEffect, useState } from 'react'

import { obtenerGoleadores } from '../services/api'
import { useTorneo } from '../context/TorneoContext'

import ReporteTabla from '../components/ReporteTabla'

function TablaGoleadores() {
  const { idTorneo } = useTorneo()

  const [goleadores, setGoleadores] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let activo = true

    async function cargarGoleadores() {
      if (!idTorneo) {
        setGoleadores([])
        setCargando(false)
        return
      }

      try {
        setCargando(true)
        setError('')
        setGoleadores([])

        const datos = await obtenerGoleadores(idTorneo)

        if (activo) {
          setGoleadores(Array.isArray(datos) ? datos : [])
        }
      } catch (error) {
        if (activo) {
          setError(error.message)
        }
      } finally {
        if (activo) {
          setCargando(false)
        }
      }
    }

    cargarGoleadores()

    return () => {
      activo = false
    }
  }, [idTorneo])

  return (
    <>
      <div className="dashboard-title-row">
        <div>
          <h2>Tabla de goleadores</h2>
          <p>Los jugadores que más goles convirtieron en el torneo.</p>
        </div>
      </div>

      <ReporteTabla
        titulo="Top 10 goleadores"
        descripcion="Clasificación de los máximos goleadores del torneo."
        columnas={[
          {
            key: 'posicion',
            titulo: 'Pos.',
            render: (fila) => goleadores.indexOf(fila) + 1
          },
          { key: 'ci', titulo: 'Cédula' },
          { key: 'nombre', titulo: 'Nombre' },
          { key: 'apellido', titulo: 'Apellido' },
          { key: 'equipo', titulo: 'Equipo' },
          { key: 'goles', titulo: 'Goles' }
        ]}
        datos={goleadores}
        cargando={cargando}
        error={error}
        mensajeVacio="Todavía no hay goles registrados."
      />
    </>
  )
}

export default TablaGoleadores
