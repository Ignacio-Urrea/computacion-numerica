# La ganancia que se evapora

Cancelación y propagación del error con el dólar observado del SII (2022–2025).
Laboratorio evaluado 1 — Análisis de error (cifras significativas, punto flotante,
error absoluto, relativo y propagación) — Universidad Católica del Maule.

## Contenido del repositorio

```
problema2-dolar-sii/
├── README.md              <- este archivo
├── INFORME.md             <- documento de entrega con la conclusión final
├── requirements.txt       <- numpy, matplotlib
├── data/
│   ├── dolar_observado_sii_2022_2025.csv   <- dataset original (SII, promedio mensual)
│   └── tabla_errores.csv                   <- tabla de evaluación de error (generada)
├── src/
│   ├── cargar_datos.py     <- carga el CSV con numpy (np.genfromtxt)
│   ├── punto_flotante.py   <- redondeo a cifras significativas, B1, B2, B4
│   ├── errores.py          <- error absoluto/relativo/propagado, A1-A5
│   └── anualidad.py        <- variación enero->diciembre por año, A4
└── graficos/                <- imágenes PNG generadas por los scripts
```

## Cómo ejecutar

```bash
pip install -r requirements.txt

cd src
python cargar_datos.py      # smoke test de carga de datos
python punto_flotante.py    # B1, B2, B4 (genera graficos/05_deriva_ida_vuelta.png)
python anualidad.py         # A4 (genera graficos/01_serie_mensual.png)
python errores.py           # A1, A2, A3, A5 (genera graficos 02, 03, 04 y data/tabla_errores.csv)
```

Norma de punto flotante usada en todo el laboratorio: 2 cifras significativas,
base decimal (ver `src/punto_flotante.py`), salvo en A3/A4 donde el enunciado pide
explícitamente 3 cifras significativas.

## Resultados clave (obtenidos al ejecutar los scripts)

- **A1** — Mayor error relativo al redondear a 2 cifras: Abril 2022 (815.12 -> 820,
  Ea=4.88, Er=0.60%).
- **A2** — Comprar en el mínimo (Feb-2023, ≈800) y vender en el máximo (Ene-2025, similar a 1000):
  Ganancia = 250.000 +- 3.674 CLP (1.47%).
- **A3** — Cancelación Dic-2022 vs Dic-2023: ΔP = -1.00 +- 0.67 (67.00%). El error relativo
  es enorme, pero |ΔP| = 1.00 sigue siendo mayor que el error propagado (0.67), por lo que —
  con el margen justo — sí se puede afirmar que el dólar bajó, aunque la certeza es baja.
- **A4** — Confiabilidad de la variación enero→diciembre por año (menor a mayor Er%):
  2025 (5.75%) > 2024 (6.16%) > 2022 (10.65%) > 2023 (20.82%, el menos confiable).
  El año menos confiable es el que tuvo la variación anual más chica en magnitud (ΔP=40)
  frente al error propagado.
- **A5** — Mes más barato: Feb-2023 (798.26); mes más caro: Ene-2025 (1000.76).
  Rentabilidad de comprar en el mínimo y vender en el máximo: 25.00% +- 1.47% — la
  diferencia domina claramente al error, conclusión sólida.
- **B4** — 874.67 − 875.66 en float64 = -0.9900000000000091; en float32 = -0.98999023.
  La resta de dos valores casi iguales pierde ~3 órdenes de magnitud de significancia
  (cancelación catastrófica), coherente con el resultado de A3.

Ver `INFORME.md` para el detalle completo, los gráficos y la conclusión argumentada final.
