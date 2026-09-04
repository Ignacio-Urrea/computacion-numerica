"""
cargar_datos.py
----------------
Carga el dataset del dolar observado (SII) usando numpy y expone utilidades
basicas para obtener arreglos de trabajo (anio, mes, mes_num, precio) y para
buscar un precio puntual por (anio, mes_num).
"""

import os
import numpy as np

RUTA_CSV_DEFECTO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "dolar_observado_sii_2022_2025.csv",
)

MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def cargar_datos(path=RUTA_CSV_DEFECTO):
    """
    Carga el CSV con np.genfromtxt y devuelve arreglos numpy:
        anios       -> int, shape (N,)
        meses_nombre-> str, shape (N,)
        meses_num   -> int, shape (N,)
        precios     -> float64, shape (N,)
        etiquetas   -> str "Mes-Año", shape (N,) (para graficos)
    """
    datos = np.genfromtxt(
        path,
        delimiter=",",
        skip_header=1,
        dtype=None,
        encoding="utf-8",
        names=["anio", "mes", "mes_num", "precio"],
    )

    anios = datos["anio"].astype(int)
    meses_nombre = datos["mes"].astype(str)
    meses_num = datos["mes_num"].astype(int)
    precios = datos["precio"].astype(np.float64)

    etiquetas = np.array(
        [f"{m[:3]}-{a}" for m, a in zip(meses_nombre, anios)]
    )

    return anios, meses_nombre, meses_num, precios, etiquetas


def precio_por(anios, meses_num, precios, anio, mes_num):
    """
    Busca el precio observado para un (anio, mes_num) especifico.
    Lanza ValueError si no se encuentra el registro.
    """
    mascara = (anios == anio) & (meses_num == mes_num)
    if not np.any(mascara):
        raise ValueError(f"No hay datos para {MESES_ES[mes_num - 1]} {anio}")
    return float(precios[mascara][0])


if __name__ == "__main__":
    anios, meses_nombre, meses_num, precios, etiquetas = cargar_datos()

    print(f"Registros cargados: {precios.shape[0]}")
    print("Primeros 3 registros:")
    for i in range(3):
        print(f"  {etiquetas[i]}: {precios[i]}")
    print("Ultimos 3 registros:")
    for i in range(-3, 0):
        print(f"  {etiquetas[i]}: {precios[i]}")

    ejemplo = precio_por(anios, meses_num, precios, 2024, 2)
    print(f"\nprecio_por(2024, Febrero) = {ejemplo}")
