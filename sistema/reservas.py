"""Reserva que integra cliente, servicio, duración, estado y procesamiento."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from sistema.clientes import Cliente
from sistema.entidades import Entidad
from sistema.excepciones import (
    CalculoInconsistente,
    DatoInvalido,
    OperacionNoPermitida,
    ParametroFaltante,
    ReservaInvalida,
    ServicioNoDisponible,
)
from sistema.logging_eventos import obtener_registro
from sistema.servicios import Servicio


class EstadoReserva(Enum):
    """Estados permitidos en el ciclo de vida de una reserva."""

    CREADA = "creada"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    PROCESADA = "procesada"


class Reserva(Entidad):
    """Reserva de un servicio por parte de un cliente.

    La clase coordina a los demás objetos del dominio y demuestra el manejo
    avanzado de excepciones con ``try/except/else/finally`` y encadenamiento.
    """

    def __init__(self, cliente, servicio, duracion_horas=1, parametros=None, identificador=None):
        super().__init__(identificador)
        self.__cliente = cliente
        self.__servicio = servicio
        # Se convierte la duración de forma segura para no perder el error original.
        try:
            self.__duracion = float(duracion_horas)
        except (TypeError, ValueError) as exc:
            raise ReservaInvalida(
                "La duración debe ser un número.", {"campo": "duracion_horas"}
            ) from exc
        self.__parametros = dict(parametros or {})
        self.__estado = EstadoReserva.CREADA
        self.__costo = 0.0
        self.__motivo_cancelacion = ""
        self.__creada_en = datetime.now()

    @property
    def cliente(self):
        """Cliente titular de la reserva."""
        return self.__cliente

    @property
    def servicio(self):
        """Servicio reservado."""
        return self.__servicio

    @property
    def duracion_horas(self) -> float:
        """Duración contratada en horas."""
        return self.__duracion

    @property
    def parametros(self) -> dict:
        """Copia de los parámetros específicos del servicio."""
        return dict(self.__parametros)

    @property
    def estado(self) -> EstadoReserva:
        """Estado actual de la reserva."""
        return self.__estado

    @property
    def costo(self) -> float:
        """Costo calculado una vez procesada la reserva."""
        return self.__costo

    @property
    def creada_en(self) -> datetime:
        """Fecha y hora de creación."""
        return self.__creada_en

    def validar(self) -> None:
        """Valida la reserva y traduce errores de entidades a ReservaInvalida."""
        if not isinstance(self.__cliente, Cliente):
            raise ReservaInvalida(
                "La reserva requiere un cliente válido.", {"campo": "cliente"}
            )
        if not isinstance(self.__servicio, Servicio):
            raise ReservaInvalida(
                "La reserva requiere un servicio válido.", {"campo": "servicio"}
            )
        try:
            self.__cliente.validar()
            self.__servicio.validar()
        except (DatoInvalido, ReservaInvalida) as exc:
            raise ReservaInvalida(
                "La reserva contiene entidades inválidas.", {"reserva": self.id}
            ) from exc
        if not self.__cliente.activo:
            raise ReservaInvalida(
                "El cliente está inactivo y no puede reservar.",
                {"cliente": self.__cliente.documento},
            )
        if self.__duracion <= 0:
            raise ReservaInvalida(
                "La duración debe ser mayor que cero.", {"duracion": self.__duracion}
            )

    def confirmar(self) -> None:
        """Confirma una reserva creada, verificando disponibilidad del servicio."""
        registro = obtener_registro()
        if self.__estado is not EstadoReserva.CREADA:
            raise OperacionNoPermitida(
                "Solo una reserva creada puede confirmarse.", {"estado": self.__estado.value}
            )
        try:
            self.__servicio.validar_disponibilidad()
            self.validar()
        except ServicioNoDisponible as exc:
            registro.error("Reserva no confirmada: servicio no disponible", exc)
            raise
        except ReservaInvalida as exc:
            registro.error("Reserva no confirmada: datos inválidos", exc)
            raise
        else:
            self.__estado = EstadoReserva.CONFIRMADA
            registro.evento("Reserva confirmada", reserva=self.id, cliente=self.__cliente.documento)
        finally:
            registro.evento("Validación de confirmación finalizada", reserva=self.id)

    def cancelar(self, motivo: str = "") -> None:
        """Cancela una reserva que aún no ha sido procesada."""
        registro = obtener_registro()
        if self.__estado in {EstadoReserva.CANCELADA, EstadoReserva.PROCESADA}:
            raise OperacionNoPermitida(
                "No se puede cancelar una reserva cancelada o procesada.",
                {"estado": self.__estado.value},
            )
        self.__estado = EstadoReserva.CANCELADA
        self.__motivo_cancelacion = motivo.strip()
        registro.evento(
            "Reserva cancelada", reserva=self.id, motivo=self.__motivo_cancelacion
        )

    def procesar(self) -> float:
        """Calcula el costo y cierra la reserva; encapsula errores de negocio.

        Se usa ``try/except/else/finally``: el error se transforma en una
        ReservaInvalida encadenada, el éxito se registra en ``else`` y el
        evento de finalización siempre se escribe en ``finally``.
        """
        registro = obtener_registro()
        if self.__estado is not EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitida(
                "La reserva debe estar confirmada antes de procesarla.",
                {"estado": self.__estado.value},
            )
        try:
            self.validar()
            self.__costo = self.__servicio.calcular_costo(
                horas=self.__duracion, parametros=self.__parametros
            )
        except (
            DatoInvalido,
            ParametroFaltante,
            CalculoInconsistente,
            ServicioNoDisponible,
            ReservaInvalida,
        ) as exc:
            registro.error("Error al procesar la reserva", exc)
            raise ReservaInvalida(
                "No fue posible procesar la reserva.", {"reserva": self.id}
            ) from exc
        else:
            self.__estado = EstadoReserva.PROCESADA
            registro.evento(
                "Reserva procesada", reserva=self.id, costo=self.__costo
            )
        finally:
            registro.evento("Procesamiento finalizado", reserva=self.id)
        return self.__costo

    def resumen(self) -> str:
        """Devuelve una línea legible con el estado y el costo de la reserva."""
        return (
            f"{self.id} · {self.__cliente.nombre} · {self.__servicio.nombre} · "
            f"{self.__duracion:g}h · {self.__estado.value} · ${self.__costo:,.2f}"
        )
