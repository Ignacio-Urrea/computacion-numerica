"""
anualidad.py
------------
Variacion enero->diciembre para cada anio (pregunta A4), con propagacion de
error, y grafico de la serie mensual completa (grafico 1).
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from cargar_datos import cargar_datos, precio_por
from punto_flotante import error_representacion, CIFRAS_SIGNIFICATIVAS
from errores import propagar_suma_resta

CARPETA_GRAFICOS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "graficos"
)


def variacion_anual(anios, meses_num, precios, cifras=CIFRAS_SIGNIFICATIVAS):
    """
    Para cada anio presente en los datos calcula:
        delta_p = Precio_diciembre - Precio_enero
        ea      = error absoluto propagado (suma de Ea de enero y diciembre)
        er_pct  = error relativo (%) de delta_p
    Devuelve una lista de dicts ordenada de mas a menos confiable (menor er_pct).
    """
    anios_unicos = sorted(set(anios.tolist()))
    filas = []

    for anio in anios_unicos:
        p_ene = precio_por(anios, meses_num, precios, anio, 1)
        p_dic = precio_por(anios, meses_num, precios, anio, 12)

        aprox_ene, ea_ene, _ = error_representacion(p_ene, cifras)
        aprox_dic, ea_dic, _ = error_representacion(p_dic, cifras)

        delta_p = float(aprox_dic - aprox_ene)
        ea = float(propagar_suma_resta(ea_ene, ea_dic))
        er_pct = (abs(ea / delta_p) * 100.0) if delta_p != 0 else float("inf")

        filas.append({
            "anio": anio, "p_enero_aprox": float(aprox_ene),
            "p_diciembre_aprox": float(aprox_dic),
            "delta_p": delta_p, "ea": ea, "er_pct": er_pct,
        })

    filas.sort(key=lambda f: f["er_pct"])
    return filas


def graficar_serie_mensual(etiquetas, precios, guardar=True):
    os.makedirs(CARPETA_GRAFICOS, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(etiquetas, precios, color="darkorange", linewidth=1.5)
    ax.set_title("Dolar observado (promedio mensual) 2022-2025")
    ax.set_ylabel("CLP por USD")
    ax.set_xticks(etiquetas[::4])
    ax.tick_params(axis="x", rotation=90)
    fig.tight_layout()
    if guardar:
        ruta = os.path.join(CARPETA_GRAFICOS, "01_serie_mensual.png")
        fig.savefig(ruta, dpi=150)
        print(f"Grafico guardado en: {ruta}")
    plt.close(fig)


if __name__ == "__main__":
    anios, meses_nombre, meses_num, precios, etiquetas = cargar_datos()

    graficar_serie_mensual(etiquetas, precios)

    tabla = variacion_anual(anios, meses_num, precios)

    print("\nA4. Variacion anual enero->diciembre (ordenado de mas a menos confiable)")
    for fila in tabla:
        print(f"  {fila['anio']}: DeltaP={fila['delta_p']:.4f} +/- {fila['ea']:.4f} "
              f"({fila['er_pct']:.2f}%)")

    menos_confiables = [f for f in tabla if f["er_pct"] > 20]
    if menos_confiables:
        anios_poco_confiables = ", ".join(str(f["anio"]) for f in menos_confiables)
        print(f"\n  Anios poco confiables (Er% > 20): {anios_poco_confiables}")
        print("  Tienen en comun una variacion anual (DeltaP) pequena en magnitud,")
        print("  cercana al tamano del error propagado, lo que dispara el error relativo.")
