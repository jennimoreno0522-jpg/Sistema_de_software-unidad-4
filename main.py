"""Punto de entrada de la aplicación Software FJ.

La ejecución no requiere instalar dependencias ni configurar bases de datos:
toda la información vive en objetos y listas en memoria.
"""

from __future__ import annotations

from sistema.demo import ejecutar_demo


def main() -> None:
    """Ejecuta la simulación completa de operaciones."""
    ejecutar_demo()


if __name__ == "__main__":
    main()
