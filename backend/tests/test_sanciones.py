import unittest
from unittest.mock import Mock
from routes.planillas import jugador_esta_suspendido


class TestSanciones(unittest.TestCase):

    def test_jugador_sin_sanciones(self):
        cursor = Mock()
        cursor.fetchone.return_value = {
            "total_sanciones": None,
            "primera_fecha": None
        }

        resultado = jugador_esta_suspendido(
            cursor, "12345678", 1, 1, 4, 10
        )

        self.assertFalse(resultado)

    def test_jugador_con_suspension_pendiente(self):
        cursor = Mock()
        cursor.fetchone.side_effect = [
            {
                "total_sanciones": 1,
                "primera_fecha": 3
            },
            {
                "fechas_cumplidas": 1
            }
        ]

        resultado = jugador_esta_suspendido(
            cursor, "12345678", 1, 1, 3, 10
        )

        self.assertTrue(resultado)

    def test_segunda_sancion_en_fecha_posterior(self):
        cursor = Mock()
        cursor.fetchone.side_effect = [
            {
                "total_sanciones": 2,
                "primera_fecha": 3
            },
            {
                "fechas_cumplidas": 6
            }
        ]

        resultado = jugador_esta_suspendido(
            cursor, "12345678", 1, 1, 8, 20
        )

        self.assertTrue(resultado)


if __name__ == "__main__":
    unittest.main()
