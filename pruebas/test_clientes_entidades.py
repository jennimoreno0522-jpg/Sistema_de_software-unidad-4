"""Pruebas de la clase abstracta Entidad y de la clase Cliente."""

from __future__ import annotations

import unittest

from sistema.clientes import Cliente
from sistema.entidades import Entidad
from sistema.excepciones import DatoInvalido


class EntidadTests(unittest.TestCase):
    """La clase abstracta no debe poder instanciarse directamente."""

    def test_entidad_es_abstracta(self):
        """Intentar instanciar Entidad produce TypeError."""
        with self.assertRaises(TypeError):
            Entidad()


class ClienteTests(unittest.TestCase):
    """Valida encapsulación, normalización y reglas de negocio."""

    def setUp(self):
        self.cliente = Cliente(
            "Laura Martínez", "CC1234", "laura@example.com", "3001234567", "Software FJ"
        )

    def test_cliente_hereda_de_entidad_y_tiene_identificador(self):
        """La herencia y la identidad funcionan sin base de datos."""
        self.assertIsInstance(self.cliente, Entidad)
        self.assertEqual(len(self.cliente.id), 8)
        self.assertEqual(self.cliente.id, self.cliente.id)

    def test_datos_se_normalizan(self):
        """Espacios y mayúsculas se normalizan al construir el objeto."""
        cliente = Cliente("  Pedro Soto ", " cc9876 ", " PEDRO@EXAMPLE.COM ")
        self.assertEqual(cliente.nombre, "Pedro Soto")
        self.assertEqual(cliente.documento, "CC9876")
        self.assertEqual(cliente.email, "pedro@example.com")

    def test_nombre_invalido(self):
        """Un nombre demasiado corto lanza DatoInvalido."""
        with self.assertRaises(DatoInvalido) as contexto:
            Cliente("A", "CC1000", "a@example.com").validar()
        self.assertEqual(contexto.exception.detalles["campo"], "nombre")

    def test_documento_invalido(self):
        """Un documento con menos de 4 caracteres se rechaza."""
        with self.assertRaises(DatoInvalido):
            Cliente("Ana Pérez", "12", "ana@example.com").validar()

    def test_requiere_al_menos_un_medio_de_contacto(self):
        """Un cliente sin correo ni teléfono no es válido."""
        with self.assertRaises(DatoInvalido) as contexto:
            Cliente("Ana Pérez", "CC1000").validar()
        self.assertEqual(contexto.exception.detalles["campo"], "contacto")

    def test_encapsulacion_de_datos_personales(self):
        """No es posible modificar atributos privados mediante propiedades."""
        with self.assertRaises(AttributeError):
            self.cliente.nombre = "Otro nombre"
        with self.assertRaises(AttributeError):
            self.cliente.email = "otro@example.com"

    def test_cambios_validados_y_estado_activo(self):
        """Los cambios pasan validación y el estado se puede alternar."""
        self.cliente.cambiar_email("NUEVO@EXAMPLE.COM")
        self.assertEqual(self.cliente.email, "nuevo@example.com")
        with self.assertRaises(DatoInvalido):
            self.cliente.cambiar_email("correo-invalido")
        self.cliente.desactivar()
        self.assertFalse(self.cliente.activo)
        self.cliente.activar()
        self.assertTrue(self.cliente.activo)

    def test_resumen_incluye_estado(self):
        """El resumen refleja el estado actual del cliente."""
        self.assertIn("activo", self.cliente.resumen())
        self.cliente.desactivar()
        self.assertIn("inactivo", self.cliente.resumen())


if __name__ == "__main__":
    unittest.main()
