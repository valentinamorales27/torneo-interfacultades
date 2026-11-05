
import '../pages/Dashboard.css'

import { useEffect, useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router'

import {
  obtenerSesion,
  cerrarSesion,
  obtenerTorneos
} from '../services/api'

import { TorneoContext } from '../context/TorneoContext'

// Componente encargado de dibujar los iconos
function Icon({ name }) {
  const paths = {
    home: (
      <>
        <path d="m3 10 9-7 9 7" />
        <path d="M5 9v12h14V9M9 21v-7h6v7" />
      </>
    ),

    users: (
      <>
        <path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
        <circle cx="10" cy="7" r="4" />
        <path d="M20 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
      </>
    ),

    user: (
      <>
        <circle cx="12" cy="8" r="4" />
        <path d="M4 21a8 8 0 0 1 16 0" />
      </>
    ),

    calendar: (
      <>
        <rect x="3" y="5" width="18" height="16" rx="2" />
        <path d="M16 3v4M8 3v4M3 10h18M8 14h3M8 17h6" />
      </>
    ),

    trophy: (
      <>
        <path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0V4Z" />
        <path d="M7 6H4v3a4 4 0 0 0 4 4M17 6h3v3a4 4 0 0 1-4 4" />
      </>
    ),

    shield: (
      <>
        <path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z" />
        <path d="m9 12 2 2 4-4" />
      </>
    ),

    ball: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="m12 7 4 3-1.5 5h-5L8 10l4-3ZM12 7V3M16 10l4-1M14.5 15l2 4M9.5 15l-2 4M8 10l-4-1" />
      </>
    ),

    info: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 11v5M12 8h.01" />
      </>
    ),

    pin: (
      <>
        <path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z" />
        <circle cx="12" cy="10" r="2.5" />
      </>
    ),

    arrow: (
      <>
        <path d="M5 12h14M13 6l6 6-6 6" />
      </>
    )
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

// Opciones del menú
const navegacion = [
  {
    nombre: 'Resumen',
    icono: 'home',
    ruta: '/inicio'
  },
  {
    nombre: 'Equipos',
    icono: 'users',
    ruta: '/equipos'
  },
  {
    nombre: 'Planteles',
    icono: 'users',
    ruta: '/planteles'
  },
  {
    nombre: 'Jugadores',
    icono: 'user',
    ruta: '/jugadores'
  },
  {
    nombre: 'Partidos',
    icono: 'calendar',
    ruta: '/partidos'
  },
  {
    nombre: 'Planillas',
    icono: 'calendar',
    ruta: '/planillas'
  },
  {
    nombre: 'Sanciones',
    icono: 'shield',
    ruta: '/sanciones',
    rol: 'administrador'
  },
  {
    nombre: 'Tabla de posiciones',
    icono: 'trophy',
    ruta: '/tabla-posiciones'
  },
  {
    nombre: 'Tabla de goleadores',
    icono: 'ball',
    ruta: '/tabla-goleadores'
  },
  {
    nombre: 'Fair play',
    icono: 'shield',
    ruta: '/fair-play'
  }
]

// Layout principal que comparten todas las páginas
function DashboardLayout() {
  const navegar = useNavigate()

  const [usuario, setUsuario] = useState(null)
  const [cargando, setCargando] = useState(true)

  const [torneos, setTorneos] = useState([])
  const [torneoSeleccionado, setTorneoSeleccionado] = useState(null)
  const [cargandoTorneos, setCargandoTorneos] = useState(true)
  const [errorTorneos, setErrorTorneos] = useState('')

  // Verificamos que exista una sesión activa
  useEffect(() => {
    async function cargarSesion() {
      try {
        const datos = await obtenerSesion()
        setUsuario(datos)
      } catch (error) {
        console.error('Error al consultar la sesión:', error)
        navegar('/', { replace: true })
      } finally {
        setCargando(false)
      }
    }

    cargarSesion()
  }, [navegar])

  // Obtenemos los torneos disponibles
  useEffect(() => {
    async function cargarTorneos() {
      try {
        setCargandoTorneos(true)
        setErrorTorneos('')

        const datos = await obtenerTorneos()

        setTorneos(datos)

        if (datos.length > 0) {
          setTorneoSeleccionado(datos[0])
        }
      } catch (error) {
        console.error('Error al consultar los torneos:', error)
        setErrorTorneos(error.message)
      } finally {
        setCargandoTorneos(false)
      }
    }

    cargarTorneos()
  }, [])

  // Cambiamos el torneo seleccionado
  function manejarCambioTorneo(idTorneo) {
    const torneo = torneos.find(
      (item) => String(item.id_torneo) === idTorneo
    )

    if (torneo) {
      setTorneoSeleccionado(torneo)
    }
  }

  // Cerramos la sesión
  async function manejarCerrarSesion() {
    try {
      await cerrarSesion()
      navegar('/', { replace: true })
    } catch (error) {
      console.error('Error al cerrar sesión:', error)
    }
  }

  if (cargando) {
    return <p>Cargando información del usuario...</p>
  }

  return (
    <TorneoContext.Provider
      value={{
        torneos,
        torneoSeleccionado,
        idTorneo: torneoSeleccionado?.id_torneo
      }}
    >
      <main className="dashboard-page">

        <header className="dashboard-header">

          <div className="dashboard-topline">
            <span>SISTEMA DE GESTIÓN</span>

            <div className="dashboard-account">

              <div className="dashboard-user">
                <div className="dashboard-user-icon">
                  <Icon name="user" />
                </div>

                <div>
                  <small>Mi sesión</small>

                  <strong>
                    {usuario ? usuario.rol : 'Cargando...'}
                  </strong>
                </div>
              </div>

              <button
                className="dashboard-logout"
                onClick={manejarCerrarSesion}
              >
                Cerrar sesión
              </button>

            </div>
          </div>

          <div className="dashboard-heading">

            <div className="dashboard-trophy">
              <Icon name="trophy" />
            </div>

            <div>
              <h1>Torneo Interfacultades de Fútbol 5</h1>
              <p>El mejor torneo de facultades del país</p>
            </div>

            <div
              className="header-field-decoration"
              aria-hidden="true"
            >
              <Icon name="ball" />
              <div className="mini-goal" />
            </div>

          </div>

          <div className="dashboard-torneo-selector">
            <label htmlFor="selector-torneo">
              Torneo seleccionado
            </label>

            {cargandoTorneos ? (
              <span>Cargando torneos...</span>
            ) : errorTorneos ? (
              <span>{errorTorneos}</span>
            ) : torneos.length === 0 ? (
              <span>No hay torneos registrados</span>
            ) : (
              <select
                id="selector-torneo"
                value={torneoSeleccionado?.id_torneo || ''}
                onChange={(e) => manejarCambioTorneo(e.target.value)}
              >
                {torneos.map((torneo) => (
                  <option
                    key={torneo.id_torneo}
                    value={torneo.id_torneo}
                  >
                    {torneo.nombre} - {torneo.anio} ({torneo.semestre}° semestre)
                  </option>
                ))}
              </select>
            )}
          </div>

        </header>

        <nav
          className="dashboard-nav"
          aria-label="Navegación principal"
        >
          {navegacion
            .filter((item) => !item.rol || item.rol === usuario?.rol)
            .map((item) => (
              <NavLink
                key={item.nombre}
                to={item.ruta}
                className={({ isActive }) =>
                  `dashboard-nav-item ${isActive ? 'active' : ''}`
                }
              >
                <Icon name={item.icono} />
                {item.nombre}
              </NavLink>
            ))}
        </nav>

        {/* CONTENIDO: cambia según la página */}
        <section className="dashboard-content">
          {cargandoTorneos ? (
            <p>Cargando torneos...</p>
          ) : errorTorneos ? (
            <p>No se pudieron cargar los torneos: {errorTorneos}</p>
          ) : torneos.length === 0 ? (
            <p>Primero se debe crear un torneo para utilizar el sistema.</p>
          ) : (
            <Outlet />
          )}
        </section>

      </main>
    </TorneoContext.Provider>
  )
}

export default DashboardLayout
