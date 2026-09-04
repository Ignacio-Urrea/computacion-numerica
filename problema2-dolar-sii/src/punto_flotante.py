"""
punto_flotante.py
------------------
Normas de punto flotante para el laboratorio (seccion 4 del enunciado) y
preguntas B1, B2, B4.

Norma acordada: version de 2 cifras significativas totales del valor
aproximado ("mantisa corta"), base decimal (10).
Ejemplo: 963.44 -> 960 (error 3.44); 1000.76 -> 1.00e3 = 1000 (error 0.76).
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from cargar_datos import cargar_datos

CIFRAS_SIGNIFICATIVAS = 2
CARPETA_GRAFICOS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "graficos"
)


def redondear_cifras_sig(valor, cifras=CIFRAS_SIGNIFICATIVAS):
    """
    Redondea (vectorizado) un valor o arreglo a `cifras` cifras significativas
    en base 10. Equivalente a truncar la mantisa a `cifras` digitos.
    """
    valor = np.asarray(valor, dtype=np.float64)
    with np.errstate(divide="ignore"):
        orden = np.floor(np.log10(np.abs(valor)))
    factor = 10.0 ** (cifras - 1 - orden)
    return np.round(valor * factor) / factor


def error_representacion(valor_real, cifras=CIFRAS_SIGNIFICATIVAS):
    """
    Devuelve (aproximado, error_absoluto, error_relativo_pct) al redondear
    valor_real a `cifras` cifras significativas.
    """
    valor_real = np.asarray(valor_real, dtype=np.float64)
    aproximado = redondear_cifras_sig(valor_real, cifras)
    ea = np.abs(valor_real - aproximado)
    er_pct = (ea / np.abs(valor_real)) * 100.0
    return aproximado, ea, er_pct


# ---------------------------------------------------------------------------
# B1. Cifras significativas = mantisa corta
# ---------------------------------------------------------------------------
def demo_b1():
    """
    Muestra por que tomar un precio con 2 cifras significativas equivale a
    guardarlo con una mantisa de pocos bits: al igual que un float de la
    maquina, solo se conservan los primeros digitos representativos del
    numero (la mantisa) y se descarta el resto, introduciendo un error de
    redondeo fijo por el "tamano de paso" que deja esa cantidad de cifras.

    Ejemplo pedido: 1000.76 dejando 3 cifras significativas.
    """
    valor = 1000.76
    aprox3, ea3, er3 = error_representacion(valor, cifras=3)
    print("B1. Cifras significativas = mantisa corta")
    print(
        "  Con 2 cifras, un numero como 963.44 solo retiene sus 2 digitos"
        " mas significativos (9 y 6) y reescala el resto con un exponente,"
        " igual que una mantisa binaria corta en punto flotante: cuantas"
        " menos cifras/bits de mantisa, mas grueso es el 'escalon' entre"
        " valores representables y mayor el error de redondeo."
    )
    print(f"  1000.76 con 3 cifras -> {aprox3} (Ea={ea3:.4f}, Er={er3:.4f}%)")
    return aprox3, ea3, er3


# ---------------------------------------------------------------------------
# B2. La ida y vuelta que no vuelve
# ---------------------------------------------------------------------------
def ciclo_ida_vuelta(monto, precio):
    """
    USD = monto / precio ; pesos_final = USD * precio.
    En aritmetica exacta pesos_final == monto. En punto flotante puede
    haber una deriva minima por redondeo interno del float.
    """
    precio = np.asarray(precio, dtype=np.float64)
    usd = monto / precio
    pesos_final = usd * precio
    return pesos_final


def demo_b2(guardar_grafico=True):
    """
    Aplica el ciclo ida-y-vuelta a todos los precios de la serie y mide la
    deriva (monto - resultado) mes a mes. Genera el grafico 5.
    """
    _, _, _, precios, etiquetas = cargar_datos()
    monto = 1_000_000.0

    resultado = ciclo_ida_vuelta(monto, precios)
    deriva = monto - resultado

    print("\nB2. La ida y vuelta que no vuelve")
    print(f"  Deriva maxima absoluta: {np.max(np.abs(deriva)):.10e} CLP")
    print(f"  Deriva promedio: {np.mean(deriva):.10e} CLP")
    print(
        "  La deriva es del orden del epsilon de maquina de float64"
        " (~1e-16 relativo), no sigue un patron propio: es ruido de"
        " redondeo, muy distinto a la curva de precios en el tiempo."
    )

    if guardar_grafico:
        os.makedirs(CARPETA_GRAFICOS, exist_ok=True)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(etiquetas, deriva, marker="o", markersize=3, linewidth=1)
        ax.axhline(0, color="gray", linewidth=0.8)
        ax.set_title("Deriva de la ida y vuelta en punto flotante (float64)")
        ax.set_ylabel("Monto - resultado (CLP)")
        ax.set_xticks(etiquetas[::4])
        ax.tick_params(axis="x", rotation=90)
        fig.tight_layout()
        ruta = os.path.join(CARPETA_GRAFICOS, "05_deriva_ida_vuelta.png")
        fig.savefig(ruta, dpi=150)
        plt.close(fig)
        print(f"  Grafico guardado en: {ruta}")

    return deriva


# ---------------------------------------------------------------------------
# B4. Cancelacion en la maquina
# ---------------------------------------------------------------------------
def demo_b4():
    """
    Calcula 874.67 - 875.66 en float32 y float64, y compara cuantas cifras
    significativas validas quedan en cada caso (se conecta con A3).
    """
    a64 = np.float64(874.67)
    b64 = np.float64(875.66)
    r64 = a64 - b64

    a32 = np.float32(874.67)
    b32 = np.float32(875.66)
    r32 = a32 - b32

    print("\nB4. Cancelacion en la maquina")
    print(f"  float64: 874.67 - 875.66 = {r64!r}")
    print(f"  float32: 874.67 - 875.66 = {r32!r}")

    # Cifras significativas "validas": cada operando tiene ~15-16 (float64)
    # o ~7 (float32) cifras significativas de precision; al restar dos
    # numeros casi iguales (~875), el resultado (~-1) pierde ~3 ordenes de
    # magnitud de significancia por cancelacion catastrofica.
    cifras_entrada_64 = 15
    cifras_entrada_32 = 7
    orden_perdido = np.log10(np.abs(a64)) - np.log10(np.abs(r64))
    cifras_validas_64 = max(cifras_entrada_64 - orden_perdido, 0)
    cifras_validas_32 = max(cifras_entrada_32 - orden_perdido, 0)

    print(
        f"  Ordenes de magnitud perdidos por cancelacion: ~{orden_perdido:.2f}"
    )
    print(f"  Cifras significativas validas aprox. en float64: {cifras_validas_64:.1f}")
    print(f"  Cifras significativas validas aprox. en float32: {cifras_validas_32:.1f}")
    print(
        "  Aunque float64 imprime mas decimales que float32, ambos sufren"
        " el mismo problema de fondo: al restar dos valores casi iguales"
        " se cancelan las cifras altas y solo sobreviven unas pocas cifras"
        " significativas reales del resultado, igual que en A3."
    )

    return r64, r32


if __name__ == "__main__":
    demo_b1()
    demo_b2()
    demo_b4()
