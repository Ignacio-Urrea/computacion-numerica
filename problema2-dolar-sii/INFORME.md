# INFORME — La ganancia que se evapora

Cancelación y propagación del error con el dólar observado del SII (2022–2025)
Universidad Católica del Maule — Laboratorio evaluado 1

## 1. Metodología

**Norma de punto flotante** (sección 4 del enunciado): cada precio se aproxima a
**2 cifras significativas totales** en base decimal (la "mantisa corta"), salvo en A3 y A4
donde el enunciado exige explícitamente **3 cifras significativas**. Ejemplo de la norma:
963.44 → 960 (Ea=3.44); 1000.76 → 1000 (Ea=0.76). Implementado en `src/punto_flotante.py`
mediante `redondear_cifras_sig`, vectorizado con numpy.

**Fórmulas de error** (sección 5), implementadas en `src/errores.py`:

- Error absoluto: `Ea = |valor_verdadero − valor_aproximado|`
- Error relativo (%): `Er = (Ea / valor_verdadero) × 100`
- Propagación en multiplicación/división: se **suman los errores relativos**.
- Propagación en suma/resta: se **suman los errores absolutos**.

**Monto de trabajo**: M = 1.000.000 CLP, según sección 4.

## 2. Resultados — Preguntas del error (A1–A5)

### A1. Error de representación mes a mes

Redondeando toda la serie (48 meses) a 2 cifras significativas y calculando Ea/Er por mes
(`errores.analisis_a1`, gráfico `graficos/03_error_representacion.png`):

- El mes con **mayor error relativo** fue **Abril 2022**: 815.12 → 820 (Ea=4.88, Er=0.60%).
- La mayoría de los meses quedan por debajo de 0.6% de error relativo, ya que 2 cifras
  significativas sobre valores de ~800–1000 dejan un "escalón" de redondeo de 10 unidades.

### A2. Evaluación entre dos puntos (una compra-venta)

Caso ilustrativo: comprar en el mes más barato del período (Feb-2023, P≈800 tras redondeo)
y vender en el mes más caro (Ene-2025, P≈1000 tras redondeo), con M=1.000.000:

- USD comprados = 1.000.000 / 800 = 1250.00
- pesos_final = 1250 × 1000 = 1.250.000
- Ganancia = 250.000 CLP
- Propagando: Er_compra + Er_venta → Ea de la ganancia = **3.673,95 CLP**
- **Ganancia = 250.000 ± 3.674 CLP (1.47%)**

La ganancia domina ampliamente al error propagado: es una conclusión sólida.

### A3. Cancelación (dos meses casi iguales)

Diciembre 2022 (875.66) vs diciembre 2023 (874.67), con 3 cifras significativas:

- P_dic2022 ≈ 876 (Ea=0.34); P_dic2023 ≈ 875 (Ea=0.33)
- ΔP = 875 − 876 = **-1.00 CLP**
- Error propagado (suma de absolutos) = **0.67 CLP** → Er% = **67.00%**
- **ΔP = -1.00 ± 0.67 CLP**

Con ese margen, el error relativo (67%) es enormemente alto — típico de una resta de dos
números grandes y casi iguales. Aun así, en magnitud absoluta |ΔP|=1.00 > Ea=0.67, así que
al límite sí se puede decir que el dólar bajó entre esos dos diciembres, pero con una
confianza muy baja: un margen de error apenas dos tercios de la magnitud del cambio
es un caso límite de cancelación, no una afirmación robusta.

### A4. Anualidad (variación enero→diciembre)

Para cada año, `ΔP = Precio_diciembre − Precio_enero` con error propagado
(`src/anualidad.py::variacion_anual`), ordenado de más a menos confiable:

| Año  | ΔP (CLP) | Error propagado | Error relativo |
|------|----------|------------------|-----------------|
| 2025 | -80.00   | ±4.60            | 5.75%           |
| 2024 | 70.00    | ±4.31            | 6.16%           |
| 2022 | 60.00    | ±6.39            | 10.65%          |
| 2023 | 40.00    | ±8.33            | **20.82%**      |

**2023 es el año menos confiable.** Lo que comparten los años poco confiables es una
variación anual (ΔP) pequeña en magnitud absoluta frente al tamaño del error propagado:
a menor |ΔP|, el mismo error absoluto se traduce en un error relativo mucho mayor.

### A5. Mejor compra y mejor venta

Sobre toda la serie 2022–2025:

- Mes más barato: **Febrero 2023** (798.26)
- Mes más caro: **Enero 2025** (1000.76)
- Rentabilidad de comprar en el mínimo y vender en el máximo: **25.00% ± 1.47%**
  (gráfico `graficos/04_rentabilidad_minimo.png`)

La diferencia (25%) es mucho mayor que la incertidumbre (1.47 puntos porcentuales): la
conclusión **sobrevive al error** con amplio margen.

## 3. Resultados — Preguntas del punto flotante (B1, B2, B4)

### B1. Cifras significativas = mantisa corta

Tomar un precio con 2 cifras significativas es análogo a guardarlo con una mantisa de
pocos bits: solo se conservan los dígitos más representativos del número y se reescala el
resto mediante un exponente (potencia de 10), exactamente como una mantisa binaria corta
en punto flotante. Cuantas menos cifras/bits de mantisa, más grueso es el "escalón" entre
valores representables y mayor el error de redondeo fijo que se introduce.

Ejemplo pedido: **1000.76** dejando 3 cifras significativas → **1000.0** (Ea=0.76, Er=0.0759%).

### B2. La ida y vuelta que no vuelve

Ciclo `USD = Monto / Precio`, `pesos_final = USD × Precio`, aplicado a los 48 meses de la
serie con Monto=1.000.000 (`src/punto_flotante.py::demo_b2`, gráfico
`graficos/05_deriva_ida_vuelta.png`):

- Deriva máxima absoluta observada: **1.16 × 10⁻¹⁰ CLP**
- Deriva promedio: **-4.85 × 10⁻¹² CLP**

La deriva es del orden del épsilon de máquina de float64 (~10⁻¹⁶ relativo) y no sigue un
patrón propio en el tiempo — es ruido de redondeo puro, sin relación con la curva de
precios que forma la serie del dólar.

### B4. Cancelación en la máquina

Calculando 874.67 − 875.66 explícitamente en cada precisión:

- float64: `-0.9900000000000091`
- float32: `-0.98999023`

Ambos operandos tienen ~875 de magnitud; el resultado tiene magnitud ~1, es decir se
pierden **~3 órdenes de magnitud** de significancia por cancelación catastrófica. En
float64 quedan del orden de 12 cifras significativas "reales" válidas y en float32
apenas ~4. Esto conecta directamente con **A3**: la misma resta (dic-2023 − dic-2022)
es la que, al redondear a 2-3 cifras significativas de entrada, produce un error
relativo de 67% — la máquina y el redondeo manual sufren el mismo fenómeno de fondo.

## 4. Conclusión final

1. **¿Cuándo conviene comprar?** El dólar estuvo más barato en **Febrero 2023** (798.26).
   Comparado con los meses vecinos (Enero 2023: 826.34, Marzo 2023: 809.50), la diferencia
   frente a marzo es de solo ~11 CLP, un valor que compite con el error de representación
   a 2 cifras (~4-5 CLP); frente a enero la diferencia (~28 CLP) sí es clara. El mínimo es
   confiable frente al conjunto del período, pero su ventaja sobre el mes inmediatamente
   posterior (marzo) es más ajustada.

2. **¿Cuándo conviene vender?** El dólar estuvo más caro en **Enero 2025** (1000.76).
   Frente a diciembre 2024 (982.30, diferencia ~18 CLP) y febrero 2025 (956.62, diferencia
   ~44 CLP), la diferencia supera holgadamente el error de representación (~4-10 CLP): el
   máximo es un pico claro y confiable, no un artefacto del redondeo.

3. **La mejor jugada completa:** comprar en Febrero 2023 y vender en Enero 2025 rinde una
   **rentabilidad de 25.00% ± 1.47%** sobre M=1.000.000 CLP (ganancia de 250.000 ± 3.674 CLP).
   Es una recomendación **sólida**: la magnitud de la ganancia es más de 15 veces el error
   propagado.

4. **Tramos donde NO se puede recomendar nada con seguridad:** la variación entre
   **diciembre 2022 y diciembre 2023** (A3) es un ejemplo directo — ΔP = -1.00 ± 0.67 CLP,
   un error relativo de 67%. Del mismo modo, la variación anual de **2023** (ΔP=40 ± 8.33,
   Er=20.82%, A4) es la menos confiable del período: cualquier afirmación tajante sobre
   "cuánto" subió o bajó el dólar en esos tramos sería irresponsable, aunque el signo de la
   dirección apenas sobreviva al margen de error.

5. **La lección de método:** cuando una "diferencia" surge de restar dos números grandes y
   parecidos, el resultado hereda todo el error absoluto de ambos operandos pero pierde la
   magnitud que lo hacía relevante — por eso el error relativo se dispara y una cifra que
   parece pequeña y precisa en realidad puede estar completamente dominada por la
   incertidumbre de origen; conviene siempre comparar la diferencia contra su error
   propagado, nunca contra su valor aparente.

La conclusión anterior se apoya íntegramente en los valores y errores calculados por
`src/errores.py` y `src/anualidad.py` (ver `data/tabla_errores.csv` y los gráficos en
`graficos/`), no en apreciaciones intuitivas sobre la serie.
