"""Simulación de operaciones reales con manejo controlado de errores.

Cada operación se ejecuta de forma secuencial: si una falla, se registra y el
programa continúa con la siguiente. Esto demuestra estabilidad y robustez.
"""

from __future__ import annotations

from sistema.clientes import Cliente
from sistema.excepciones import ErrorSistema
from sistema.gestores import GestorClientes, GestorReservas, GestorServicios
from sistema.logging_eventos import obtener_registro
from sistema.reservas import EstadoReserva
from sistema.servicios import AlquilerEquipos, AsesoriaEspecializada, ReservaSala


def _ejecutar(numero: int, descripcion: str, operacion) -> dict:
    """Ejecuta una operación con try/except/else/finally y reporta el resultado."""
    registro = obtener_registro()
    resultado = {"numero": numero, "operacion": descripcion, "estado": "ERROR", "mensaje": ""}
    print(f"\n[{numero:02d}] {descripcion}")
    try:
        mensaje = operacion()
    except ErrorSistema as exc:
        # Se capturan las excepciones de negocio sin detener la simulación.
        resultado["mensaje"] = f"{exc.codigo}: {exc.mensaje}"
        registro.error(f"Operación {numero} fallida: {descripcion}", exc)
        print(f"    ERROR -> {resultado['mensaje']}")
    except Exception as exc:
        # Red de seguridad: ningún error inesperado interrumpe el sistema.
        resultado["mensaje"] = f"error_inesperado: {exc}"
        registro.error(f"Error inesperado en operación {numero}", exc)
        print(f"    ERROR -> {resultado['mensaje']}")
    else:
        resultado["estado"] = "OK"
        resultado["mensaje"] = str(mensaje)
        registro.evento(f"Operación {numero} exitosa: {descripcion}")
        print(f"    OK -> {mensaje}")
    finally:
        # Este bloque se ejecuta siempre, haya o no haya error.
        registro.evento(f"Operación {numero} finalizada", estado=resultado["estado"])
    return resultado


def ejecutar_demo() -> list[dict]:
    """Ejecuta 22 operaciones y devuelve el detalle de cada una."""
    registro = obtener_registro()
    clientes = GestorClientes()
    servicios = GestorServicios()
    reservas = GestorReservas()

    print("=" * 78)
    print("SOFTWARE FJ - SIMULACION DE OPERACIONES (SIN BASE DE DATOS)")
    print("=" * 78)
    registro.evento("Inicio de la simulación de operaciones")

    cliente = None
    sala = None
    asesoria = None
    reserva_exitosa = None
    resultados = []

    resultados.append(_ejecutar(1, "Registrar cliente válido", lambda: clientes.agregar(
        Cliente("María Gómez", "CC1001", "maria@example.com", "3001112233", "Software FJ")
    ).resumen()))

    resultados.append(_ejecutar(2, "Registrar cliente con documento inválido", lambda: clientes.agregar(
        Cliente("Ana Pérez", "12", "ana@example.com", "3001112244")
    ).resumen()))

    resultados.append(_ejecutar(3, "Registrar cliente duplicado", lambda: clientes.agregar(
        Cliente("María Gómez", "CC1001", "otra@example.com", "3001112255")
    ).resumen()))

    resultados.append(_ejecutar(4, "Registrar servicio de reserva de sala", lambda: servicios.agregar(
        ReservaSala("Sala Élite", 200000, 20)
    ).describir()))

    resultados.append(_ejecutar(5, "Registrar servicio con tarifa negativa", lambda: servicios.agregar(
        AlquilerEquipos("Proyector", -50000, 4)
    ).describir()))

    def registrar_asesoria():
        nonlocal asesoria
        asesoria = AsesoriaEspecializada("Arquitectura", 350000, "Ing. Torres")
        return servicios.agregar(asesoria).describir()

    resultados.append(_ejecutar(6, "Registrar asesoría especializada", registrar_asesoria))

    def operacion_reserva_exitosa():
        nonlocal cliente, sala, reserva_exitosa
        cliente = clientes.buscar("CC1001")
        sala = servicios.buscar("Sala Élite")
        reserva_exitosa = reservas.crear(cliente, sala, 3, {"capacidad": 8})
        reservas.confirmar(reserva_exitosa.id)
        costo = reservas.procesar(reserva_exitosa.id)
        return f"{reserva_exitosa.resumen()} | costo ${costo:,.2f}"

    resultados.append(_ejecutar(7, "Crear, confirmar y procesar reserva válida", operacion_reserva_exitosa))

    def operacion_cliente_inactivo():
        inactivo = Cliente("Carlos Ruiz", "CC2002", "carlos@example.com", "3001112266")
        inactivo.desactivar()
        return reservas.crear(inactivo, sala, 2, {"capacidad": 5}).resumen()

    resultados.append(_ejecutar(8, "Crear reserva con cliente inactivo", operacion_cliente_inactivo))

    def operacion_servicio_no_disponible():
        no_disponible = ReservaSala("Sala Mantenimiento", 120000, 10, disponible=False)
        nueva = reservas.crear(cliente, no_disponible, 1, {"capacidad": 4})
        reservas.confirmar(nueva.id)
        return nueva.resumen()

    resultados.append(_ejecutar(9, "Reservar servicio no disponible", operacion_servicio_no_disponible))

    def operacion_capacidad_excedida():
        excedida = reservas.crear(cliente, sala, 2, {"capacidad": 50})
        reservas.confirmar(excedida.id)
        reservas.procesar(excedida.id)
        return excedida.resumen()

    resultados.append(_ejecutar(10, "Reservar sala con capacidad excedida", operacion_capacidad_excedida))

    resultados.append(_ejecutar(11, "Cancelar reserva ya procesada", lambda: reserva_exitosa.cancelar("Cambio de planes")))

    resultados.append(_ejecutar(12, "Calcular costo con descuento inválido", lambda: sala.calcular_costo(
        horas=2, descuento=1.5, capacidad=8
    )))

    resultados.append(_ejecutar(13, "Calcular asesoría sin parámetro obligatorio", lambda: asesoria.calcular_costo(horas=2)))

    resultados.append(_ejecutar(14, "Calcular con duración no numérica", lambda: sala.calcular_costo(
        horas="dos", capacidad=8
    )))

    resultados.append(_ejecutar(15, "Registrar cliente con correo inválido", lambda: clientes.agregar(
        Cliente("Laura Díaz", "CC3003", "laura-sin-arroba", "3001112277")
    ).resumen()))

    resultados.append(_ejecutar(16, "Registrar alquiler de equipos", lambda: servicios.agregar(
        AlquilerEquipos("Portátiles", 25000, 6)
    ).describir()))

    resultados.append(_ejecutar(17, "Registrar sala con capacidad no numérica", lambda: servicios.agregar(
        ReservaSala("Sala Rota", 90000, "veinte")
    ).describir()))

    def reserva_de_equipos():
        equipo = servicios.buscar("Portátiles")
        reserva = reservas.crear(cliente, equipo, 4, {"cantidad": 2})
        reservas.confirmar(reserva.id)
        reservas.procesar(reserva.id)
        return reserva.resumen()

    resultados.append(_ejecutar(18, "Crear, confirmar y procesar alquiler de equipos", reserva_de_equipos))

    def reserva_cancelada():
        reserva = reservas.crear(cliente, asesoria, 2, {"nivel": "avanzado"})
        reservas.confirmar(reserva.id)
        reservas.cancelar(reserva.id, "El especialista no está disponible")
        return reserva.resumen()

    resultados.append(_ejecutar(19, "Confirmar y cancelar una asesoría", reserva_cancelada))

    def procesar_sin_confirmar():
        reserva = reservas.crear(cliente, asesoria, 1, {"nivel": "basica"})
        return reservas.procesar(reserva.id)

    resultados.append(_ejecutar(20, "Procesar una reserva sin confirmarla", procesar_sin_confirmar))

    resultados.append(_ejecutar(21, "Crear reserva sin cliente", lambda: reservas.crear(
        None, sala, 1, {"capacidad": 2}
    ).resumen()))

    resultados.append(_ejecutar(22, "Calcular costo con impuestos y descuento (sobrecarga)", lambda: (
        f"{sala.calcular_costo(2, 0.19, 0.10, capacidad=8):,.2f} "
        f"(posicional) | {sala.calcular_costo(horas=2, impuestos=0.19, descuento=0.10, capacidad=8):,.2f} "
        f"(nombrado) | {sala.calcular_costo_con_impuestos(2, 0.19, capacidad=8):,.2f} (solo impuestos)"
    )))

    exitosas = sum(1 for item in resultados if item["estado"] == "OK")
    print("\n" + "=" * 78)
    print(f"RESUMEN: {len(resultados)} operaciones | {exitosas} exitosas | "
          f"{len(resultados) - exitosas} fallidas controladas")
    print(f"FACTURACION TOTAL: ${reservas.facturado_total():,.2f}")
    print(f"ESTADO FINAL DEL SISTEMA: activo ({len(reservas.todas())} reservas en memoria)")
    print("=" * 78)
    registro.evento(
        "Fin de la simulación",
        operaciones=len(resultados),
        exitosas=exitosas,
        facturado=reservas.facturado_total(),
    )
    return resultados


if __name__ == "__main__":
    ejecutar_demo()
