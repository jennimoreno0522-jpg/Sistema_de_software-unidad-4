"""Clase abstracta base de todas las entidades del dominio."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import uuid4


class Entidad(ABC):
    """Define identidad, validación obligatoria y representación común.

    La herencia de ``ABC`` impide instanciar esta clase directamente: solo las
    clases concretas que implementen ``validar`` y ``resumen`` pueden crearse.
    """

    def __init__(self, identificador: str | None = None):
        # El identificador se encapsula con doble guion bajo para evitar cambios
        # accidentales desde fuera de la clase.
        self.__identificador = identificador or uuid4().hex[:8].upper()

    @property
    def id(self) -> str:
        """Devuelve el identificador inmutable de la entidad."""
        return self.__identificador

    @abstractmethod
    def validar(self) -> None:
        """Comprueba que la entidad sea consistente; la implementa cada clase."""

    @abstractmethod
    def resumen(self) -> str:
        """Devuelve una descripción breve y legible de la entidad."""

    def __str__(self) -> str:
        # Al convertir la entidad a texto se usa el resumen Polimórfico.
        return self.resumen()

    def __repr__(self) -> str:
        # Representación técnica útil durante las pruebas y el logging.
        return f"<{type(self).__name__} id={self.__identificador}>"
