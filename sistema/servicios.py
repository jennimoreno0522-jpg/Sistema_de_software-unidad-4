"""Servicios especializados con herencia, polimorfismo y sobrecarga de cálculo."""

from __future__ import annotations

from abc import abstractmethod

from sistema.entidades import Entidad
from sistema.excepciones import (
    CalculoInconsistente,
    DatoInvalido,
    ParametroFaltante,
    ServicioNoDisponible,
)

NIVELES_ASESORIA = {"basica": 1.0, "intermedia": 1.35, "avanzada": 1.8}


class Servicio(Entidad):
    """Clase abstracta que define la interfaz común de todos los servicios."""

    def __init__(self, nombre: str, tarifa_base: float, disponible: bool = True, identificador: str | None = None):
        super().__init__(identificador)
        self.__nombre = nombre.strip() if isinstance(nombre, str) else ""
        # La tarifa se convierte aquí para detectar datos no numéricos de inmediato.
        try:
            self.__tarifa_base = float(tarifa_base)
        except (TypeError, ValueError) as exc:
            raise DatoInvalido(
                "La tarifa base debe ser un número.", {"campo": "tarifa_base"}
            ) from exc
        self.__disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        """Nombre comercial del servicio."""
        return self.__nombre

    @property
    def tarifa_base(self) -> float:
        """Tarifa por unidad u hora, según el servicio."""
        return self.__tarifa_base

    @property
    def disponible(self) -> bool:
        """Indica si el servicio puede reservarse."""
        return self.__disponible

    def validar(self) -> None:
        """Valida los atributos comunes a todos los servicios."""
        if len(self.__nombre) < 3:
            raise DatoInvalido(
                "El nombre del servicio debe tener al menos 3 caracteres.",
                {"campo": "nombre", "valor": self.__nombre},
            )
        if self.__tarifa_base < 0:
            raise DatoInvalido(
                "La tarifa base no puede ser negativa.",
                {"campo": "tarifa_base", "valor": self.__tarifa_base},
            )

    def validar_disponibilidad(self) -> None:
        """Impide reservar un servicio inactivo."""
        if not self.__disponible:
            raise ServicioNoDisponible(
                f"El servicio «{self.__nombre}» no está disponible.",
                {"servicio": self.__nombre},
            )

    @abstractmethod
    def describir(self) -> str:
        """Devuelve la descripción polimórfica del servicio."""

    @abstractmethod
    def validar_parametros(self, parametros: dict) -> dict:
        """Normaliza y valida los parámetros propios de cada servicio."""

    @staticmethod
    def _numero(valor, campo: str) -> float:
        """Convierte un valor a float o lanza CalculoInconsistente encadenado."""
        try:
            return float(valor)
        except (TypeError, ValueError) as exc:
            raise CalculoInconsistente(
                f"El parámetro «{campo}» debe ser numérico.", {"campo": campo}
            ) from exc

    @staticmethod
    def _entero(valor, campo: str) -> int:
        """Convierte a entero o lanza DatoInvalido encadenado con el error original."""
        try:
            numero = float(valor)
            if not numero.is_integer():
                raise ValueError(valor)
            return int(numero)
        except (TypeError, ValueError, OverflowError) as exc:
            raise DatoInvalido(
                f"«{campo}» debe ser un número entero.", {"campo": campo, "valor": valor}
            ) from exc

    @staticmethod
    def _entero_positivo(valor, campo: str) -> int:
        """Convierte un valor a entero positivo o falla con DatoInvalido."""
        numero = Servicio._numero(valor, campo)
        if numero <= 0 or not numero.is_integer():
            raise DatoInvalido(
                f"«{campo}» debe ser un entero mayor que cero.",
                {"campo": campo, "valor": valor},
            )
        return int(numero)

    def calcular_costo(self, *args, **kwargs) -> float:
        """Calcula el costo; admite varias firmas (método sobrecargado).

        Formas admitidas:
        ``calcular_costo()``, ``calcular_costo(horas)``,
        ``calcular_costo(horas, impuestos)``,
        ``calcular_costo(horas, impuestos, descuento)``,
        ``calcular_costo({"horas": 2, ...})`` y ``calcular_costo(horas=2, ...)``.
        """
        horas = 1
        impuestos = 0
        descuento = 0
        # Los parámetros propios del servicio pueden venir en ``parametros`` o
        # directamente como argumentos de palabra clave.
        parametros: dict = dict(kwargs.pop("parametros", {}))

        # Primero se resuelve la firma posicional (sobrecarga por cantidad y tipo
        # de argumentos) y después se leen las palabras clave en todos los casos.
        if len(args) == 1 and isinstance(args[0], dict):
            datos = dict(args[0])
            kwargs = {**datos, **kwargs}
        elif len(args) == 1:
            horas = args[0]
        elif len(args) == 2:
            horas, impuestos = args
        elif len(args) == 3:
            horas, impuestos, descuento = args
        elif len(args) > 3:
            raise ParametroFaltante(
                "calcular_costo admite como máximo horas, impuestos y descuento.",
                {"recibidos": len(args)},
            )

        # Las palabras clave solo completan lo que no llegó de forma posicional.
        if len(args) < 1 or isinstance(args[0], dict):
            horas = kwargs.pop("horas", horas)
        if len(args) < 2:
            impuestos = kwargs.pop("impuestos", impuestos)
        if len(args) < 3:
            descuento = kwargs.pop("descuento", descuento)
        parametros.update(kwargs)

        horas = self._numero(horas, "horas")
        impuestos = self._numero(impuestos, "impuestos")
        descuento = self._numero(descuento, "descuento")

        # Los porcentajes se reciben como decimales: 0.19 equivale al 19 %.
        if horas <= 0:
            raise DatoInvalido("La duración debe ser mayor que cero.", {"campo": "horas"})
        if not 0 <= impuestos <= 1:
            raise DatoInvalido(
                "Los impuestos deben estar entre 0 y 1.", {"campo": "impuestos"}
            )
        if not 0 <= descuento <= 1:
            raise DatoInvalido(
                "El descuento debe estar entre 0 y 1.", {"campo": "descuento"}
            )

        parametros = self.validar_parametros(parametros)
        total = self._calcular_base(horas, impuestos, descuento, parametros)
        if total < 0:
            raise CalculoInconsistente("El costo calculado no puede ser negativo.")
        return round(total, 2)

    def calcular_costo_con_impuestos(self, horas: float, impuestos: float, **parametros) -> float:
        """Variante sobrecargada: calcula el costo aplicando solo impuestos."""
        return self.calcular_costo(horas, impuestos, 0, **parametros)

    def calcular_costo_con_descuento(self, horas: float, descuento: float, **parametros) -> float:
        """Variante sobrecargada: calcula el costo aplicando solo un descuento."""
        return self.calcular_costo(horas, 0, descuento, **parametros)

    def _subtotal(self, horas: float, parametros: dict) -> float:
        """Subtotal sin descuento ni impuestos; cada servicio lo sobrescribe."""
        return self.__tarifa_base * horas

    def _calcular_base(self, horas: float, impuestos: float, descuento: float, parametros: dict) -> float:
        """Fórmula común: subtotal propio del servicio, descuento y luego impuestos."""
        return self._subtotal(horas, parametros) * (1 - descuento) * (1 + impuestos)

    def resumen(self) -> str:
        """El resumen de un servicio es su descripción especializada."""
        return self.describir()


class ReservaSala(Servicio):
    """Alquiler de salas; exige la capacidad requerida."""

    def __init__(self, nombre: str, tarifa_por_hora: float, capacidad_maxima: int, **kwargs):
        super().__init__(nombre, tarifa_por_hora, **kwargs)
        self.__capacidad_maxima = self._entero(capacidad_maxima, "capacidad_maxima")

    @property
    def capacidad_maxima(self) -> int:
        """Cantidad máxima de personas admitidas en la sala."""
        return self.__capacidad_maxima

    def validar(self) -> None:
        """Valida los datos comunes y el cupo de la sala."""
        super().validar()
        if self.__capacidad_maxima <= 0:
            raise DatoInvalido(
                "La capacidad máxima debe ser mayor que cero.",
                {"campo": "capacidad_maxima"},
            )

    def describir(self) -> str:
        """Describe la sala y su capacidad."""
        return f"Sala «{self.nombre}» · ${self.tarifa_base:,.0f}/h · cupo {self.__capacidad_maxima}"

    def validar_parametros(self, parametros: dict) -> dict:
        """Valida que la capacidad solicitada exista y sea positiva."""
        if "capacidad" not in parametros:
            raise ParametroFaltante(
                "La reserva de sala requiere el parámetro «capacidad».",
                {"campo": "capacidad"},
            )
        capacidad = self._entero_positivo(parametros["capacidad"], "capacidad")
        if capacidad > self.__capacidad_maxima:
            raise DatoInvalido(
                "La capacidad solicitada supera el cupo de la sala.",
                {"campo": "capacidad", "valor": capacidad},
            )
        return {"capacidad": capacidad}

    def _subtotal(self, horas, parametros) -> float:
        """Sobrescribe el subtotal añadiendo un recargo por gran capacidad."""
        recargo = max(0, parametros["capacidad"] - 10) * 5000
        return super()._subtotal(horas, parametros) + recargo


class AlquilerEquipos(Servicio):
    """Alquiler de equipos; exige cantidad de unidades."""

    def __init__(self, nombre: str, tarifa_por_hora: float, unidades_disponibles: int, **kwargs):
        super().__init__(nombre, tarifa_por_hora, **kwargs)
        self.__unidades_disponibles = self._entero(unidades_disponibles, "unidades_disponibles")

    @property
    def unidades_disponibles(self) -> int:
        """Unidades disponibles en inventario."""
        return self.__unidades_disponibles

    def validar(self) -> None:
        """Valida los datos comunes y el inventario disponible."""
        super().validar()
        if self.__unidades_disponibles <= 0:
            raise DatoInvalido(
                "Debe existir al menos una unidad en inventario.",
                {"campo": "unidades_disponibles"},
            )

    def describir(self) -> str:
        """Describe el equipo y las unidades existentes."""
        return f"Equipo «{self.nombre}» · ${self.tarifa_base:,.0f}/h · {self.__unidades_disponibles} uds."

    def validar_parametros(self, parametros: dict) -> dict:
        """Valida la cantidad solicitada contra el inventario."""
        if "cantidad" not in parametros:
            raise ParametroFaltante(
                "El alquiler requiere el parámetro «cantidad».", {"campo": "cantidad"}
            )
        cantidad = self._entero_positivo(parametros["cantidad"], "cantidad")
        if cantidad > self.__unidades_disponibles:
            raise DatoInvalido(
                "No hay suficientes unidades disponibles.",
                {"campo": "cantidad", "valor": cantidad},
            )
        return {"cantidad": cantidad}

    def _subtotal(self, horas, parametros) -> float:
        """Sobrescribe el subtotal multiplicando por las unidades alquiladas."""
        return super()._subtotal(horas, parametros) * parametros["cantidad"]


class AsesoriaEspecializada(Servicio):
    """Asesoría profesional; exige un nivel de complejidad."""

    def __init__(self, nombre: str, tarifa_por_hora: float, especialista: str, **kwargs):
        super().__init__(nombre, tarifa_por_hora, **kwargs)
        self.__especialista = especialista.strip() if isinstance(especialista, str) else ""

    @property
    def especialista(self) -> str:
        """Nombre del especialista asignado."""
        return self.__especialista

    def validar(self) -> None:
        """Valida los datos comunes y la asignación del especialista."""
        super().validar()
        if len(self.__especialista.strip()) < 3:
            raise DatoInvalido(
                "Debe indicar el nombre del especialista.", {"campo": "especialista"}
            )

    def describir(self) -> str:
        """Describe la asesoría y al especialista."""
        return f"Asesoría «{self.nombre}» · {self.__especialista} · ${self.tarifa_base:,.0f}/h"

    def validar_parametros(self, parametros: dict) -> dict:
        """Valida que el nivel de la asesoría sea reconocido."""
        nivel = parametros.get("nivel")
        if nivel is None:
            raise ParametroFaltante(
                "La asesoría requiere el parámetro «nivel».", {"campo": "nivel"}
            )
        nivel = str(nivel).strip().lower()
        nivel = {"basico": "basica", "básico": "basica"}.get(nivel, nivel)
        if nivel not in NIVELES_ASESORIA:
            raise DatoInvalido(
                "El nivel debe ser básico, intermedio o avanzado.",
                {"campo": "nivel", "valor": nivel},
            )
        return {"nivel": nivel}

    def _subtotal(self, horas, parametros) -> float:
        """Sobrescribe el subtotal aplicando el multiplicador del nivel."""
        return super()._subtotal(horas, parametros) * NIVELES_ASESORIA[parametros["nivel"]]
