"""Pruebas de la jerarquía de servicios y de la sobrecarga de calcular_costo."""

from __future__ import annotations

import unittest

from sistema.entidades import Entidad
from sistema.excepciones import (
    DatoInvalido,
    ParametroFaltante,
    ServicioNoDisponible,
)
from sistema.servicios import AlquilerEquipos, AsesoriaEspecializada, ReservaSala, Servicio


class ServiciosTests(unittest.TestCase):
    """Verifica abstracción, herencia, polimorfismo y cálculos."""

    def setUp(self):
        self.sala = ReservaSala("Sala A", 100000, 20)
        self.equipo = AlquilerEquipos("Proyector", 50000, 5)
        self.asesoria = AsesoriaEspecializada("Arquitectura", 200000, "Ing. Torres")

    def test_servicio_es_abstracto(self):
        """Servicio no se puede instanciar directamente."""
        with self.assertRaises(TypeError):
            Servicio("Genérico", 1000)

    def test_herencia_y_descripcion_polimorfica(self):
        """Cada subclase describe su propio servicio."""
        for servicio, frase in [
            (self.sala, "Sala"),
            (self.equipo, "Proyector"),
            (self.asesoria, "Arquitectura"),
        ]:
            with self.subTest(servicio=servicio.nombre):
                self.assertIsInstance(servicio, Entidad)
                self.assertIn(frase, servicio.describir())
                self.assertIn("·", servicio.resumen())

    def test_calcular_costo_con_argumentos_nombrados(self):
        """La primera forma de la sobrecarga usa kwargs."""
        self.assertEqual(self.sala.calcular_costo(horas=2, capacidad=8), 200000)

    def test_calcular_costo_con_diccionario(self):
        """La segunda forma de la sobrecarga recibe un diccionario."""
        self.assertEqual(self.equipo.calcular_costo({"horas": 2, "cantidad": 3}), 300000)

    def test_calcular_costo_posicional_con_parametros_extra(self):
        """La tercera forma conserva los kwargs del servicio."""
        total = self.equipo.calcular_costo(2, 0, 0, cantidad=3)
        self.assertEqual(total, 300000)

    def test_calcular_costo_con_parametros_anidados(self):
        """Los parámetros pueden venir dentro de ``parametros``."""
        total = self.asesoria.calcular_costo(
            horas=2, parametros={"nivel": "avanzada"}
        )
        self.assertEqual(total, 720000)

    def test_recargo_por_alta_capacidad(self):
        """La reserva de sala aplica recargo cuando se supera el cupo medio."""
        total = self.sala.calcular_costo(horas=1, capacidad=16)
        self.assertEqual(total, 130000)

    def test_descuento_fuera_de_rango(self):
        """Un descuento mayor que 1 se rechaza."""
        with self.assertRaises(DatoInvalido) as contexto:
            self.sala.calcular_costo(horas=2, descuento=1.5, capacidad=8)
        self.assertEqual(contexto.exception.detalles["campo"], "descuento")

    def test_nivel_de_asesoria_invalido(self):
        """Solo se aceptan niveles definidos en el catálogo."""
        with self.assertRaises(DatoInvalido):
            self.asesoria.calcular_costo(horas=2, nivel="experto")

    def test_alias_de_nivel_basico(self):
        """El alias sin tilde se normaliza al nivel básico."""
        self.assertEqual(self.asesoria.calcular_costo(horas=1, nivel="basico"), 200000)

    def test_parametro_obligatorio_ausente(self):
        """La asesoría exige el nivel para poder cotizarse."""
        with self.assertRaises(ParametroFaltante):
            self.asesoria.calcular_costo(horas=2)

    def test_servicio_no_disponible(self):
        """Un servicio inactivo no admite reservas."""
        inactivo = ReservaSala("Sala Cerrada", 100000, 10, disponible=False)
        with self.assertRaises(ServicioNoDisponible):
            inactivo.validar_disponibilidad()

    def test_tarifa_negativa(self):
        """La validación impide tarifas negativas."""
        with self.assertRaises(DatoInvalido):
            AlquilerEquipos("Proyector", -1, 5).validar()

    def test_sobrecarga_lee_descuento_con_horas_posicional(self):
        """Antes el descuento nombrado se ignoraba si las horas iban posicionales."""
        self.assertEqual(self.sala.calcular_costo(2, descuento=0.5, capacidad=5), 100000)

    def test_sobrecarga_posicional_completa_y_variantes(self):
        """Las firmas posicional, nombrada y de conveniencia dan el mismo total."""
        base = self.sala.calcular_costo(2, 0.19, 0.10, capacidad=8)
        self.assertEqual(base, 214200)
        self.assertEqual(
            self.sala.calcular_costo(horas=2, impuestos=0.19, descuento=0.10, capacidad=8), base
        )
        self.assertEqual(self.sala.calcular_costo_con_impuestos(2, 0.19, capacidad=8), 238000)
        self.assertEqual(self.sala.calcular_costo_con_descuento(2, 0.10, capacidad=8), 180000)

    def test_recargo_de_sala_entra_antes_de_impuestos(self):
        """El recargo por capacidad también paga impuestos (cálculo consistente)."""
        # 2 h x 100000 + recargo (20-10) x 5000 = 250000; con 19 % de impuestos.
        self.assertEqual(self.sala.calcular_costo(horas=2, impuestos=0.19, capacidad=20), 297500)

    def test_demasiados_argumentos_posicionales(self):
        """Más de tres argumentos posicionales se rechazan de forma controlada."""
        with self.assertRaises(ParametroFaltante):
            self.sala.calcular_costo(1, 0, 0, 0, capacidad=2)

    def test_capacidad_e_inventario_no_numericos(self):
        """Los datos no numéricos se convierten en DatoInvalido encadenado."""
        for crear in (
            lambda: ReservaSala("Sala X", 1000, "veinte"),
            lambda: AlquilerEquipos("Equipo X", 1000, None),
        ):
            with self.subTest(crear=crear):
                with self.assertRaises(DatoInvalido) as contexto:
                    crear()
                self.assertIsNotNone(contexto.exception.__cause__)


if __name__ == "__main__":
    unittest.main()
