import { BrowserRouter, Routes, Route, Navigate } from 'react-router'

import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import DashboardLayout from './components/DashboardLayout'

import TablaPosiciones from './pages/TablaPosiciones'
import Equipos from './pages/Equipos'
import Planteles from './pages/Planteles'
import Jugadores from './pages/Jugadores'
import Partidos from './pages/Partidos'
import TablaGoleadores from './pages/TablaGoleadores'
import FairPlay from './pages/FairPlay'
import Planillas from './pages/Planillas'
import Sanciones from './pages/Sanciones'
import Usuarios from './pages/Usuarios'
import Complejos from './pages/Complejos'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />

        <Route element={<DashboardLayout />}>
          <Route path="/inicio" element={<Dashboard />} />
          <Route path="/tabla-posiciones" element={<TablaPosiciones />} />
          <Route path="/equipos" element={<Equipos />} />
          <Route path="/planteles" element={<Planteles />} />
          <Route path="/jugadores" element={<Jugadores />} />
          <Route path="/partidos" element={<Partidos />} />
          <Route path="/tabla-goleadores" element={<TablaGoleadores />} />
          <Route path="/fair-play" element={<FairPlay />} />
          <Route path="/planillas" element={<Planillas />} />
          <Route path="/sanciones" element={<Sanciones />} />
          <Route path="/usuarios" element={<Usuarios />} />
          <Route path="complejos" element={<Complejos />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App