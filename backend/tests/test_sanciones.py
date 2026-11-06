
import unittest
from unittest.mock import Mock
from routes.planillas import jugador_esta_suspendido


class TestSanciones(unittest.TestCase):

    def comprobar_suspension(self, sanciones, fechas_jugadas, fecha_actual):
        cursor = Mock()

        cursor.fetchall.side_effect = [
            sanciones,
            [{"numero_fecha": fecha} for fecha in fechas_jugadas]
        ]

        resultado = jugador_esta_suspendido(
            cursor,
            "12345678",
            1,
            1,
            fecha_actual,
            10
        )

        #las pruebas no deben modificar datos
        for llamada in cursor.execute.call_args_list:
            consulta = llamada.args[0].strip().upper()
            self.assertTrue(consulta.startswith("SELECT"))

        return resultado

    def test_jugador_sin_sanciones(self):
        resultado = self.comprobar_suspension(
            [], [1, 2, 3], 4
        )

        self.assertFalse(resultado)

    def test_jugador_con_suspension_pendiente(self):
        sanciones = [
            {"numero_fecha_inicio": 3, "cantidad_fechas": 1}
        ]

        resultado = self.comprobar_suspension(
            sanciones, [1, 2], 3
        )

        self.assertTrue(resultado)

    def test_suspension_cumplida(self):
        sanciones = [
            {"numero_fecha_inicio": 3, "cantidad_fechas": 1}
        ]

        resultado = self.comprobar_suspension(
            sanciones, [1, 2, 3], 4
        )

        self.assertFalse(resultado)

    def test_segunda_sancion_en_fecha_posterior(self):
        sanciones = [
            {"numero_fecha_inicio": 3, "cantidad_fechas": 1},
            {"numero_fecha_inicio": 8, "cantidad_fechas": 1}
        ]

        resultado = self.comprobar_suspension(
            sanciones, [1, 2, 3, 4, 5, 6, 7], 8
        )

        self.assertTrue(resultado)

    def test_suspension_de_dos_fechas(self):
        sanciones = [
            {"numero_fecha_inicio": 4, "cantidad_fechas": 2}
        ]

        #en la fecha 5 todavía está suspendido
        resultado = self.comprobar_suspension(
            sanciones, [1, 2, 3, 4], 5
        )

        self.assertTrue(resultado)

        #en la fecha 6 ya cumplió ambas fechas
        resultado = self.comprobar_suspension(
            sanciones, [1, 2, 3, 4, 5], 6
        )

        self.assertFalse(resultado)

    def test_sanciones_acumuladas(self):
        sanciones = [
            {"numero_fecha_inicio": 3, "cantidad_fechas": 1},
            {"numero_fecha_inicio": 3, "cantidad_fechas": 1}
        ]

        #dos sanciones sumadas implican dos fechas
        resultado = self.comprobar_suspension(
            sanciones, [1, 2, 3], 4
        )

        self.assertTrue(resultado)

        resultado = self.comprobar_suspension(
            sanciones, [1, 2, 3, 4], 5
        )

        self.assertFalse(resultado)

    def test_suspension_sin_partido_disputado(self):
        sanciones = [
            {"numero_fecha_inicio": 3, "cantidad_fechas": 1}
        ]

        #el equipo todavía no jugó desde la sanción
        resultado = self.comprobar_suspension(
            sanciones, [1, 2], 5
        )

        self.assertTrue(resultado)

    def test_suspension_cumplida_en_fecha_posterior(self):
        sanciones = [
            {"numero_fecha_inicio": 3, "cantidad_fechas": 1}
        ]

        #el equipo cumplió la sanción jugando la fecha 5
        resultado = self.comprobar_suspension(
            sanciones, [1, 2, 5], 6
        )

        self.assertFalse(resultado)

    
    def test_partidos_no_jugados_no_cumplen_suspension(self):
        sanciones = [
            {"numero_fecha_inicio": 3, "cantidad_fechas": 1}
        ]

        #las fechas 3 y 4 no fueron jugadas
        resultado = self.comprobar_suspension(
            sanciones, [1, 2], 5
        )

        self.assertTrue(resultado)

    def test_sanciones_nuevas_se_acumulan(self):
        sanciones = [
            {"numero_fecha_inicio": 3, "cantidad_fechas": 2},
            {"numero_fecha_inicio": 4, "cantidad_fechas": 1}
        ]

        #el equipo ya jugó la fecha 3
        resultado = self.comprobar_suspension(
            sanciones, [1, 2, 3], 4
        )

        self.assertTrue(resultado)

        #tras jugar las fechas 4 y 5, cumple las tres
        resultado = self.comprobar_suspension(
            sanciones, [1, 2, 3, 4, 5], 6
        )

        self.assertFalse(resultado)



if __name__ == "__main__":
    unittest.main()
