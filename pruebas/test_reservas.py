"""Pruebas del ciclo de vida de Reserva y del encadenamiento de errores."""

from __future__ import annotations

import unittest

from sistema.clientes import Cliente
from sistema.excepciones import (
    DatoInvalido,
    OperacionNoPermitida,
    ReservaInvalida,
    ServicioNoDisponible,
)
from sistema.reservas import EstadoReserva, Reserva
from sistema.servicios import ReservaSala


class ReservasTests(unittest.TestCase):
    """Verifica creación, confirmación, cancelación y procesamiento."""

    def setUp(self):
        self.cliente = Cliente("Diego López", "CC5555", "diego@example.com", "3005555555")
        self.sala = ReservaSala("Sala B", 100000, 20)

    def test_ciclo_completo_de_reserva(self):
        """Una reserva válida pasa por todos sus estados."""
        reserva = Reserva(self.cliente, self.sala, 2, {"capacidad": 5})
        self.assertIs(reserva.estado, EstadoReserva.CREADA)
        reserva.confirmar()
        self.assertIs(reserva.estado, EstadoReserva.CONFIRMADA)
        costo = reserva.procesar()
        self.assertEqual(costo, 200000)
        self.assertIs(reserva.estado, EstadoReserva.PROCESADA)
        self.assertEqual(reserva.costo, 200000)

    def test_no_se_puede_procesar_sin_confirmar(self):
        """El orden del ciclo de vida se respeta."""
        reserva = Reserva(self.cliente, self.sala, 1)
        with self.assertRaises(OperacionNoPermitida):
            reserva.procesar()

    def test_cancelacion_valida_y_repetida(self):
        """Cancelar funciona una sola vez antes de procesar."""
        reserva = Reserva(self.cliente, self.sala, 1)
        reserva.cancelar("Solicitud del cliente")
        self.assertIs(reserva.estado, EstadoReserva.CANCELADA)
        with self.assertRaises(OperacionNoPermitida):
            reserva.cancelar("Otro motivo")

    def test_no_se_puede_cancelar_una_reserva_procesada(self):
        """Una reserva procesada es definitiva."""
        reserva = Reserva(self.cliente, self.sala, 1, {"capacidad": 2})
        reserva.confirmar()
        reserva.procesar()
        with self.assertRaises(OperacionNoPermitida):
            reserva.cancelar("Cambio de planes")

    def test_cliente_inactivo_no_puede_reservar(self):
        """Se traduce el error de la entidad a ReservaInvalida."""
        self.cliente.desactivar()
        reserva = Reserva(self.cliente, self.sala, 1)
        with self.assertRaises(ReservaInvalida):
            reserva.confirmar()

    def test_duracion_no_numerica_encadena_error_original(self):
        """El ValueError original se conserva como causa."""
        with self.assertRaises(ReservaInvalida) as contexto:
            Reserva(self.cliente, self.sala, "dos")
        self.assertIsInstance(contexto.exception.__cause__, ValueError)

    def test_capacidad_excedida_encadena_dato_invalido(self):
        """El error de validación del servicio se transforma en ReservaInvalida."""
        reserva = Reserva(self.cliente, self.sala, 1, {"capacidad": 50})
        reserva.confirmar()
        with self.assertRaises(ReservaInvalida) as contexto:
            reserva.procesar()
        self.assertIsInstance(contexto.exception.__cause__, DatoInvalido)

    def test_servicio_no_disponible_al_confirmar(self):
        """La indisponibilidad se detecta antes de procesar."""
        cerrada = ReservaSala("Sala Cerrada", 100000, 10, disponible=False)
        reserva = Reserva(self.cliente, cerrada, 1)
        with self.assertRaises(ServicioNoDisponible):
            reserva.confirmar()

    def test_resumen_refleja_estado_y_costo(self):
        """El resumen permite mostrar el resultado de la reserva."""
        reserva = Reserva(self.cliente, self.sala, 1, {"capacidad": 2})
        reserva.confirmar()
        reserva.procesar()
        texto = reserva.resumen()
        self.assertIn("procesada", texto)
        self.assertIn("$100,000.00", texto)

    def test_reserva_sin_cliente_o_servicio(self):
        """Un cliente o servicio ausente produce ReservaInvalida, no AttributeError."""
        for cliente, servicio in [(None, self.sala), (self.cliente, None)]:
            with self.subTest(cliente=cliente, servicio=servicio):
                with self.assertRaises(ReservaInvalida):
                    Reserva(cliente, servicio, 1).validar()


if __name__ == "__main__":
    unittest.main()
