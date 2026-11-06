
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask
from routes.goles import goles_bp


class TestGoles(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "clave-solo-para-tests"
        self.app.register_blueprint(goles_bp)

        self.cliente = self.app.test_client()

        with self.cliente.session_transaction() as sesion:
            sesion["correo"] = "admin_prueba@test.local"
            sesion["rol"] = "administrador"

        self.gol = {
            "ci_jugador": "12345678",
            "minuto": 15,
            "autogol": False
        }

    def test_cedula_invalida(self):
        datos = self.gol.copy()
        datos["ci_jugador"] = "abc"

        with patch("routes.goles.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/partidos/1/goles",
                json=datos
            )

            self.assertEqual(respuesta.status_code, 400)
            conexion.assert_not_called()

    def test_minuto_invalido(self):
        datos = self.gol.copy()
        datos["minuto"] = -5

        with patch("routes.goles.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/partidos/1/goles",
                json=datos
            )

            self.assertEqual(respuesta.status_code, 400)
            conexion.assert_not_called()

    def test_autogol_invalido(self):
        datos = self.gol.copy()
        datos["autogol"] = "no"

        with patch("routes.goles.obtener_conexion") as conexion:
            respuesta = self.cliente.post(
                "/partidos/1/goles",
                json=datos
            )

            self.assertEqual(respuesta.status_code, 400)
            conexion.assert_not_called()

    def test_no_registrar_gol_en_partido_programado(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        cursor.fetchone.return_value = {
            "id_partido": 1,
            "id_torneo": 1,
            "estado": "programado"
        }

        with patch(
            "routes.goles.obtener_conexion",
            return_value=conexion
        ):
            respuesta = self.cliente.post(
                "/partidos/1/goles",
                json=self.gol
            )

        self.assertEqual(respuesta.status_code, 409)
        self.assertIn(
            "Solamente se pueden registrar goles en partidos jugados",
            respuesta.get_json()["error"]
        )
        conexion.commit.assert_not_called()

    
    def test_jugador_fuera_de_planilla(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        #simulamos un partido jugado
        #y un jugador que no aparece en la planilla
        cursor.fetchone.side_effect = [
            {
                "id_partido": 1,
                "id_torneo": 1,
                "estado": "jugado"
            },
            None
        ]

        with patch(
            "routes.goles.obtener_conexion",
            return_value=conexion
        ), patch(
            "routes.goles.permite_corregir_resultado",
            return_value=True
        ) as verificar_plazo:

            respuesta = self.cliente.post(
                "/partidos/1/goles",
                json=self.gol
            )

        self.assertEqual(respuesta.status_code, 409)

        self.assertIn(
            "no está registrado en la planilla",
            respuesta.get_json()["error"]
        )

        verificar_plazo.assert_called_once_with(cursor, 1)
        self.assertEqual(cursor.fetchone.call_count, 2)
        conexion.commit.assert_not_called()


    def test_planillero_puede_registrar_gol(self):
        with self.cliente.session_transaction() as sesion:
            sesion["rol"] = "planillero"

        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        
        cursor.fetchone.side_effect = [
            {
                "id_partido": 1,
                "id_torneo": 1,
                "estado": "jugado"
            },
            {"ci_jugador": "12345678"}
        ]

        cursor.lastrowid = 10

        with patch(
            "routes.goles.obtener_conexion",
            return_value=conexion
        ), patch(
            "routes.goles.permite_corregir_resultado",
            return_value=True
        ):
            respuesta = self.cliente.post(
                "/partidos/1/goles",
                json=self.gol
            )

        self.assertEqual(respuesta.status_code, 201)
        conexion.commit.assert_called_once()
        self.assertEqual(respuesta.get_json()["id_gol"], 10)


    def test_planillero_no_puede_eliminar_gol(self):
        with self.cliente.session_transaction() as sesion:
            sesion["rol"] = "planillero"

        with patch("routes.goles.obtener_conexion") as conexion:
            respuesta = self.cliente.delete(
                "/partidos/goles/1"
            )

            self.assertEqual(respuesta.status_code, 403)
            conexion.assert_not_called()
    
    
    def test_no_agregar_gol_despues_48_horas(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        cursor.fetchone.return_value = {
            "id_partido": 1,
            "id_torneo": 1,
            "estado": "jugado"
        }

        with patch(
            "routes.goles.obtener_conexion",
            return_value=conexion
        ), patch(
            "routes.goles.permite_corregir_resultado",
            return_value=False
        ) as verificar_plazo:
            respuesta = self.cliente.post(
                "/partidos/1/goles",
                json=self.gol
            )

        self.assertEqual(respuesta.status_code, 409)
        self.assertIn(
            "48 horas",
            respuesta.get_json()["error"]
        )

        verificar_plazo.assert_called_once_with(cursor, 1)
        conexion.commit.assert_not_called()

        consultas = [
            llamada.args[0].upper()
            for llamada in cursor.execute.call_args_list
        ]

        self.assertFalse(
            any("INSERT INTO GOL" in consulta for consulta in consultas)
        )


    def test_no_eliminar_gol_despues_48_horas(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        cursor.fetchone.return_value = {
            "id_gol": 1,
            "id_partido": 1,
            "estado": "jugado"
        }

        with patch(
            "routes.goles.obtener_conexion",
            return_value=conexion
        ), patch(
            "routes.goles.permite_corregir_resultado",
            return_value=False
        ):
            respuesta = self.cliente.delete(
                "/partidos/goles/1"
            )

        self.assertEqual(respuesta.status_code, 409)
        conexion.commit.assert_not_called()

    def test_eliminar_gol_dentro_48_horas(self):
        conexion = MagicMock()
        cursor = conexion.cursor.return_value

        cursor.fetchone.return_value = {
            "id_gol": 1,
            "id_partido": 1,
            "estado": "jugado"
        }

        with patch(
            "routes.goles.obtener_conexion",
            return_value=conexion
        ), patch(
            "routes.goles.permite_corregir_resultado",
            return_value=True
        ):
            respuesta = self.cliente.delete(
                "/partidos/goles/1"
            )

        self.assertEqual(respuesta.status_code, 200)
        conexion.commit.assert_called_once()



if __name__ == "__main__":
    unittest.main()
