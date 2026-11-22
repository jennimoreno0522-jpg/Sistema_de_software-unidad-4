"""Pruebas del módulo de excepciones personalizadas."""

from __future__ import annotations

import unittest

from sistema.excepciones import (
    CalculoInconsistente,
    DatoInvalido,
    ErrorSistema,
    OperacionNoPermitida,
    ParametroFaltante,
    ReservaInvalida,
)


class ExcepcionesTests(unittest.TestCase):
    """Verifica códigos, detalles y encadenamiento de excepciones."""

    def test_todas_heredan_de_error_sistema(self):
        """Todas las excepciones de negocio comparten una base común."""
        clases = [
            DatoInvalido,
            ParametroFaltante,
            OperacionNoPermitida,
            ReservaInvalida,
            CalculoInconsistente,
        ]
        for clase in clases:
            with self.subTest(clase=clase.__name__):
                self.assertTrue(issubclass(clase, ErrorSistema))

    def test_codigo_y_detalles_se_conservan(self):
        """El código y los detalles permiten mostrar mensajes precisos."""
        error = DatoInvalido("Documento inválido", {"campo": "documento"})
        self.assertEqual(error.codigo, "dato_invalido")
        self.assertEqual(error.detalles["campo"], "documento")
        self.assertEqual(str(error), "Documento inválido")

    def test_encadenamiento_explicito_de_excepciones(self):
        """La causa original se mantiene accesible mediante __cause__."""
        original = ValueError("no es número")
        try:
            try:
                raise original
            except ValueError as exc:
                raise CalculoInconsistente("Cálculo inválido") from exc
        except CalculoInconsistente as exc:
            self.assertIs(exc.__cause__, original)


if __name__ == "__main__":
    unittest.main()
