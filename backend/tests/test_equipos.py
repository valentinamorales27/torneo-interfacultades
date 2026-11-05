
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask
from routes.equipos import equipos_bp


class TestEquipos(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "clave-solo-para-tests"
        self.app.register_blueprint(equipos_bp)

        self.cliente = self.app.test_client()

        #simulamos una sesion de administrador
        with self.cliente.session_transaction() as sesion:
            sesion["correo"] = "admin_prueba@test.local"
            sesion["rol"] = "administrador"

        self.equipo = {
            "nombre": "Equipo de Prueba",
            "id_torneo": 1,
            "id_facultad": 1,
            "ci_capitan": "12345678",
            "numero_camiseta_capitan": 10
        }

    def test_nombre_vacio(self):
        datos = self.equipo.copy()
        datos["nombre"] = ""

        with patch("routes.equipos.obtener_conexion") as conexion:
            respuesta = self.cliente.post("/equipos", json=datos)

            self.assertEqual(respuesta.status_code, 400)
            conexion.assert_not_called()

    def test_cedula_invalida(self):
        datos = self.equipo.copy()
        datos["ci_capitan"] = "123"

        with patch("routes.equipos.obtener_conexion") as conexion:
            respuesta = self.cliente.post("/equipos", json=datos)

            self.assertEqual(respuesta.status_code, 400)
            conexion.assert_not_called()

    def test_planillero_no_puede_crear_equipo(self):
        with self.cliente.session_transaction() as sesion:
            sesion["rol"] = "planillero"

        with patch("routes.equipos.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/equipos",
                json=self.equipo
            )

            self.assertEqual(respuesta.status_code, 403)
            conexion.assert_not_called()

    def probar_estado_torneo(self, estado):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        cursor.fetchone.return_value = {
            "estado": estado
        }

        with patch(
            "routes.equipos.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.post(
                "/equipos",
                json=self.equipo
            )

        return respuesta, cursor

    def test_no_crear_equipo_en_curso(self):
        respuesta, cursor = self.probar_estado_torneo("en curso")

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn(
            "Solo se pueden crear equipos durante la inscripción",
            respuesta.get_json()["error"]
        )

        consultas = [
            llamada.args[0]
            for llamada in cursor.execute.call_args_list
        ]

        self.assertFalse(
            any("INSERT INTO equipo" in consulta for consulta in consultas)
        )

    def test_no_crear_equipo_finalizado(self):
        respuesta, cursor = self.probar_estado_torneo("finalizado")

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn(
            "Solo se pueden crear equipos durante la inscripción",
            respuesta.get_json()["error"]
        )

        consultas = [
            llamada.args[0]
            for llamada in cursor.execute.call_args_list
        ]

        self.assertFalse(
            any("INSERT INTO equipo" in consulta for consulta in consultas)
        )


if __name__ == "__main__":
    unittest.main()
