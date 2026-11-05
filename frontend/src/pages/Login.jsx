
import { useState } from 'react'
import './Login.css'
import { useNavigate } from 'react-router'
import { iniciarSesion } from '../services/api'

function IconoTrofeo() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0V4Z" />
      <path d="M7 6H4v3a4 4 0 0 0 4 4M17 6h3v3a4 4 0 0 1-4 4" />
    </svg>
  )
}

function IconoCorreo() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="m4 7 8 6 8-6" />
    </svg>
  )
}

function IconoCandado() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <rect x="4" y="10" width="16" height="11" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3" />
    </svg>
  )
}

function IconoOjo({ visible }) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" />
      <circle cx="12" cy="12" r="3" />
      {visible && <path d="m4 4 16 16" />}
    </svg>
  )
}

function Decoraciones() {
  return (
    <div className="login-decorations" aria-hidden="true">
      <svg className="decoration trophy-decoration" viewBox="0 0 150 150">
        <path d="M48 35h54v34a27 27 0 0 1-54 0V35Z" />
        <path d="M48 44H27v19a27 27 0 0 0 27 27M102 44h21v19a27 27 0 0 1-27 27" />
        <path d="M75 96v25M53 124h44M65 60l10-9 10 9-4 13H69Z" />
      </svg>

      <svg className="decoration field-decoration" viewBox="0 0 180 110">
        <rect x="5" y="5" width="170" height="100" rx="4" />
        <path d="M90 5v100M90 5a25 25 0 0 0 0 50 25 25 0 0 0 0-50M5 32h27v46H5M175 32h-27v46h27" />
        <path d="M5 43h12v24H5M175 43h-12v24h12" />
      </svg>

      <svg className="decoration ball-decoration" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="36" />
        <path d="m50 31 17 12-6 20H39l-6-20 17-12ZM50 31V14M67 43l18-8M61 63l10 18M39 63 29 81M33 43l-18-8" />
      </svg>

      <svg className="decoration goal-decoration" viewBox="0 0 190 130">
        <path d="M15 48 55 15h105v90H55V15M15 48v57h40" />
        <path d="M55 15 80 34v71M80 34h80M80 34v71M105 34v71M130 34v71M55 58h105M55 82h105" />
        <circle cx="15" cy="48" r="5" />
        <path d="M2 75c15-19 25-24 37-29M-5 96c18-21 31-30 45-36" />
      </svg>
    </div>
  )
}

function Login() {
    const [correo, setCorreo] = useState('')
    const [contrasena, setContrasena] = useState('')
    const [mostrarContrasena, setMostrarContrasena] = useState(false)
    const [mensaje, setMensaje] = useState('')
    const navegar = useNavigate()
    const [cargando, setCargando] = useState(false) 

  
    async function manejarEnvio(event) {
        event.preventDefault()
        setMensaje('')

        const correoValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

        if (!correo.trim()) {
            setMensaje('Por favor, ingresá tu correo electrónico.')
            return
        }

        if (!correoValido.test(correo)) {
            setMensaje('Ingresá un correo electrónico válido.')
            return
        }

        if (!contrasena.trim()) {
            setMensaje('Por favor, ingresá tu contraseña.')
            return
        }

        try {
            setCargando(true)

            const datos = await iniciarSesion(correo, contrasena)

            console.log('Inicio de sesión correcto:', datos)

            navegar('/inicio')
        } catch (error) {
            setMensaje(error.message)
        } finally {
            setCargando(false)
        }
    }


  return (
    <main className="login-page">
      <Decoraciones />

      <header className="login-brand">
        <div className="login-brand-icon">
          <IconoTrofeo />
        </div>

        <span className="login-eyebrow">SISTEMA DE GESTIÓN</span>

        <h1>Torneo Interfacultades de Fútbol 5</h1>

        <p>El mejor torneo de facultades del país</p>
      </header>

      <section className="login-card">
        <h2>Iniciar sesión</h2>

        <p className="login-description">
          Ingresá con tu correo y contraseña.
        </p>

        <form onSubmit={manejarEnvio} noValidate>
          <div className="login-field">
            <label htmlFor="correo">Correo electrónico</label>

            <div className="login-input-wrapper">
              <span className="login-input-icon">
                <IconoCorreo />
              </span>

                <input
                    id="correo"
                    type="text"
                    inputMode="email"
                    placeholder="nombre@universidad.edu"
                    value={correo}
                    onChange={(event) => {
                        setCorreo(event.target.value)
                        setMensaje('')
                    }}
                />
            </div>
          </div>

          <div className="login-field">
            <label htmlFor="contrasena">Contraseña</label>

            <div className="login-input-wrapper">
              <span className="login-input-icon">
                <IconoCandado />
              </span>

                <input
                    id="contrasena"
                    type={mostrarContrasena ? 'text' : 'password'}
                    placeholder="Ingresá tu contraseña"
                    value={contrasena}
                    onChange={(event) => {
                        setContrasena(event.target.value)
                        setMensaje('')
                    }}
                />

              <button
                type="button"
                className="password-toggle"
                aria-label={mostrarContrasena ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                onClick={() => setMostrarContrasena(!mostrarContrasena)}
              >
                <IconoOjo visible={mostrarContrasena} />
              </button>
            </div>
          </div>

          <div className="login-forgot">
            <button
              type="button"
              onClick={() => setMensaje('La recuperación de contraseña todavía no está implementada.')}
            >
              ¿Olvidaste tu contraseña?
            </button>
          </div>

            <button
                type="submit"
                className="login-submit"
                disabled={cargando}
                >
                <span>{cargando ? 'Ingresando...' : 'Ingresar'}</span>
                <span className="login-arrow">→</span>
            </button>

          {mensaje && (
            <p className="login-message" role="status">
              {mensaje}
            </p>
          )}
        </form>

        <div className="login-divider" />

        <div className="login-access">
          <span className="access-shield">✓</span>
          <span>Acceso para planilleros y administradores.</span>
        </div>
      </section>
    </main>
  )
}

export default Login
