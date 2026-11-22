"""Cliente con encapsulación de datos personales y validaciones estrictas."""

from __future__ import annotations

import re

from sistema.entidades import Entidad
from sistema.excepciones import DatoInvalido, OperacionNoPermitida

PATRON_NOMBRE = re.compile(r"^[\w\s.\-&]{3,120}$", re.UNICODE)
PATRON_DOCUMENTO = re.compile(r"^[A-Za-z0-9\-]{4,20}$")
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PATRON_TELEFONO = re.compile(r"^[+0-9][0-9\s()\-]{6,19}$")


class Cliente(Entidad):
    """Representa a un cliente de Software FJ.

    Los atributos sensibles son privados y solo se exponen lecturas mediante
    propiedades. Las modificaciones pasan por métodos que validan el nuevo
    valor, garantizando encapsulación e invariantes del objeto.
    """

    def __init__(
        self,
        nombre: str,
        documento: str,
        email: str = "",
        telefono: str = "",
        empresa: str = "",
        identificador: str | None = None,
    ):
        super().__init__(identificador)
        # Se normaliza la entrada antes de guardarla para evitar espacios extra.
        self.__nombre = nombre.strip() if isinstance(nombre, str) else ""
        self.__documento = documento.strip().upper() if isinstance(documento, str) else ""
        self.__email = email.strip().lower() if isinstance(email, str) else ""
        self.__telefono = telefono.strip() if isinstance(telefono, str) else ""
        self.__empresa = empresa.strip() if isinstance(empresa, str) else ""
        self.__activo = True

    @property
    def nombre(self) -> str:
        """Nombre completo del cliente."""
        return self.__nombre

    @property
    def documento(self) -> str:
        """Número de documento normalizado."""
        return self.__documento

    @property
    def email(self) -> str:
        """Correo electrónico normalizado."""
        return self.__email

    @property
    def telefono(self) -> str:
        """Teléfono de contacto."""
        return self.__telefono

    @property
    def empresa(self) -> str:
        """Empresa asociada al cliente, si la hay."""
        return self.__empresa

    @property
    def activo(self) -> bool:
        """Indica si el cliente puede contratar servicios."""
        return self.__activo

    @staticmethod
    def __validar_campo(valor: str, patron: re.Pattern, campo: str, mensaje: str) -> None:
        """Aplica un patrón y lanza DatoInvalido si el valor no coincide."""
        if valor and not patron.match(valor):
            raise DatoInvalido(mensaje, {"campo": campo, "valor": valor})

    def validar(self) -> None:
        """Comprueba todas las reglas de negocio del cliente."""
        if not PATRON_NOMBRE.match(self.__nombre):
            raise DatoInvalido(
                "El nombre debe tener entre 3 y 120 caracteres válidos.",
                {"campo": "nombre", "valor": self.__nombre},
            )
        if not PATRON_DOCUMENTO.match(self.__documento):
            raise DatoInvalido(
                "El documento debe tener entre 4 y 20 caracteres alfanuméricos.",
                {"campo": "documento", "valor": self.__documento},
            )
        # Estos dos campos son opcionales, pero al menos uno debe existir.
        self.__validar_campo(
            self.__email, PATRON_CORREO, "email", "El correo electrónico no es válido."
        )
        self.__validar_campo(
            self.__telefono, PATRON_TELEFONO, "telefono", "El teléfono no es válido."
        )
        if not self.__email and not self.__telefono:
            raise DatoInvalido(
                "Debe registrar un correo electrónico o un teléfono.",
                {"campo": "contacto"},
            )

    def cambiar_email(self, nuevo_email: str) -> None:
        """Actualiza el correo después de validarlo, conservando el estado."""
        valor = nuevo_email.strip().lower()
        self.__validar_campo(valor, PATRON_CORREO, "email", "El correo electrónico no es válido.")
        self.__email = valor

    def cambiar_telefono(self, nuevo_telefono: str) -> None:
        """Actualiza el teléfono después de validarlo."""
        valor = nuevo_telefono.strip()
        self.__validar_campo(valor, PATRON_TELEFONO, "telefono", "El teléfono no es válido.")
        self.__telefono = valor

    def desactivar(self) -> None:
        """Marca el cliente como inactivo para impedir nuevas reservas."""
        self.__activo = False

    def activar(self) -> None:
        """Reactiva un cliente previamente desactivado."""
        self.__activo = True

    def resumen(self) -> str:
        """Devuelve el resumen legible usado por consola, logs y pruebas."""
        estado = "activo" if self.__activo else "inactivo"
        return f"{self.__nombre} · {self.__documento} · {estado}"
