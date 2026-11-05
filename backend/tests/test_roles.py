
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask

from routes.equipos import equipos_bp
from routes.planteles import planteles_bp
from routes.torneos import torneos_bp


class TestRoles(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "clave-solo-para-tests"

        self.app.register_blueprint(equipos_bp)
        self.app.register_blueprint(planteles_bp)
        self.app.register_blueprint(torneos_bp)

        self.cliente = self.app.test_client()

        self.equipo = {
            "nombre": "Equipo de Prueba",
            "id_torneo": 1,
            "id_facultad": 1,
            "ci_capitan": "12345678",
            "numero_camiseta_capitan": 10
        }

    def iniciar_sesion(self, rol):
        with self.cliente.session_transaction() as sesion:
            sesion["correo"] = "usuario@test.local"
            sesion["rol"] = rol

    def test_planillero_no_puede_crear_equipos(self):
        self.iniciar_sesion("planillero")

        with patch("routes.equipos.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/equipos",
                json=self.equipo
            )

            self.assertEqual(respuesta.status_code, 403)
            conexion.assert_not_called()

    def test_planillero_no_puede_modificar_equipos(self):
        self.iniciar_sesion("planillero")

        with patch("routes.equipos.obtener_conexion") as conexion:
            respuesta = self.cliente.put(
                "/equipos/1",
                json={"nombre": "Nuevo nombre"}
            )

            self.assertEqual(respuesta.status_code, 403)
            conexion.assert_not_called()

    def test_planillero_no_puede_modificar_planteles(self):
        self.iniciar_sesion("planillero")

        with patch("routes.planteles.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/equipos/1/plantel",
                json={
                    "ci_jugador": "12345678",
                    "numero_camiseta": 7
                }
            )

            self.assertEqual(respuesta.status_code, 403)
            conexion.assert_not_called()

    def test_planillero_puede_consultar_equipos(self):
        self.iniciar_sesion("planillero")

        conexion = MagicMock()
        cursor = conexion.cursor.return_value
        cursor.fetchall.return_value = []

        with patch(
            "routes.equipos.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.get(
                "/equipos?id_torneo=1"
            )

        self.assertEqual(respuesta.status_code, 200)

    def test_planillero_puede_consultar_planteles(self):
        self.iniciar_sesion("planillero")

        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        cursor.fetchone.return_value = {
            "id_equipo": 1,
            "id_torneo": 1
        }

        cursor.fetchall.return_value = []

        with patch(
            "routes.planteles.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.get(
                "/equipos/1/plantel"
            )

        self.assertEqual(respuesta.status_code, 200)

    def test_administrador_puede_consultar_torneos(self):
        self.iniciar_sesion("administrador")

        conexion = MagicMock()
        cursor = conexion.cursor.return_value
        cursor.fetchall.return_value = []

        with patch(
            "routes.torneos.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.get("/torneos/")

        self.assertEqual(respuesta.status_code, 200)

    def test_usuario_sin_sesion_no_puede_consultar_equipos(self):
        with patch("routes.equipos.obtener_conexion") as conexion:
            respuesta = self.cliente.get(
                "/equipos?id_torneo=1"
            )

            self.assertEqual(respuesta.status_code, 401)
            conexion.assert_not_called()


if __name__ == "__main__":
    unittest.main()
