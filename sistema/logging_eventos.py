"""Registro centralizado de eventos y errores en archivos de texto."""

from __future__ import annotations

import logging
from pathlib import Path

# La raíz del proyecto se calcula desde este archivo, así el log siempre queda
# en ``logs/sistema.log`` sin importar desde dónde se ejecute el programa.
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_LOG_POR_DEFECTO = RAIZ_PROYECTO / "logs" / "sistema.log"


class RegistroEventos:
    """Configura un logger único y escribe en ``logs/sistema.log``.

    Se usa composición en lugar de herencia porque el registro es un servicio
    técnico, no una entidad del dominio.
    """

    def __init__(self, ruta: str | Path = RUTA_LOG_POR_DEFECTO):
        self.ruta = Path(ruta)
        # La carpeta se crea antes de abrir el archivo para evitar FileNotFoundError.
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        self.__logger = logging.getLogger("software_fj")
        self.__logger.setLevel(logging.DEBUG)
        self.__logger.propagate = False
        # Se evita duplicar manejadores cuando el módulo se recarga en las pruebas.
        if not self.__logger.handlers:
            manejador = logging.FileHandler(self.ruta, mode="a", encoding="utf-8")
            manejador.setFormatter(
                logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
            )
            self.__logger.addHandler(manejador)

    def evento(self, mensaje: str, **detalles) -> None:
        """Registra un evento correcto con sus detalles opcionales."""
        self.__logger.info("%s | %s", mensaje, detalles or {})

    def advertencia(self, mensaje: str, **detalles) -> None:
        """Registra una situación anómala que no detiene la ejecución."""
        self.__logger.warning("%s | %s", mensaje, detalles or {})

    def error(self, mensaje: str, excepcion: Exception | None = None) -> None:
        """Registra un error y, si existe, la traza de la excepción encadenada."""
        if excepcion is None:
            self.__logger.error(mensaje)
        else:
            self.__logger.error("%s: %s", mensaje, excepcion, exc_info=True)


_registro = RegistroEventos()


def obtener_registro() -> RegistroEventos:
    """Devuelve el registro compartido por todos los módulos."""
    return _registro
