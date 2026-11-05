
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask
from routes.planteles import planteles_bp


class TestPlanteles(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "clave-solo-para-tests"
        self.app.register_blueprint(planteles_bp)

        self.cliente = self.app.test_client()

        #simulamos una sesion de administrador
        with self.cliente.session_transaction() as sesion:
            sesion["correo"] = "admin_prueba@test.local"
            sesion["rol"] = "administrador"

        self.jugador = {
            "ci_jugador": "12345678",
            "numero_camiseta": 10
        }

    def test_cedula_invalida(self):
        datos = self.jugador.copy()
        datos["ci_jugador"] = "123"

        with patch("routes.planteles.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/equipos/1/plantel",
                json=datos
            )

            self.assertEqual(respuesta.status_code, 400)
            conexion.assert_not_called()

    def test_planillero_no_puede_agregar_jugador(self):
        with self.cliente.session_transaction() as sesion:
            sesion["rol"] = "planillero"

        with patch("routes.planteles.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/equipos/1/plantel",
                json=self.jugador
            )

            self.assertEqual(respuesta.status_code, 403)
            conexion.assert_not_called()

    def probar_estado_torneo(self, estado):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        cursor.fetchone.return_value = {
            "id_equipo": 1,
            "id_torneo": 1,
            "id_facultad": 1,
            "ci_capitan": "87654321",
            "estado": estado
        }

        with patch(
            "routes.planteles.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.post(
                "/equipos/1/plantel",
                json=self.jugador
            )

        return respuesta, cursor

    def test_no_agregar_jugador_en_curso(self):
        respuesta, cursor = self.probar_estado_torneo("en curso")

        #el codigo actual devuelve 404 al bloquear esta operacion
        self.assertEqual(respuesta.status_code, 404)
        self.assertIn(
            "no está en inscripción",
            respuesta.get_json()["error"]
        )

        consultas = [
            llamada.args[0]
            for llamada in cursor.execute.call_args_list
        ]

        self.assertFalse(
            any("INSERT INTO equipo_jugador_torneo" in consulta
                for consulta in consultas)
        )

    def test_no_agregar_jugador_finalizado(self):
        respuesta, cursor = self.probar_estado_torneo("finalizado")

        self.assertEqual(respuesta.status_code, 404)
        self.assertIn(
            "no está en inscripción",
            respuesta.get_json()["error"]
        )

        consultas = [
            llamada.args[0]
            for llamada in cursor.execute.call_args_list
        ]

        self.assertFalse(
            any("INSERT INTO equipo_jugador_torneo" in consulta
                for consulta in consultas)
        )

    
    def test_maximo_diez_jugadores(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        cursor.fetchone.side_effect = [
            {
                "id_equipo": 1,
                "id_torneo": 1,
                "id_facultad": 1,
                "ci_capitan": "87654321",
                "estado": "inscripción"
            },
            {
                "ci": "12345678",
                "nombre": "Jugador",
                "apellido": "Prueba",
                "tipo": "grado",
                "id_facultad": 1
            }
        ]

        cursor.fetchall.return_value = [
            {
                "ci_jugador": str(i),
                "numero_camiseta": i,
                "tipo": "grado"
            }
            for i in range(10)
        ]

        with patch("routes.planteles.obtener_conexion", return_value=conexion):
            respuesta = self.cliente.post(
                "/equipos/1/plantel",
                json=self.jugador
            )

        self.assertEqual(respuesta.status_code, 409)
        self.assertIn("máximo de 10 jugadores", respuesta.get_json()["error"])
        conexion.commit.assert_not_called()

    def test_maximo_dos_docentes_funcionarios(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        cursor.fetchone.side_effect = [
            {
                "id_equipo": 1,
                "id_torneo": 1,
                "id_facultad": 1,
                "ci_capitan": "87654321",
                "estado": "inscripción"
            },
            {
                "ci": "12345678",
                "nombre": "Jugador",
                "apellido": "Prueba",
                "tipo": "docente",
                "id_facultad": 1
            },
            None
        ]

        cursor.fetchall.return_value = [
            {"ci_jugador": "11111111", "numero_camiseta": 1, "tipo": "docente"},
            {"ci_jugador": "22222222", "numero_camiseta": 2, "tipo": "funcionario"}
        ]

        with patch("routes.planteles.obtener_conexion", return_value=conexion):
            respuesta = self.cliente.post(
                "/equipos/1/plantel",
                json=self.jugador
            )

        self.assertEqual(respuesta.status_code, 409)
        self.assertIn("más de 2 docentes y funcionarios", respuesta.get_json()["error"])
        conexion.commit.assert_not_called()



if __name__ == "__main__":
    unittest.main()
