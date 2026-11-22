# Sistema Integral de Gestión de Clientes, Servicios y Reservas — Software FJ

Proyecto en equipo (cinco integrantes) de la Fase 4 del curso **Programación (213023)** de la UNAD, Ingeniería de Sistemas.
Aplicación de consola **orientada a objetos, sin motor de base de datos**, que gestiona clientes, servicios y reservas y continúa funcionando ante errores controlados.

## Cumplimiento del Anexo 3

| Requisito | Implementación |
| --- | --- |
| Sin base de datos | Información en objetos y listas privadas; archivos solo para logs. |
| Clase abstracta de entidades | `sistema/entidades.py` → `Entidad(ABC)`. |
| Cliente validado y encapsulado | `sistema/clientes.py` → `Cliente` con propiedades sin setters públicos. |
| `Servicio` abstracto + 3 especializados | `Servicio`, `ReservaSala`, `AlquilerEquipos`, `AsesoriaEspecializada`. |
| Polimorfismo y métodos sobrescritos | `describir()`, `validar_parametros()`, `_subtotal()`. |
| Métodos sobrecargados | `calcular_costo()` admite kwargs, diccionario y hasta tres argumentos posicionales (horas, impuestos, descuento); además `calcular_costo_con_impuestos()` y `calcular_costo_con_descuento()`. |
| Reserva con estado y ciclo de vida | `sistema/reservas.py` → `Reserva` + `EstadoReserva`. |
| Excepciones personalizadas | `sistema/excepciones.py` → `ErrorSistema` y seis subclases. |
| Manejo avanzado de errores | `try/except`, `try/except/else`, `try/except/finally` y `raise ... from exc`. |
| Logs de eventos y errores | `sistema/logging_eventos.py` → `logs/sistema.log`. |
| Simulación de operaciones | 22 operaciones válidas e inválidas en `sistema/demo.py` (mínimo exigido: 10). |

## Integrantes

| Integrante | Rol / módulo |
| --- | --- |
| _Nombre 1_ | _Completar_ |
| _Nombre 2_ | _Completar_ |
| _Nombre 3_ | _Completar_ |
| _Nombre 4_ | _Completar_ |
| _Nombre 5_ | _Completar_ |

## Estructura

```
main.py                      Punto de entrada.
sistema/
  __init__.py                Paquete del dominio.
  excepciones.py             Excepciones de negocio con código y detalles.
  entidades.py               Clase abstracta Entidad.
  clientes.py                Entidad Cliente.
  servicios.py               Jerarquía polimórfica de servicios.
  reservas.py                Ciclo de vida de reservas.
  gestores.py                Listas en memoria de clientes, servicios y reservas.
  logging_eventos.py         Registro en logs/sistema.log.
  demo.py                    Simulación de 22 operaciones.
pruebas/                     Pruebas unitarias por módulo.
```

## Ejecución

La aplicación usa solo la biblioteca estándar de Python 3.10+; no requiere instalar dependencias ni configurar bases de datos.

```powershell
python main.py
python -m unittest discover -s pruebas -v
```

Salida esperada: **22 operaciones** (8 exitosas y 14 fallas controladas), facturación de las reservas procesadas y el mensaje final `ESTADO FINAL DEL SISTEMA: activo`.

## Decisiones de diseño

- `Cliente`, `Servicio` y `Reserva` heredan de `Entidad`, que entrega un identificador corto y define la interfaz `validar()` / `resumen()`.
- Cada servicio conoce sus propias reglas: cupo de sala, inventario de equipos y nivel de asesoría.
- `Reserva.procesar()` encapsula errores de negocio en `ReservaInvalida` usando encadenamiento, registra el éxito en `else` y siempre finaliza en `finally`.
- Cada servicio sobrescribe `_subtotal()`; el descuento y los impuestos se aplican siempre después, de modo que recargos, unidades y nivel de asesoría se calculan igual en todas las firmas de `calcular_costo()`.
- `Reserva.validar()` rechaza clientes o servicios ausentes con `ReservaInvalida`, y los servicios convierten capacidad e inventario no numéricos en `DatoInvalido` encadenado.
- La ruta del log se calcula desde la raíz del proyecto: `logs/sistema.log` se crea en el mismo lugar sin importar desde dónde se ejecute.
- `_ejecutar()` en el demo captura cada falla y continúa con la siguiente operación.
- En Windows se recomienda ejecutar con `$env:PYTHONIOENCODING="utf-8"` para conservar acentos en consola y archivos.

## Pruebas

Las 48 pruebas `unittest` cubren excepciones, entidades, clientes, servicios, reservas, gestores, logging y la simulación completa. El flujo de CI ejecuta las pruebas y la demo.
