
import unittest
from unittest.mock import patch
from flask import Flask
from routes.torneos import torneos_bp


class TestTorneos(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "clave-solo-para-tests"
        self.app.register_blueprint(torneos_bp)

        self.cliente = self.app.test_client()

        #simulamos una sesion de administrador
        with self.cliente.session_transaction() as sesion:
            sesion["correo"] = "admin_prueba@test.local"
            sesion["rol"] = "administrador"

        #datos validos para utilizar como base
        self.torneo = {
            "nombre": "Torneo de prueba",
            "anio": 2028,
            "semestre": 1,
            "fecha_inicio": "2028-03-01",
            "fecha_fin": "2028-06-30",
            "estado": "inscripción"
        }

    def comprobar_error(self, cambios):
        datos = self.torneo.copy()
        datos.update(cambios)

        #comprobamos que no se intente conectar a MySQL
        with patch(
            "routes.torneos.obtener_conexion"
        ) as conexion:
            respuesta = self.cliente.post(
                "/torneos/",
                json=datos
            )

            self.assertEqual(respuesta.status_code, 400)
            conexion.assert_not_called()

    def test_nombre_vacio(self):
        self.comprobar_error({
            "nombre": ""
        })

    def test_semestre_incorrecto(self):
        self.comprobar_error({
            "semestre": 3
        })

    def test_estado_incorrecto(self):
        self.comprobar_error({
            "estado": "pausado"
        })

    def test_fechas_invertidas(self):
        self.comprobar_error({
            "fecha_inicio": "2028-06-30",
            "fecha_fin": "2028-03-01"
        })

    def test_planillero_no_puede_crear_torneo(self):
        with self.cliente.session_transaction() as sesion:
            sesion["rol"] = "planillero"

        with patch("routes.torneos.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/torneos/",
                json=self.torneo
            )

            self.assertEqual(respuesta.status_code, 403)
            conexion.assert_not_called()

    def test_sin_sesion_no_puede_crear_torneo(self):
        with self.cliente.session_transaction() as sesion:
            sesion.clear()

        with patch("routes.torneos.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/torneos/",
                json=self.torneo
            )

            self.assertEqual(respuesta.status_code, 401)
            conexion.assert_not_called()


if __name__ == "__main__":
    unittest.main()
