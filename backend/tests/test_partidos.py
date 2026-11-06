
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask

from routes.partidos import (
    partidos_bp,
    validar_partido,
    validar_disponibilidad_cancha,
    validar_fecha_torneo
)


class TestPartidos(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "clave-solo-para-tests"
        self.app.register_blueprint(partidos_bp)

        self.cliente = self.app.test_client()

        with self.cliente.session_transaction() as sesion:
            sesion["correo"] = "admin_prueba@test.local"
            sesion["rol"] = "administrador"

        self.partido = {
            "id_torneo": 1,
            "numero_fecha": 1,
            "id_equipo_local": 1,
            "id_equipo_visitante": 2,
            "dia": "2026-11-10",
            "id_turno": 1,
            "nombre_cancha": "Cancha A",
            "id_complejo": 1,
            "estado": "programado"
        }

    def test_fecha_invalida(self):
        datos = self.partido.copy()
        datos["dia"] = "10/11/2026"

        resultado = validar_partido(datos)

        self.assertIsNotNone(resultado)
        self.assertIn("formato", resultado)

    def test_equipo_contra_si_mismo(self):
        datos = self.partido.copy()
        datos["id_equipo_visitante"] = 1

        resultado = validar_partido(datos)

        self.assertEqual(
            resultado,
            "Un equipo no puede jugar contra sí mismo"
        )

    def test_estado_invalido(self):
        datos = self.partido.copy()
        datos["estado"] = "desconocido"

        resultado = validar_partido(datos)

        self.assertEqual(
            resultado,
            "El estado del partido no es válido"
        )

    def test_equipo_local_invalido(self):
        datos = self.partido.copy()
        datos["id_equipo_local"] = -1

        resultado = validar_partido(datos)

        self.assertEqual(
            resultado,
            "El equipo local debe ser válido"
        )

    def test_planillero_no_puede_crear_partido(self):
        with self.cliente.session_transaction() as sesion:
            sesion["rol"] = "planillero"

        with patch("routes.partidos.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/partidos/",
                json=self.partido
            )

            self.assertEqual(respuesta.status_code, 403)
            conexion.assert_not_called()

    def test_sin_sesion_no_puede_crear_partido(self):
        with self.cliente.session_transaction() as sesion:
            sesion.clear()

        with patch("routes.partidos.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/partidos/",
                json=self.partido
            )

            self.assertEqual(respuesta.status_code, 401)
            conexion.assert_not_called()
    
    def test_cancha_ocupada(self):
        from unittest.mock import MagicMock

        cursor = MagicMock()

        #simulamos que ya existe un partido en esa cancha y turno
        cursor.fetchall.return_value = [
            {"id_partido": 15}
        ]

        resultado = validar_disponibilidad_cancha(
            cursor,
            self.partido
        )

        self.assertEqual(
            resultado,
            "La cancha ya está ocupada en ese día y turno"
        )

    def test_cancha_disponible(self):
        from unittest.mock import MagicMock

        cursor = MagicMock()

        #simulamos que no hay partidos en esa cancha y turno
        cursor.fetchall.return_value = []

        resultado = validar_disponibilidad_cancha(
            cursor,
            self.partido
        )

        self.assertIsNone(resultado)
    
    def test_partido_antes_del_inicio_torneo(self):
        from unittest.mock import MagicMock
        from datetime import date

        cursor = MagicMock()
        cursor.fetchone.return_value = {
            "fecha_inicio": date(2026, 9, 1),
            "fecha_fin": date(2026, 11, 30)
        }

        resultado = validar_fecha_torneo(
            cursor, 1, "2026-08-15"
        )

        self.assertEqual(
            resultado,
            "La fecha del partido no puede ser anterior al inicio del torneo"
        )

    def test_partido_despues_del_fin_torneo(self):
        from unittest.mock import MagicMock
        from datetime import date

        cursor = MagicMock()
        cursor.fetchone.return_value = {
            "fecha_inicio": date(2026, 9, 1),
            "fecha_fin": date(2026, 11, 30)
        }

        resultado = validar_fecha_torneo(
            cursor, 1, "2026-12-05"
        )

        self.assertEqual(
            resultado,
            "La fecha del partido no puede ser posterior al fin del torneo"
        )

    def test_partido_dentro_del_periodo(self):
        from unittest.mock import MagicMock
        from datetime import date

        cursor = MagicMock()
        cursor.fetchone.return_value = {
            "fecha_inicio": date(2026, 9, 1),
            "fecha_fin": date(2026, 11, 30)
        }

        resultado = validar_fecha_torneo(
            cursor, 1, "2026-10-15"
        )

        self.assertIsNone(resultado)
    
    def test_partido_nuevo_debe_ser_programado(self):
        datos = self.partido.copy()
        datos["estado"] = "jugado"

        with patch("routes.partidos.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/partidos/",
                json=datos
            )

            self.assertEqual(respuesta.status_code, 400)
            self.assertIn(
                "Un partido nuevo debe crearse en estado programado",
                respuesta.get_json()["error"]
            )
            conexion.assert_not_called()

    def test_no_modificar_partido_jugado(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        cursor.fetchone.return_value = {
            "id_partido": 1,
            "estado": "jugado"
        }

        with patch(
            "routes.partidos.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.put(
                "/partidos/1",
                json=self.partido
            )

        self.assertEqual(respuesta.status_code, 409)
        self.assertIn(
            "No se pueden modificar partidos jugados o cancelados",
            respuesta.get_json()["error"]
        )

        conexion.commit.assert_not_called()

    def test_no_modificar_partido_cancelado(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        cursor.fetchone.return_value = {
            "id_partido": 1,
            "estado": "cancelado"
        }

        with patch(
            "routes.partidos.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.put(
                "/partidos/1",
                json=self.partido
            )

        self.assertEqual(respuesta.status_code, 409)
        self.assertIn(
            "No se pueden modificar partidos jugados o cancelados",
            respuesta.get_json()["error"]
        )

        conexion.commit.assert_not_called()
    
    def test_no_crear_partido_torneo_finalizado(self):
        from unittest.mock import MagicMock, patch

        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        cursor.fetchone.return_value = {
            "estado": "finalizado"
        }

        with patch(
            "routes.partidos.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.post(
                "/partidos/",
                json=self.partido
            )

        self.assertEqual(respuesta.status_code, 409)

        self.assertIn(
            "No se pueden crear partidos en un torneo finalizado",
            respuesta.get_json()["error"]
        )

        conexion.commit.assert_not_called()



if __name__ == "__main__":
    unittest.main()
