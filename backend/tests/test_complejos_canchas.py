
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask

from routes.complejos import complejos_bp
from routes.canchas import canchas_bp


class TestComplejosCanchas(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "clave-para-tests"

        self.app.register_blueprint(complejos_bp)
        self.app.register_blueprint(canchas_bp)

        self.cliente = self.app.test_client()

        self.complejo = {
            "nombre": "Complejo de Prueba",
            "direccion": "Av. Italia 1234",
            "departamento": "Montevideo"
        }

        self.cancha = {
            "nombre_cancha": "Cancha de Prueba",
            "id_complejo": 1,
            "superficie": "sintético",
            "techada": True
        }

    def iniciar_sesion(self, rol):
        with self.cliente.session_transaction() as sesion:
            sesion["correo"] = "usuario@prueba.com"
            sesion["rol"] = rol

    def test_administrador_puede_crear_complejo(self):
        self.iniciar_sesion("administrador")

        conexion = MagicMock()
        cursor = conexion.cursor.return_value
        cursor.lastrowid = 5

        with patch(
            "routes.complejos.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.post(
                "/complejos/",
                json=self.complejo
            )

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.get_json()["id_complejo"], 5)
        conexion.commit.assert_called_once()

    def test_planillero_no_puede_crear_complejo(self):
        self.iniciar_sesion("planillero")

        with patch("routes.complejos.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/complejos/",
                json=self.complejo
            )

        self.assertEqual(respuesta.status_code, 403)
        conexion.assert_not_called()

    def test_administrador_puede_crear_cancha(self):
        self.iniciar_sesion("administrador")

        conexion = MagicMock()

        with patch(
            "routes.canchas.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.post(
                "/canchas/",
                json=self.cancha
            )

        self.assertEqual(respuesta.status_code, 201)
        conexion.commit.assert_called_once()

    def test_planillero_no_puede_crear_cancha(self):
        self.iniciar_sesion("planillero")

        with patch("routes.canchas.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/canchas/",
                json=self.cancha
            )

        self.assertEqual(respuesta.status_code, 403)
        conexion.assert_not_called()

    def test_planillero_puede_consultar_complejos(self):
        self.iniciar_sesion("planillero")

        conexion = MagicMock()
        cursor = conexion.cursor.return_value
        cursor.fetchall.return_value = [self.complejo]

        with patch(
            "routes.complejos.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.get("/complejos/")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.get_json()), 1)

    def test_planillero_puede_consultar_canchas(self):
        self.iniciar_sesion("planillero")

        conexion = MagicMock()
        cursor = conexion.cursor.return_value
        cursor.fetchall.return_value = [self.cancha]

        with patch(
            "routes.canchas.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.get("/canchas/")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.get_json()), 1)

    def test_sin_sesion_no_puede_crear_complejo(self):
        with patch("routes.complejos.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/complejos/",
                json=self.complejo
            )

        self.assertEqual(respuesta.status_code, 401)
        conexion.assert_not_called()

    def test_sin_sesion_no_puede_crear_cancha(self):
        with patch("routes.canchas.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/canchas/",
                json=self.cancha
            )

        self.assertEqual(respuesta.status_code, 401)
        conexion.assert_not_called()
    
    def test_administrador_puede_modificar_complejo(self):
        self.iniciar_sesion("administrador")

        conexion = MagicMock()
        cursor = conexion.cursor.return_value
        cursor.fetchone.return_value = {"id_complejo": 1}

        with patch(
            "routes.complejos.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.put(
                "/complejos/1",
                json=self.complejo
            )

        self.assertEqual(respuesta.status_code, 200)
        conexion.commit.assert_called_once()

        consultas = [
            llamada.args[0].upper()
            for llamada in cursor.execute.call_args_list
        ]

        self.assertTrue(
            any("UPDATE COMPLEJO" in consulta for consulta in consultas)
        )

    def test_planillero_no_puede_modificar_complejo(self):
        self.iniciar_sesion("planillero")

        with patch("routes.complejos.obtener_conexion") as conexion:
            respuesta = self.cliente.put(
                "/complejos/1",
                json=self.complejo
            )

        self.assertEqual(respuesta.status_code, 403)
        conexion.assert_not_called()

    def test_administrador_puede_modificar_cancha(self):
        self.iniciar_sesion("administrador")

        conexion = MagicMock()
        cursor = conexion.cursor.return_value
        cursor.fetchone.return_value = {"nombre_cancha": "Cancha de Prueba"}

        with patch(
            "routes.canchas.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.put(
                "/canchas/1/Cancha%20de%20Prueba",
                json={
                    "superficie": "parquet",
                    "techada": False
                }
            )

        self.assertEqual(respuesta.status_code, 200)
        conexion.commit.assert_called_once()

        consultas = [
            llamada.args[0].upper()
            for llamada in cursor.execute.call_args_list
        ]

        self.assertTrue(
            any("UPDATE CANCHA" in consulta for consulta in consultas)
        )

    def test_planillero_no_puede_modificar_cancha(self):
        self.iniciar_sesion("planillero")

        with patch("routes.canchas.obtener_conexion") as conexion:
            respuesta = self.cliente.put(
                "/canchas/1/Cancha%20de%20Prueba",
                json={
                    "superficie": "parquet",
                    "techada": False
                }
            )

        self.assertEqual(respuesta.status_code, 403)
        conexion.assert_not_called()



if __name__ == "__main__":
    unittest.main()
