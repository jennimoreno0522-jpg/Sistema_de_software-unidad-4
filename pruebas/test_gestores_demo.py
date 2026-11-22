"""Pruebas de los gestores en memoria y de la simulación completa."""

from __future__ import annotations

import sys
import unittest

from sistema.clientes import Cliente
from sistema.demo import ejecutar_demo
from sistema.excepciones import DuplicadoError
from sistema.logging_eventos import obtener_registro
from sistema.gestores import GestorClientes, GestorReservas, GestorServicios
from sistema.servicios import ReservaSala


class GestoresTests(unittest.TestCase):
    """Verifica listas internas, búsquedas y control de duplicados."""

    def setUp(self):
        self.clientes = GestorClientes()
        self.servicios = GestorServicios()
        self.reservas = GestorReservas()
        self.cliente = Cliente("Sara Pinzón", "CC7777", "sara@example.com", "3007777777")
        self.sala = ReservaSala("Sala D", 120000, 12)

    def test_registro_y_busqueda_de_cliente(self):
        """El gestor conserva los objetos en una lista privada."""
        self.clientes.agregar(self.cliente)
        self.assertEqual(self.clientes.buscar("cc7777"), self.cliente)
        self.assertEqual(len(self.clientes.todos()), 1)
        self.assertIsNone(self.clientes.buscar("CC0000"))

    def test_cliente_duplicado(self):
        """No se permite repetir documento."""
        self.clientes.agregar(self.cliente)
        with self.assertRaises(DuplicadoError):
            self.clientes.agregar(
                Cliente("Otra Persona", "CC7777", "otra@example.com", "3007777778")
            )

    def test_servicio_duplicado(self):
        """No se permite repetir nombre de servicio."""
        self.servicios.agregar(self.sala)
        with self.assertRaises(DuplicadoError):
            self.servicios.agregar(ReservaSala("Sala D", 80000, 5))

    def test_gestor_de_reservas_y_facturacion(self):
        """Solo las reservas procesadas suman a la facturación."""
        self.clientes.agregar(self.cliente)
        self.servicios.agregar(self.sala)
        reserva = self.reservas.crear(self.cliente, self.sala, 2, {"capacidad": 4})
        self.assertEqual(self.reservas.facturado_total(), 0.0)
        self.reservas.confirmar(reserva.id)
        self.reservas.procesar(reserva.id)
        self.assertEqual(self.reservas.facturado_total(), 240000.0)
        self.assertEqual(len(self.reservas.todas()), 1)


class DemoTests(unittest.TestCase):
    """Verifica la simulación exigida por el Anexo 3."""

    def test_simulacion_ejecuta_al_menos_diez_operaciones(self):
        """Se ejecutan operaciones válidas e inválidas sin detener el programa."""
        resultados = ejecutar_demo()
        self.assertGreaterEqual(len(resultados), 10)
        estados = {item["estado"] for item in resultados}
        self.assertIn("OK", estados)
        self.assertIn("ERROR", estados)

    def test_simulacion_cubre_casos_exigidos(self):
        """Hay clientes, servicios y reservas válidos e inválidos."""
        resultados = {item["numero"]: item["estado"] for item in ejecutar_demo()}
        self.assertGreaterEqual(len(resultados), 20)
        # Clientes: 1 válido; 2, 3 y 15 inválidos.
        self.assertEqual((resultados[1], resultados[2], resultados[15]), ("OK", "ERROR", "ERROR"))
        # Servicios: 4, 6 y 16 válidos; 5 y 17 inválidos.
        self.assertEqual((resultados[4], resultados[16], resultados[5], resultados[17]),
                         ("OK", "OK", "ERROR", "ERROR"))
        # Reservas: 7 y 18 exitosas; 8, 9, 10, 20 y 21 fallidas.
        self.assertEqual((resultados[7], resultados[18]), ("OK", "OK"))
        self.assertTrue(all(resultados[n] == "ERROR" for n in (8, 9, 10, 20, 21)))

    def test_simulacion_genera_archivo_de_log(self):
        """Los errores quedan registrados en el archivo de logs."""
        ejecutar_demo()
        ruta = obtener_registro().ruta
        self.assertTrue(ruta.exists())
        contenido = ruta.read_text(encoding="utf-8")
        self.assertIn("Inicio de la simulación", contenido)
        self.assertIn("Fin de la simulación", contenido)

    def test_no_se_importa_django(self):
        """La solución no depende de Django ni de bases de datos."""
        self.assertFalse(any(nombre.startswith("django") for nombre in sys.modules))


if __name__ == "__main__":
    unittest.main()
