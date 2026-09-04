import os
import numpy as np
import matplotlib.pyplot as plt

# creamos la carpeta para guardar los graficos
os.makedirs("graficos", exist_ok=True)

# ruta del archivo csv
ruta_csv = "data/dolar_observado_sii_2022_2025.csv"
if not os.path.exists(ruta_csv):
    ruta_csv = "dolar_observado_sii_2022_2025.csv"

# leemos la primera linea para saber si viene en formato tabla (12 filas) o largo (48 filas)
with open(ruta_csv, "r", encoding="utf-8") as f:
    encabezado = f.readline().strip().lower().split(",")

meses_nombres = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
anios_lista = ["22", "23", "24", "25"]

if len(encabezado) == 5 and "mes" in encabezado[0]:
    # caso tabla: 12 filas con columnas mes, 2022, 2023, 2024, 2025
    matriz = np.genfromtxt(ruta_csv, delimiter=",", skip_header=1, usecols=(1, 2, 3, 4))
    precios = []
    etiquetas = []
    for a_idx, a_txt in enumerate(anios_lista):
        for m_idx, m_txt in enumerate(meses_nombres):
            precios.append(matriz[m_idx, a_idx])
            etiquetas.append(f"{m_txt}-{a_txt}")
    precios = np.array(precios, dtype=float)
else:
    # caso formato largo: año, mes, mes_num, precio (48 filas)
    precios = np.genfromtxt(ruta_csv, delimiter=",", skip_header=1, usecols=3)
    datos_txt = np.genfromtxt(ruta_csv, delimiter=",", skip_header=1, usecols=(0, 1), dtype=str)
    etiquetas = [f"{m[:3].lower()}-{a[-2:]}" for a, m in datos_txt]

# funcion para redondear a n cifras significativas
def redondear_cifras(x, cifras=2):
    x = np.asarray(x, dtype=float)
    factor = np.floor(np.log10(np.abs(x)))
    escala = 10.0 ** (cifras - 1 - factor)
    return np.round(x * escala) / escala

# funcion para error absoluto y relativo
def calc_errores(real, aprox):
    ea = np.abs(real - aprox)
    er = (ea / real) * 100.0
    return ea, er

# -------------------------------------------------------------
# a1. error de redondeo mes a mes a 2 cifras
# -------------------------------------------------------------
precios_aprox2 = redondear_cifras(precios, cifras=2)
ea_mes, er_mes = calc_errores(precios, precios_aprox2)

idx_peor = int(np.argmax(er_mes))
print("\n--- a1. error de redondeo mes a mes (2 cifras) ---")
print(f"mes con mayor error relativo: {etiquetas[idx_peor]}")
print(f"precio real: {precios[idx_peor]:.2f} clp | redondeado: {precios_aprox2[idx_peor]:.2f} clp")
print(f"error absoluto: {ea_mes[idx_peor]:.2f} clp | error relativo: {er_mes[idx_peor]:.2f}%")

# -------------------------------------------------------------
# a2. compra y venta de 1.000.000 de pesos
# -------------------------------------------------------------
monto = 1000000.0
idx_c = int(np.argmin(precios))  # mes mas barato
idx_v = int(np.argmax(precios))  # mes mas caro

p_compra_ap = precios_aprox2[idx_c]
p_venta_ap = precios_aprox2[idx_v]

# division: usd = monto / precio_compra (se pasa el error de compra)
usd_ap = monto / p_compra_ap
er_usd = er_mes[idx_c]

# multiplicacion: pesos = usd * precio_venta (se suman errores relativos)
pesos_final_ap = usd_ap * p_venta_ap
er_pesos_final = er_usd + er_mes[idx_v]

# pasamos el error relativo a pesos (error absoluto)
ea_pesos_final = (er_pesos_final / 100.0) * pesos_final_ap

# resta: ganancia = pesos - monto (se conserva el error absoluto)
ganancia_ap = pesos_final_ap - monto
ea_ganancia = ea_pesos_final
er_ganancia = (ea_ganancia / ganancia_ap) * 100.0

print("\n--- a2. evaluacion compra y venta ---")
print(f"comprando en {etiquetas[idx_c]} ({p_compra_ap:.0f} clp) y vendiendo en {etiquetas[idx_v]} ({p_venta_ap:.0f} clp):")
print(f"ganancia estimada: ${ganancia_ap:,.2f} clp")
print(f"margen de error: +- ${ea_ganancia:,.2f} clp ({er_ganancia:.2f}%)")

# -------------------------------------------------------------
# a3. cancelacion dic 2022 vs dic 2023
# -------------------------------------------------------------
# diciembre 2022 es indice 11 y diciembre 2023 es indice 23
p_dic22 = precios[11]
p_dic23 = precios[23]

p_dic22_ap3 = redondear_cifras(p_dic22, cifras=3)
p_dic23_ap3 = redondear_cifras(p_dic23, cifras=3)

ea_d22 = abs(p_dic22 - p_dic22_ap3)
ea_d23 = abs(p_dic23 - p_dic23_ap3)

delta_real = p_dic23 - p_dic22
delta_ap3 = p_dic23_ap3 - p_dic22_ap3
ea_delta = ea_d22 + ea_d23

# protegemos por si delta_real da cero exacto
if abs(delta_real) > 1e-6:
    er_delta = (ea_delta / abs(delta_real)) * 100.0
else:
    er_delta = 0.0

print("\n--- a3. cancelacion dic 2022 vs dic 2023 (3 cifras) ---")
print(f"cambio real: {delta_real:.2f} clp")
print(f"cambio con redondeo: {delta_ap3:.2f} +- {ea_delta:.2f} clp")
print(f"error porcentual: {er_delta:.2f}%")
print("no se puede asegurar si subio o bajo porque el error es similar al cambio real")

# -------------------------------------------------------------
# a4. variacion enero a diciembre de cada año
# -------------------------------------------------------------
print("\n--- a4. variacion anual enero a diciembre ---")
anios = [2022, 2023, 2024, 2025]
anualidades = []

for i, anio in enumerate(anios):
    idx_ene = i * 12
    idx_dic = i * 12 + 11
    
    ene_r, dic_r = precios[idx_ene], precios[idx_dic]
    ene_ap = precios_aprox2[idx_ene]
    dic_ap = precios_aprox2[idx_dic]
    
    diff_real = dic_r - ene_r
    diff_ap = dic_ap - ene_ap
    
    ea_anual = ea_mes[idx_ene] + ea_mes[idx_dic]
    if abs(diff_real) > 1e-6:
        er_anual = (ea_anual / abs(diff_real)) * 100.0
    else:
        er_anual = np.inf
        
    anualidades.append((anio, diff_real, diff_ap, ea_anual, er_anual))

anualidades.sort(key=lambda x: x[4])

print("ranking de confiabilidad (menor a mayor error %):")
for anio, dr, da, ea_a, er_a in anualidades:
    print(f"anio {anio}: cambio real = {dr:+6.2f} clp | error propagado = {er_a:6.2f}%")
print("los años menos confiables tienen en comun variaciones muy chicas donde se cancelan los digitos")

# -------------------------------------------------------------
# a5. mejor compra y mejor venta de todo el periodo
# -------------------------------------------------------------
rentab_real = ((precios[idx_v] - precios[idx_c]) / precios[idx_c]) * 100.0
print("\n--- a5. mejor compra y mejor venta ---")
print(f"comprar en: {etiquetas[idx_c]} ({precios[idx_c]:.2f} clp)")
print(f"vender en:  {etiquetas[idx_v]} ({precios[idx_v]:.2f} clp)")
print(f"rentabilidad real: {rentab_real:.2f}%")
print("la conclusion si sobrevive al error porque la subida total supera por mucho la incertidumbre")

# -------------------------------------------------------------
# b4. cancelacion en maquina float32 vs float64
# -------------------------------------------------------------
diff64 = np.float64(874.67) - np.float64(875.66)
diff32 = np.float32(874.67) - np.float32(875.66)

print("\n--- b4. resta (float32 vs float64) ---")
print(f"resultado en float64: {diff64:.12f}")
print(f"resultado en float32: {diff32:.12f}")

# -------------------------------------------------------------
# guardamos la tabla csv de evaluacion de errores
# -------------------------------------------------------------
with open("evaluacion_errores.csv", "w", encoding="utf-8") as f:
    f.write("tipo,nombre,valor_real,valor_aprox,error_absoluto,error_relativo_porc\n")
    for i in range(len(precios)):
        f.write(f"mes,{etiquetas[i]},{precios[i]:.2f},{precios_aprox2[i]:.2f},{ea_mes[i]:.2f},{er_mes[i]:.2f}\n")
    for a, dr, da, ea_a, er_a in anualidades:
        f.write(f"anualidad,{a},{dr:.2f},{da:.2f},{ea_a:.2f},{er_a:.2f}\n")
print("\nse guardo evaluacion_errores.csv")

# -------------------------------------------------------------
# graficos
# -------------------------------------------------------------
print("guardando imagenes en graficos/...")

# 1. serie mensual
plt.figure(figsize=(10, 4))
plt.plot(etiquetas, precios, marker="o", color="tab:blue", linewidth=1.5)
plt.xticks(range(0, len(etiquetas), 4), rotation=45)
plt.title("1. serie mensual dolar observado (2022-2025)")
plt.ylabel("precio clp")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("graficos/1_serie_mensual.png")
plt.close()

# 2. variacion mes a mes
delta_mes = np.diff(precios)
plt.figure(figsize=(10, 4))
plt.bar(range(len(delta_mes)), delta_mes, color="orange")
plt.axhline(0, color="black", linewidth=0.8)
plt.xticks(range(0, len(delta_mes), 4), etiquetas[1::4], rotation=45)
plt.title("2. variacion mes a mes (delta p)")
plt.ylabel("delta p (clp)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("graficos/2_variacion_mes_a_mes.png")
plt.close()

# 3. error de redondeo
plt.figure(figsize=(10, 4))
plt.bar(range(len(ea_mes)), ea_mes, color="tab:red")
plt.xticks(range(0, len(ea_mes), 4), etiquetas[::4], rotation=45)
plt.title("3. error absoluto de redondeo por mes (2 cifras)")
plt.ylabel("error absoluto (clp)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("graficos/3_error_representacion.png")
plt.close()

# 4. rentabilidad desde el minimo
meses_post = list(range(idx_c + 1, len(precios)))
rentabilidades = [((precios[i] - precios[idx_c]) / precios[idx_c]) * 100.0 for i in meses_post]
errores_rentab = [er_mes[idx_c] + er_mes[i] for i in meses_post]

plt.figure(figsize=(10, 4))
plt.errorbar(range(len(meses_post)), rentabilidades, yerr=errores_rentab, fmt="-o", color="green", ecolor="red", capsize=3)
plt.xticks(range(0, len(meses_post), 3), [etiquetas[i] for i in meses_post[::3]], rotation=45)
plt.title(f"4. rentabilidad comprando en {etiquetas[idx_c]} con margen de error")
plt.ylabel("rentabilidad (%)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("graficos/4_rentabilidad_minimo.png")
plt.close()

# 5. deriva ida y vuelta
dolares = monto / precios
pesos_devuelta = dolares * precios
deriva = pesos_devuelta - monto

plt.figure(figsize=(10, 4))
plt.plot(etiquetas, deriva, marker="x", color="purple")
plt.xticks(range(0, len(etiquetas), 4), rotation=45)
plt.title("5. deriva de ida y vuelta (pesos a usd y vuelta a pesos)")
plt.ylabel("deriva (clp)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("graficos/5_deriva_ida_vuelta.png")
plt.close()

