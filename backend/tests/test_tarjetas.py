
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask
from routes.tarjetas import tarjetas_bp


class TestTarjetas(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "clave-solo-para-tests"
        self.app.register_blueprint(tarjetas_bp)

        self.cliente = self.app.test_client()

        #simulamos una sesion de administrador
        with self.cliente.session_transaction() as sesion:
            sesion["correo"] = "admin_prueba@test.local"
            sesion["rol"] = "administrador"

        self.tarjeta = {
            "ci_jugador": "12345678",
            "minuto": 15,
            "color": "amarilla"
        }

    def test_cedula_invalida(self):
        datos = self.tarjeta.copy()
        datos["ci_jugador"] = "abc"

        with patch("routes.tarjetas.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/partidos/1/tarjetas",
                json=datos
            )

            self.assertEqual(respuesta.status_code, 400)
            conexion.assert_not_called()

    def test_minuto_invalido(self):
        datos = self.tarjeta.copy()
        datos["minuto"] = -5

        with patch("routes.tarjetas.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/partidos/1/tarjetas",
                json=datos
            )

            self.assertEqual(respuesta.status_code, 400)
            conexion.assert_not_called()

    def test_color_invalido(self):
        datos = self.tarjeta.copy()
        datos["color"] = "verde"

        with patch("routes.tarjetas.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/partidos/1/tarjetas",
                json=datos
            )

            self.assertEqual(respuesta.status_code, 400)
            conexion.assert_not_called()

    def test_no_registrar_tarjeta_en_partido_programado(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        cursor.fetchone.return_value = {
            "id_partido": 1,
            "id_torneo": 1,
            "numero_fecha": 1,
            "estado": "programado"
        }

        with patch(
            "routes.tarjetas.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.post(
                "/partidos/1/tarjetas",
                json=self.tarjeta
            )

        self.assertEqual(respuesta.status_code, 409)
        self.assertIn(
            "Solamente se pueden registrar tarjetas en partidos jugados",
            respuesta.get_json()["error"]
        )
        conexion.commit.assert_not_called()

    def test_jugador_fuera_de_planilla(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        cursor.fetchone.side_effect = [
            {
                "id_partido": 1,
                "id_torneo": 1,
                "numero_fecha": 1,
                "estado": "jugado"
            },
            None
        ]

        with patch(
            "routes.tarjetas.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.post(
                "/partidos/1/tarjetas",
                json=self.tarjeta
            )

        self.assertEqual(respuesta.status_code, 409)
        self.assertIn(
            "no está registrado en la planilla",
            respuesta.get_json()["error"]
        )
        conexion.commit.assert_not_called()

    def test_planillero_puede_registrar_tarjeta(self):
        with self.cliente.session_transaction() as sesion:
            sesion["rol"] = "planillero"

        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        cursor.fetchone.side_effect = [
            {
                "id_partido": 1,
                "id_torneo": 1,
                "numero_fecha": 1,
                "estado": "jugado"
            },
            {"ci_jugador": "12345678"}
        ]

        cursor.lastrowid = 10

        #simulamos solamente el recalculo de sanciones
        #para no necesitar registros reales de MySQL
        with patch(
            "routes.tarjetas.obtener_conexion",
            return_value=conexion
        ), patch(
            "routes.tarjetas.recalcular_sanciones_automaticas"
        ) as recalcular:
            respuesta = self.cliente.post(
                "/partidos/1/tarjetas",
                json=self.tarjeta
            )

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.get_json()["id_tarjeta"], 10)
        conexion.commit.assert_called_once()
        recalcular.assert_called_once_with(
            cursor, "12345678", 1
        )

    def test_planillero_no_puede_eliminar_tarjeta(self):
        with self.cliente.session_transaction() as sesion:
            sesion["rol"] = "planillero"

        with patch("routes.tarjetas.obtener_conexion") as conexion:
            respuesta = self.cliente.delete(
                "/partidos/tarjetas/1"
            )

            self.assertEqual(respuesta.status_code, 403)
            conexion.assert_not_called()


if __name__ == "__main__":
    unittest.main()
