"""Gestores en memoria: usan listas internas, sin motor de base de datos."""

from __future__ import annotations

from sistema.clientes import Cliente
from sistema.excepciones import DuplicadoError, ReservaInvalida
from sistema.logging_eventos import obtener_registro
from sistema.reservas import EstadoReserva, Reserva
from sistema.servicios import Servicio


class GestorClientes:
    """Administra una lista privada de clientes."""

    def __init__(self):
        self.__clientes: list[Cliente] = []
        self.__registro = obtener_registro()

    def agregar(self, cliente: Cliente) -> Cliente:
        """Valida y agrega un cliente, rechazando documentos repetidos."""
        cliente.validar()
        if any(item.documento == cliente.documento for item in self.__clientes):
            raise DuplicadoError(
                "Ya existe un cliente con ese documento.",
                {"documento": cliente.documento},
            )
        self.__clientes.append(cliente)
        self.__registro.evento("Cliente registrado", cliente=cliente.documento)
        return cliente

    def buscar(self, documento: str) -> Cliente | None:
        """Busca un cliente por documento; devuelve None si no existe."""
        objetivo = documento.strip().upper()
        return next((item for item in self.__clientes if item.documento == objetivo), None)

    def todos(self) -> list[Cliente]:
        """Devuelve una copia de la lista para proteger el estado interno."""
        return list(self.__clientes)


class GestorServicios:
    """Administra una lista privada de servicios."""

    def __init__(self):
        self.__servicios: list[Servicio] = []
        self.__registro = obtener_registro()

    def agregar(self, servicio: Servicio) -> Servicio:
        """Valida y agrega un servicio, rechazando nombres repetidos."""
        servicio.validar()
        if any(item.nombre.lower() == servicio.nombre.lower() for item in self.__servicios):
            raise DuplicadoError(
                "Ya existe un servicio con ese nombre.", {"nombre": servicio.nombre}
            )
        self.__servicios.append(servicio)
        self.__registro.evento("Servicio registrado", servicio=servicio.nombre)
        return servicio

    def buscar(self, nombre: str) -> Servicio | None:
        """Busca un servicio por nombre exacto, sin distinguir mayúsculas."""
        objetivo = nombre.strip().lower()
        return next((item for item in self.__servicios if item.nombre.lower() == objetivo), None)

    def todos(self) -> list[Servicio]:
        """Devuelve una copia de la lista de servicios."""
        return list(self.__servicios)


class GestorReservas:
    """Administra una lista privada de reservas y su ciclo de vida."""

    def __init__(self):
        self.__reservas: list[Reserva] = []
        self.__registro = obtener_registro()

    def crear(self, cliente: Cliente, servicio: Servicio, duracion_horas: int = 1, parametros=None) -> Reserva:
        """Crea una reserva válida y la incorpora a la lista interna."""
        reserva = Reserva(cliente, servicio, duracion_horas, parametros)
        reserva.validar()
        self.__reservas.append(reserva)
        self.__registro.evento(
            "Reserva creada", reserva=reserva.id, cliente=cliente.documento
        )
        return reserva

    def __obtener(self, identificador: str) -> Reserva:
        """Busca una reserva por identificador o falla con ReservaInvalida."""
        reserva = next((item for item in self.__reservas if item.id == identificador), None)
        if reserva is None:
            raise ReservaInvalida(
                "No existe una reserva con ese identificador.", {"reserva": identificador}
            )
        return reserva

    def confirmar(self, identificador: str) -> Reserva:
        """Confirma la reserva indicada."""
        reserva = self.__obtener(identificador)
        reserva.confirmar()
        return reserva

    def procesar(self, identificador: str) -> float:
        """Procesa la reserva indicada y devuelve su costo."""
        return self.__obtener(identificador).procesar()

    def cancelar(self, identificador: str, motivo: str = "") -> Reserva:
        """Cancela la reserva indicada."""
        reserva = self.__obtener(identificador)
        reserva.cancelar(motivo)
        return reserva

    def todas(self) -> list[Reserva]:
        """Devuelve una copia de la lista de reservas."""
        return list(self.__reservas)

    def facturado_total(self) -> float:
        """Suma el costo de todas las reservas procesadas."""
        return round(
            sum(item.costo for item in self.__reservas if item.estado is EstadoReserva.PROCESADA),
            2,
        )
