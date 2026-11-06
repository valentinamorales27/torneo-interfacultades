
const API_URL = 'http://localhost:5000'

//funcion para hacer las consultas al backend
async function solicitarAPI(ruta, opciones = {}, mensajeError = 'Ocurrio un error.') {
  const respuesta = await fetch(`${API_URL}${ruta}`, {
    ...opciones,
    credentials: 'include',
    headers: {
      ...(opciones.body ? { 'Content-Type': 'application/json' } : {}),
      ...opciones.headers
    }
  })

  const datos = await respuesta.json()

  if (!respuesta.ok) {
    throw new Error(datos.error || datos.mensaje || mensajeError)
  }

  return datos
}

//login y sesion
export async function iniciarSesion(correo, contrasena) {
  return solicitarAPI('/login', {
    method: 'POST',
    body: JSON.stringify({
      correo,
      contraseña: contrasena
    })
  }, 'No se pudo iniciar sesion.')
}

export async function obtenerSesion() {
  return solicitarAPI('/sesion', { method: 'GET' }, 'No se pudo obtener la sesion.')
}

export async function cerrarSesion() {
  return solicitarAPI('/logout', { method: 'POST' }, 'No se pudo cerrar sesion.')
}

//torneos
export async function obtenerTorneos() {
  return solicitarAPI('/torneos/', { method: 'GET' }, 'No se pudieron obtener los torneos.')
}

export async function obtenerTorneo(idTorneo) {
  return solicitarAPI(`/torneos/${idTorneo}`, { method: 'GET' }, 'No se pudo obtener el torneo.')
}

export async function crearTorneo(torneo) {
  return solicitarAPI('/torneos/', {
    method: 'POST',
    body: JSON.stringify(torneo)
  }, 'No se pudo crear el torneo.')
}
//modificamos el estado de un torneo
export async function modificarEstadoTorneo(idTorneo, estado) {
  return solicitarAPI(`/torneos/${idTorneo}/estado`, {
    method: 'PUT',
    body: JSON.stringify({ estado })
  }, 'No se pudo modificar el estado del torneo.')
}

//equipos
export async function obtenerEquipos(idTorneo) {
  return solicitarAPI(`/equipos?id_torneo=${idTorneo}`, { method: 'GET' }, 'No se pudieron obtener los equipos.')
}

export async function obtenerEquipo(idEquipo) {
  return solicitarAPI(`/equipos/${idEquipo}`, { method: 'GET' }, 'No se pudo obtener el equipo.')
}

export async function crearEquipo(equipo) {
  return solicitarAPI('/equipos', {
    method: 'POST',
    body: JSON.stringify(equipo)
  }, 'No se pudo crear el equipo.')
}

export async function modificarEquipo(idEquipo, equipo) {
  return solicitarAPI(`/equipos/${idEquipo}`, {
    method: 'PUT',
    body: JSON.stringify(equipo)
  }, 'No se pudo modificar el equipo.')
}

export async function eliminarEquipo(idEquipo) {
  return solicitarAPI(`/equipos/${idEquipo}`, { method: 'DELETE' }, 'No se pudo eliminar el equipo.')
}


//jugadores
export async function obtenerJugadores() {
  return solicitarAPI('/jugadores', { method: 'GET' }, 'No se pudieron obtener los jugadores.')
}

export async function obtenerJugador(ci) {
  return solicitarAPI(`/jugadores/${ci}`, { method: 'GET' }, 'No se pudo obtener el jugador.')
}

export async function crearJugador(jugador) {
  return solicitarAPI('/jugadores', {
    method: 'POST',
    body: JSON.stringify(jugador)
  }, 'No se pudo crear el jugador.')
}

export async function modificarJugador(ci, jugador) {
  return solicitarAPI(`/jugadores/${ci}`, {
    method: 'PUT',
    body: JSON.stringify(jugador)
  }, 'No se pudo modificar el jugador.')
}

export async function eliminarJugador(ci) {
  return solicitarAPI(`/jugadores/${ci}`, { method: 'DELETE' }, 'No se pudo eliminar el jugador.')
}

//partidos
export async function obtenerPartidos(idTorneo) {
  return solicitarAPI(`/partidos/torneo/${idTorneo}`, { method: 'GET' }, 'No se pudieron obtener los partidos.')
}

//mantenemos esta funcion para no tener que cambiar los lugares que ya la utilizan
export async function obtenerPartidosTorneo(idTorneo) {
  return obtenerPartidos(idTorneo)
}

export async function obtenerPartido(idPartido) {
  return solicitarAPI(`/partidos/${idPartido}`, { method: 'GET' }, 'No se pudo obtener el partido.')
}

export async function crearPartido(partido) {
  return solicitarAPI('/partidos/', {
    method: 'POST',
    body: JSON.stringify(partido)
  }, 'No se pudo crear el partido.')
}

export async function modificarPartido(idPartido, partido) {
  return solicitarAPI(`/partidos/${idPartido}`, {
    method: 'PUT',
    body: JSON.stringify(partido)
  }, 'No se pudo modificar el partido.')
}

export async function eliminarPartido(idPartido) {
  return solicitarAPI(`/partidos/${idPartido}`, { method: 'DELETE' }, 'No se pudo eliminar el partido.')
}

//planillas
export async function obtenerPlanilla(idPartido) {
  return solicitarAPI(`/partidos/${idPartido}/planilla`, { method: 'GET' }, 'No se pudo obtener la planilla.')
}

export async function agregarJugadorPlanilla(idPartido, ciJugador) {
  return solicitarAPI(`/partidos/${idPartido}/planilla`, {
    method: 'POST',
    body: JSON.stringify({ ci_jugador: ciJugador })
  }, 'No se pudo agregar el jugador a la planilla.')
}

export async function eliminarJugadorPlanilla(idPartido, ciJugador) {
  return solicitarAPI(`/partidos/${idPartido}/planilla/${ciJugador}`, { method: 'DELETE' }, 'No se pudo eliminar el jugador de la planilla.')
}

//goles
export async function obtenerGoles(idPartido) {
  return solicitarAPI(`/partidos/${idPartido}/goles`, { method: 'GET' }, 'No se pudieron obtener los goles.')
}

export async function agregarGol(idPartido, gol) {
  return solicitarAPI(`/partidos/${idPartido}/goles`, {
    method: 'POST',
    body: JSON.stringify(gol)
  }, 'No se pudo registrar el gol.')
}

export async function eliminarGol(idGol) {
  return solicitarAPI(`/partidos/goles/${idGol}`, { method: 'DELETE' }, 'No se pudo eliminar el gol.')
}

//tarjetas
export async function obtenerTarjetas(idPartido) {
  return solicitarAPI(`/partidos/${idPartido}/tarjetas`, { method: 'GET' }, 'No se pudieron obtener las tarjetas.')
}

export async function agregarTarjeta(idPartido, tarjeta) {
  return solicitarAPI(`/partidos/${idPartido}/tarjetas`, {
    method: 'POST',
    body: JSON.stringify(tarjeta)
  }, 'No se pudo registrar la tarjeta.')
}

export async function eliminarTarjeta(idTarjeta) {
  return solicitarAPI(`/partidos/tarjetas/${idTarjeta}`, { method: 'DELETE' }, 'No se pudo eliminar la tarjeta.')
}

//sanciones
export async function obtenerSanciones(idTorneo) {
  return solicitarAPI(`/sanciones/?id_torneo=${idTorneo}`, { method: 'GET' }, 'No se pudieron obtener las sanciones.')
}
//obtenemos todas las facultades
export async function obtenerFacultades() {
  return solicitarAPI('/equipos/facultades', { method: 'GET' }, 'No se pudieron obtener las facultades.')
}
//consultamos los datos de la sesion iniciada
export async function consultarSesion() {
  return solicitarAPI('/sesion', { method: 'GET' }, 'No se pudo consultar la sesion.')
}

//obtenemos los integrantes de un equipo
export async function obtenerPlantel(idEquipo) {
  return solicitarAPI(
    `/equipos/${idEquipo}/plantel`,
    { method: 'GET' },
    'No se pudo obtener el plantel.'
  )
}

//agregamos un jugador al plantel
export async function agregarJugadorPlantel(idEquipo, jugador) {
  return solicitarAPI(
    `/equipos/${idEquipo}/plantel`,
    {
      method: 'POST',
      body: JSON.stringify(jugador)
    },
    'No se pudo agregar el jugador al plantel.'
  )
}

//quitamos un jugador del plantel
export async function quitarJugadorPlantel(idEquipo, ci) {
  return solicitarAPI(
    `/equipos/${idEquipo}/plantel/${ci}`,
    { method: 'DELETE' },
    'No se pudo quitar el jugador del plantel.'
  )
}

//modificamos el número de camiseta
export async function modificarCamiseta(idEquipo, ci, numeroCamiseta) {
  return solicitarAPI(
    `/equipos/${idEquipo}/plantel/${ci}/camiseta`,
    {
      method: 'PUT',
      body: JSON.stringify({
        numero_camiseta: numeroCamiseta
      })
    },
    'No se pudo modificar el número de camiseta.'
  )
}

//cambiamos el capitán del equipo
export async function cambiarCapitan(idEquipo, ci) {
  return solicitarAPI(
    `/equipos/${idEquipo}/capitan`,
    {
      method: 'PUT',
      body: JSON.stringify({
        ci_capitan: ci
      })
    },
    'No se pudo cambiar el capitán.'
  )
}

export async function obtenerSancionesJugador(ciJugador) {
  return solicitarAPI(`/sanciones/jugador/${ciJugador}`, { method: 'GET' }, 'No se pudieron obtener las sanciones del jugador.')
}

export async function crearSancion(sancion) {
  return solicitarAPI('/sanciones/', {
    method: 'POST',
    body: JSON.stringify(sancion)
  }, 'No se pudo crear la sancion.')
}
export async function eliminarSancion(idSancion) {
  return solicitarAPI(`/sanciones/${idSancion}`, {
    method: 'DELETE'
  }, 'No se pudo eliminar la sancion.')
}

//reportes
async function obtenerReporte(ruta, mensajeError) {
  return solicitarAPI(`/reportes/${ruta}`, { method: 'GET' }, mensajeError)
}

export async function obtenerTablaPosiciones(idTorneo) {
  return obtenerReporte(`tabla-posiciones/${idTorneo}`, 'No se pudo obtener la tabla de posiciones.')
}

export async function obtenerGoleadores(idTorneo) {
  return obtenerReporte(`goleadores/${idTorneo}`, 'No se pudo obtener la tabla de goleadores.')
}

export async function obtenerFairPlay(idTorneo) {
  return obtenerReporte(`fair-play/${idTorneo}`, 'No se pudo obtener Fair Play.')
}

export async function obtenerPromedioGoles(idTorneo) {
  return obtenerReporte(`promedio-goles/${idTorneo}`, 'No se pudo obtener el promedio de goles.')
}

export async function obtenerUsoCanchasTurnos(idTorneo) {
  return obtenerReporte(`uso-canchas-turnos/${idTorneo}`, 'No se pudo obtener el uso de canchas y turnos.')
}

export async function obtenerJugadoresFacultadTipo(idTorneo) {
  return obtenerReporte(`jugadores-facultad-tipo/${idTorneo}`, 'No se pudo obtener el reporte de jugadores.')
}

export async function obtenerJugadoresSinPlanilla(idTorneo) {
  return obtenerReporte(`jugadores-sin-planilla/${idTorneo}`, 'No se pudo obtener el reporte de jugadores sin planilla.')
}

export async function obtenerSancionesEquipo(idTorneo) {
  return obtenerReporte(`sanciones-equipo/${idTorneo}`, 'No se pudo obtener el reporte de sanciones.')
}

export async function obtenerEstadoPartidos(idTorneo) {
  return obtenerReporte(`estado-partidos/${idTorneo}`, 'No se pudo obtener el estado de los partidos.')
}

export async function obtenerPartidosCanceladosPostergados(idTorneo) {
  return obtenerReporte(`partidos-cancelados-postergados/${idTorneo}`, 'No se pudo obtener el reporte de partidos cancelados y postergados.')
}

export async function obtenerProximosPartidos(idTorneo) {
  return obtenerReporte(`proximos-partidos/${idTorneo}`, 'No se pudo obtener los proximos partidos.')
}

export async function obtenerJugadoresMasPartidos(idTorneo) {
  return obtenerReporte(`jugadores-mas-partidos/${idTorneo}`, 'No se pudo obtener el reporte de jugadores con mas partidos.')
}
//obtenemos todas las canchas
export async function obtenerCanchas() {
  return solicitarAPI(
    '/canchas/',
    { method: 'GET' },
    'No se pudieron obtener las canchas.'
  )
}

//obtenemos todos los turnos
export async function obtenerTurnos() {
  return solicitarAPI(
    '/partidos/turnos',
    { method: 'GET' },
    'No se pudieron obtener los turnos.'
  )
}

export async function obtenerPlanilleros() {
  return solicitarAPI(
    '/usuarios/planilleros',
    {},
    'No se pudieron obtener los planilleros.'
  )
}

export async function crearPlanillero(datos) {
  return solicitarAPI(
    '/usuarios/planilleros',
    {
      method: 'POST',
      body: JSON.stringify(datos)
    },
    'No se pudo crear el planillero.'
  )
}

export async function eliminarPlanillero(correo) {
  return solicitarAPI(
    `/usuarios/planilleros/${encodeURIComponent(correo)}`,
    {
      method: 'DELETE'
    },
    'No se pudo eliminar el planillero.'
  )
}
