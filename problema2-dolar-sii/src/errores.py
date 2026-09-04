"""
errores.py
----------
Definiciones de error (seccion 5) y preguntas A1-A5 del enunciado, todo
vectorizado con numpy sobre la serie completa del dolar observado.
"""

import os
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from cargar_datos import cargar_datos, precio_por
from punto_flotante import redondear_cifras_sig, error_representacion, CIFRAS_SIGNIFICATIVAS

CARPETA_GRAFICOS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "graficos"
)
CARPETA_DATA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)
MONTO_TRABAJO = 1_000_000.0


# ---------------------------------------------------------------------------
# Seccion 5: definiciones basicas de error (vectorizadas)
# ---------------------------------------------------------------------------
def error_absoluto(v_real, v_aprox):
    return np.abs(np.asarray(v_real, dtype=np.float64) - np.asarray(v_aprox, dtype=np.float64))


def error_relativo(v_real, v_aprox):
    v_real = np.asarray(v_real, dtype=np.float64)
    return (error_absoluto(v_real, v_aprox) / np.abs(v_real)) * 100.0


def propagar_mult_div(er_a, er_b):
    """En multiplicacion/division se suman los errores relativos (%)."""
    return np.abs(er_a) + np.abs(er_b)


def propagar_suma_resta(ea_a, ea_b):
    """En suma/resta se suman los errores absolutos."""
    return np.abs(ea_a) + np.abs(ea_b)


# ---------------------------------------------------------------------------
# A1. Error de representacion mes a mes
# ---------------------------------------------------------------------------
def analisis_a1(precios, etiquetas, guardar_grafico=True):
    aproximados, ea, er_pct = error_representacion(precios, cifras=CIFRAS_SIGNIFICATIVAS)

    idx_max = int(np.argmax(er_pct))
    print("A1. Error de representacion mes a mes (2 cifras significativas)")
    print(f"  Mes con mayor error relativo: {etiquetas[idx_max]} "
          f"(precio={precios[idx_max]}, aprox={aproximados[idx_max]}, "
          f"Ea={ea[idx_max]:.4f}, Er={er_pct[idx_max]:.4f}%)")

    if guardar_grafico:
        os.makedirs(CARPETA_GRAFICOS, exist_ok=True)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(etiquetas, er_pct, color="steelblue")
        ax.set_title("Error relativo por mes al redondear a 2 cifras significativas")
        ax.set_ylabel("Error relativo (%)")
        ax.set_xticks(etiquetas[::4])
        ax.tick_params(axis="x", rotation=90)
        fig.tight_layout()
        ruta = os.path.join(CARPETA_GRAFICOS, "03_error_representacion.png")
        fig.savefig(ruta, dpi=150)
        plt.close(fig)
        print(f"  Grafico guardado en: {ruta}")

    return aproximados, ea, er_pct, idx_max


# ---------------------------------------------------------------------------
# A2. Evaluacion entre dos puntos (una compra-venta)
# ---------------------------------------------------------------------------
def evaluar_compra_venta(p_compra_real, p_venta_real, monto=MONTO_TRABAJO,
                          cifras=CIFRAS_SIGNIFICATIVAS):
    """
    Aplica redondeo a p_compra y p_venta, calcula USD, pesos_final y
    Ganancia, y propaga el error: suma los relativos de compra+venta,
    los pasa a absoluto sobre la ganancia y entrega ganancia +/- error.
    """
    p_compra, ea_compra, er_compra = error_representacion(p_compra_real, cifras)
    p_venta, ea_venta, er_venta = error_representacion(p_venta_real, cifras)

    usd = monto / p_compra
    pesos_final = usd * p_venta
    ganancia = pesos_final - monto

    er_operacion = propagar_mult_div(er_compra, er_venta)  # % combinado
    ea_ganancia = np.abs(pesos_final) * (er_operacion / 100.0)
    er_ganancia_pct = (ea_ganancia / np.abs(ganancia)) * 100.0 if ganancia != 0 else np.inf

    return {
        "p_compra_aprox": float(p_compra), "p_venta_aprox": float(p_venta),
        "usd": float(usd), "pesos_final": float(pesos_final),
        "ganancia": float(ganancia), "ea_ganancia": float(ea_ganancia),
        "er_ganancia_pct": float(er_ganancia_pct),
    }


def analisis_a2(anios, meses_num, precios):
    idx_min, idx_max = int(np.argmin(precios)), int(np.argmax(precios))
    p_compra, p_venta = precios[idx_min], precios[idx_max]

    resultado = evaluar_compra_venta(p_compra, p_venta)
    print("\nA2. Evaluacion entre dos puntos (compra en el minimo, venta en el maximo)")
    print(f"  P_compra~{resultado['p_compra_aprox']}, P_venta~{resultado['p_venta_aprox']}")
    print(f"  USD comprados: {resultado['usd']:.4f}")
    print(f"  Ganancia = {resultado['ganancia']:.2f} +/- {resultado['ea_ganancia']:.2f} CLP "
          f"({resultado['er_ganancia_pct']:.4f}%)")
    return resultado


# ---------------------------------------------------------------------------
# A3. Cancelacion (dos meses casi iguales): dic-2022 vs dic-2023
# ---------------------------------------------------------------------------
def analisis_a3(anios, meses_num, precios):
    p_dic2022 = precio_por(anios, meses_num, precios, 2022, 12)
    p_dic2023 = precio_por(anios, meses_num, precios, 2023, 12)

    aprox2022, ea2022, _ = error_representacion(p_dic2022, cifras=3)
    aprox2023, ea2023, _ = error_representacion(p_dic2023, cifras=3)

    delta_p = aprox2023 - aprox2022
    ea_delta = propagar_suma_resta(ea2022, ea2023)
    er_delta_pct = (ea_delta / abs(delta_p)) * 100.0 if delta_p != 0 else np.inf

    afirmable = abs(delta_p) > ea_delta

    print("\nA3. Cancelacion: diciembre 2022 vs diciembre 2023 (3 cifras significativas)")
    print(f"  P_dic2022~{aprox2022} (Ea={ea2022:.4f}), P_dic2023~{aprox2023} (Ea={ea2023:.4f})")
    print(f"  DeltaP = {delta_p:.4f} +/- {ea_delta:.4f} ({er_delta_pct:.2f}%)")
    print(f"  ¿Se puede afirmar con seguridad la direccion del cambio? "
          f"{'SI' if afirmable else 'NO, el error domina la variacion (cancelacion)'}")

    return {
        "delta_p": float(delta_p), "ea_delta": float(ea_delta),
        "er_delta_pct": float(er_delta_pct), "afirmable": bool(afirmable),
    }


# ---------------------------------------------------------------------------
# A4 (soporte): variacion mes a mes de toda la serie, para el grafico 2
# ---------------------------------------------------------------------------
def variaciones_mes_a_mes(precios, etiquetas, cifras=CIFRAS_SIGNIFICATIVAS, guardar_grafico=True):
    aprox, ea, _ = error_representacion(precios, cifras)
    delta_p = np.diff(aprox)
    ea_delta = ea[1:] + ea[:-1]
    etiquetas_delta = etiquetas[1:]

    if guardar_grafico:
        os.makedirs(CARPETA_GRAFICOS, exist_ok=True)
        fig, ax = plt.subplots(figsize=(11, 4.5))
        colores = ["crimson" if abs(dp) < e else "steelblue" for dp, e in zip(delta_p, ea_delta)]
        ax.bar(etiquetas_delta, delta_p, yerr=ea_delta, color=colores, capsize=2)
        ax.axhline(0, color="gray", linewidth=0.8)
        ax.set_title("Variacion mes a mes (rojo = dominada por el error, cancelacion)")
        ax.set_ylabel("Delta P (CLP)")
        ax.set_xticks(etiquetas_delta[::4])
        ax.tick_params(axis="x", rotation=90)
        fig.tight_layout()
        ruta = os.path.join(CARPETA_GRAFICOS, "02_variacion_mes_a_mes.png")
        fig.savefig(ruta, dpi=150)
        plt.close(fig)
        print(f"  Grafico guardado en: {ruta}")

    return delta_p, ea_delta, etiquetas_delta


# ---------------------------------------------------------------------------
# A5. Mejor compra y mejor venta
# ---------------------------------------------------------------------------
def analisis_a5(precios, etiquetas, guardar_grafico=True):
    idx_min, idx_max = int(np.argmin(precios)), int(np.argmax(precios))
    p_min, p_max = precios[idx_min], precios[idx_max]

    resultado = evaluar_compra_venta(p_min, p_max)
    rentabilidad = (resultado["ganancia"] / MONTO_TRABAJO) * 100.0
    er_rentabilidad = resultado["er_ganancia_pct"]  # division por constante no agrega error

    print("\nA5. Mejor compra y mejor venta (minimo y maximo del periodo)")
    print(f"  Mes mas barato: {etiquetas[idx_min]} ({p_min}); "
          f"mes mas caro: {etiquetas[idx_max]} ({p_max})")
    print(f"  Rentabilidad = {rentabilidad:.4f}% +/- {er_rentabilidad:.4f}%")
    diferencia_vs_error = rentabilidad != 0 and abs(rentabilidad) > er_rentabilidad
    print(f"  ¿La conclusion sobrevive al error? "
          f"{'SI, la diferencia domina al error' if diferencia_vs_error else 'Queda en duda'}")

    # Rentabilidad de comprar en el minimo y vender en cada mes posterior
    aprox, _, _ = error_representacion(precios, CIFRAS_SIGNIFICATIVAS)
    er_compra_fija = error_representacion(p_min, CIFRAS_SIGNIFICATIVAS)[2]
    _, _, er_todos = error_representacion(precios, CIFRAS_SIGNIFICATIVAS)

    rentabilidades = np.full(precios.shape[0], np.nan)
    errores_rentabilidad = np.full(precios.shape[0], np.nan)
    for i in range(idx_min + 1, precios.shape[0]):
        r = evaluar_compra_venta(p_min, precios[i])
        rentabilidades[i] = (r["ganancia"] / MONTO_TRABAJO) * 100.0
        errores_rentabilidad[i] = r["er_ganancia_pct"]

    if guardar_grafico:
        os.makedirs(CARPETA_GRAFICOS, exist_ok=True)
        validos = ~np.isnan(rentabilidades)
        fig, ax = plt.subplots(figsize=(11, 4.5))
        ax.bar(
            etiquetas[validos], rentabilidades[validos],
            yerr=errores_rentabilidad[validos], color="seagreen", capsize=2,
        )
        ax.axhline(0, color="gray", linewidth=0.8)
        ax.set_title(f"Rentabilidad de comprar en el minimo ({etiquetas[idx_min]}) "
                     "y vender en cada mes posterior")
        ax.set_ylabel("Rentabilidad (%)")
        ax.set_xticks(etiquetas[validos][::3])
        ax.tick_params(axis="x", rotation=90)
        fig.tight_layout()
        ruta = os.path.join(CARPETA_GRAFICOS, "04_rentabilidad_minimo.png")
        fig.savefig(ruta, dpi=150)
        plt.close(fig)
        print(f"  Grafico guardado en: {ruta}")

    return {
        "idx_min": idx_min, "idx_max": idx_max,
        "rentabilidad_pct": rentabilidad, "er_rentabilidad_pct": er_rentabilidad,
        "diferencia_vs_error": diferencia_vs_error,
    }


# ---------------------------------------------------------------------------
# Exportacion de la tabla de evaluacion de error
# ---------------------------------------------------------------------------
def exportar_tabla_errores(anios, meses_num, etiquetas, ea, er_pct, resultado_a3,
                            tabla_anual=None, ruta_salida=None):
    if ruta_salida is None:
        ruta_salida = os.path.join(CARPETA_DATA, "tabla_errores.csv")

    with open(ruta_salida, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["tipo", "referencia", "error_absoluto", "error_relativo_pct",
                            "error_propagado"])

        for i in range(len(etiquetas)):
            escritor.writerow(["representacion", etiquetas[i], f"{ea[i]:.6f}",
                                f"{er_pct[i]:.6f}", ""])

        escritor.writerow(["cancelacion_A3", "dic2022_vs_dic2023", "",
                            f"{resultado_a3['er_delta_pct']:.6f}",
                            f"{resultado_a3['ea_delta']:.6f}"])

        if tabla_anual is not None:
            for fila in tabla_anual:
                escritor.writerow(["anualidad_A4", fila["anio"], f"{fila['ea']:.6f}",
                                    f"{fila['er_pct']:.6f}", f"{fila['ea']:.6f}"])

    print(f"\nTabla de evaluacion de error exportada a: {ruta_salida}")
    return ruta_salida


if __name__ == "__main__":
    from anualidad import variacion_anual

    anios, meses_nombre, meses_num, precios, etiquetas = cargar_datos()

    aproximados, ea, er_pct, idx_max = analisis_a1(precios, etiquetas)
    resultado_a2 = analisis_a2(anios, meses_num, precios)
    resultado_a3 = analisis_a3(anios, meses_num, precios)
    variaciones_mes_a_mes(precios, etiquetas)
    resultado_a5 = analisis_a5(precios, etiquetas)
    tabla_anual = variacion_anual(anios, meses_num, precios)

    exportar_tabla_errores(anios, meses_num, etiquetas, ea, er_pct, resultado_a3,
                            tabla_anual=tabla_anual)
