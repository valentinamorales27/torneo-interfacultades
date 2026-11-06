
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask
from werkzeug.security import check_password_hash

from routes.usuarios import usuarios_bp


class TestUsuarios(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "clave-solo-para-tests"
        self.app.register_blueprint(usuarios_bp)

        self.cliente = self.app.test_client()

        with self.cliente.session_transaction() as sesion:
            sesion["correo"] = "admin_prueba@test.local"
            sesion["rol"] = "administrador"

        self.usuario = {
            "correo": "nuevo_planillero@test.local",
            "contraseña": "Prueba123!"
        }

    def test_correo_invalido(self):
        datos = self.usuario.copy()
        datos["correo"] = "correo_incorrecto"

        with patch("routes.usuarios.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/usuarios/planilleros",
                json=datos
            )

            self.assertEqual(respuesta.status_code, 400)
            conexion.assert_not_called()

    def test_contrasena_corta(self):
        datos = self.usuario.copy()
        datos["contraseña"] = "123"

        with patch("routes.usuarios.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/usuarios/planilleros",
                json=datos
            )

            self.assertEqual(respuesta.status_code, 400)
            conexion.assert_not_called()

    def test_administrador_crea_planillero(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        with patch(
            "routes.usuarios.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.post(
                "/usuarios/planilleros",
                json=self.usuario
            )

        self.assertEqual(respuesta.status_code, 201)
        conexion.commit.assert_called_once()

        valores = cursor.execute.call_args.args[1]

        self.assertEqual(valores[0], self.usuario["correo"])
        self.assertNotEqual(valores[1], self.usuario["contraseña"])
        self.assertTrue(
            check_password_hash(valores[1], self.usuario["contraseña"])
        )
        self.assertEqual(valores[2], "planillero")

    def test_planillero_no_puede_crear_usuario(self):
        with self.cliente.session_transaction() as sesion:
            sesion["rol"] = "planillero"

        with patch("routes.usuarios.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/usuarios/planilleros",
                json=self.usuario
            )

            self.assertEqual(respuesta.status_code, 403)
            conexion.assert_not_called()

    def test_planillero_no_puede_eliminar_usuario(self):
        with self.cliente.session_transaction() as sesion:
            sesion["rol"] = "planillero"

        with patch("routes.usuarios.obtener_conexion") as conexion:
            respuesta = self.cliente.delete(
                "/usuarios/planilleros/nuevo_planillero@test.local"
            )

            self.assertEqual(respuesta.status_code, 403)
            conexion.assert_not_called()

    def test_administrador_consulta_planilleros(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value
        cursor.fetchall.return_value = [
            {
                "correo": "planillero@test.local",
                "rol": "planillero"
            }
        ]

        with patch(
            "routes.usuarios.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.get("/usuarios/planilleros")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.get_json()), 1)

    def test_planillero_no_puede_consultar_usuarios(self):
        with self.cliente.session_transaction() as sesion:
            sesion["rol"] = "planillero"

        with patch("routes.usuarios.obtener_conexion") as conexion:
            respuesta = self.cliente.get("/usuarios/planilleros")

            self.assertEqual(respuesta.status_code, 403)
            conexion.assert_not_called()


if __name__ == "__main__":
    unittest.main()
