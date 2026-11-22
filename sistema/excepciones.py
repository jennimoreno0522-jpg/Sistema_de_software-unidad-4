"""Excepciones personalizadas del sistema Software FJ.

Cada excepción conserva un código legible y un diccionario de detalles para que
la capa de presentación pueda mostrar mensajes claros sin perder información
técnica. La clase base admite encadenamiento explícito de excepciones.
"""

from __future__ import annotations


class ErrorSistema(Exception):
    """Error base de todas las reglas de negocio del sistema."""

    codigo = "error_sistema"

    def __init__(self, mensaje: str, detalles: dict | None = None, causa: Exception | None = None):
        # Se guarda el mensaje como atributo propio para accederlo sin str(exc).
        super().__init__(mensaje)
        self.mensaje = mensaje
        # Los detalles permiten reportar el campo o parámetro que falló.
        self.detalles = detalles or {}
        # El encadenamiento explica qué error original provocó este error.
        if causa is not None:
            self.__cause__ = causa


class DatoInvalido(ErrorSistema):
    """Se lanza cuando un dato no cumple las validaciones establecidas."""

    codigo = "dato_invalido"


class ParametroFaltante(ErrorSistema):
    """Se lanza cuando no se entrega un parámetro obligatorio."""

    codigo = "parametro_faltante"


class OperacionNoPermitida(ErrorSistema):
    """Se lanza cuando el estado del objeto no permite la operación."""

    codigo = "operacion_no_permitida"


class DuplicadoError(ErrorSistema):
    """Se lanza cuando se intenta registrar dos veces la misma entidad."""

    codigo = "duplicado"


class ReservaInvalida(ErrorSistema):
    """Se lanza cuando una reserva no es consistente o no puede procesarse."""

    codigo = "reserva_invalida"


class ServicioNoDisponible(ErrorSistema):
    """Se lanza cuando el servicio solicitado está inactivo."""

    codigo = "servicio_no_disponible"


class CalculoInconsistente(ErrorSistema):
    """Se lanza cuando los parámetros de cálculo producen un costo inválido."""

    codigo = "calculo_inconsistente"
