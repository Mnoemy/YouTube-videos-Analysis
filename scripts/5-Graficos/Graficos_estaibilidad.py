# ESTABILIDAD DE LA MATRIZ PROMEDIO
# Figura de dos paneles: (a) correlación diaria con el promedio, (b) histograma del CV por par
# Además: split-half y tabla de los cinco pares principales

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PATH_RESULTADOS = Path("../../Resultados/analisisW")
PATH_GRAFICOS = Path("../../Resultados/GraficosAnalisisW")
PATH_GRAFICOS.mkdir(parents=True, exist_ok=True)


UMBRAL_CORR = 0.9   # umbral para reportar el % de días con alta correlación


# ---------------------------------------------------------------
# Carga y preparación
# ---------------------------------------------------------------
series = pd.read_parquet(PATH_RESULTADOS / "series_temporales.parquet")
peso_promedio_pares = pd.read_parquet(PATH_RESULTADOS / "peso_promedio_pares.parquet")


# La fecha debe quedar como índice y las columnas deben ser solo los pares
if "fecha" in series.columns:
    series["fecha"] = pd.to_datetime(series["fecha"])
    series = series.set_index("fecha")
series = series.sort_index()

top_5_pares = (
    peso_promedio_pares
    .sort_values(by="peso_promedio", ascending=False)
    .head(5)["pares"]
    .tolist()
)


promedio = series.mean()


# ---------------------------------------------------------------
# (a) Correlación diaria con el promedio
# ---------------------------------------------------------------
# Pearson entre el vector del día y el vector promedio (NaN si alguno es constante)
corr_diaria = series.apply(lambda fila: fila.corr(promedio), axis=1)

# ---------------------------------------------------------------
# (b) Coeficiente de variación (CV) por par
# ---------------------------------------------------------------
desv = series.std()
cv = (desv / promedio.replace(0, np.nan)).dropna()

# ---------------------------------------------------------------
# Figura de dos paneles
# ---------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Panel (a)
ax1.plot(corr_diaria.index, corr_diaria, linewidth=0.0, marker="o", markersize=1.5)
#ax1.axhline(UMBRAL_CORR, color="gray", linestyle="--", linewidth=0.8)
ax1.set_xlabel("Fecha")
ax1.set_ylabel("Correlación con la matriz promedio")
ax1.set_title("(a) Correlación diaria con el promedio", loc="left", fontsize=10)
ax1.grid(axis="y", alpha=0.2)
for etiqueta in ax1.get_xticklabels():
    etiqueta.set_rotation(30)
    etiqueta.set_ha("right")

# Panel (b)
ax2.hist(cv, bins=10, edgecolor="white")
ax2.axvline(cv.median(), color="black", linestyle="--", linewidth=1,
           label=f"Mediana = {cv.median():.2f}")
ax2.set_xlabel("Coeficiente de variación (desv. est. / media)")
ax2.set_ylabel("Número de pares")
ax2.set_title("(b) Variabilidad temporal por par", loc="left", fontsize=10)
ax2.legend(frameon=False)
ax2.grid(axis="y", alpha=0.2)

plt.tight_layout()
plt.savefig(PATH_GRAFICOS / "02_estabilidad_dos_panelesv2.pdf")
plt.savefig(PATH_GRAFICOS / "02_estabilidad_dos_panelesv2.png", dpi=300)
plt.show()





# ---------------------------------------------------------------
# Resumen de la correlación diaria (para el texto)
# ---------------------------------------------------------------
c = corr_diaria.dropna()
print("--- Correlación diaria con el promedio ---")
print(f"Días con correlación definida: {len(c)} de {len(corr_diaria)}")
print(f"Media: {c.mean():.3f} | Mediana: {c.median():.3f} | Mínimo: {c.min():.3f}")
print(f"Días con r > {UMBRAL_CORR}: {(c > UMBRAL_CORR).mean() * 100:.1f} %")

# ---------------------------------------------------------------
# Resumen del CV (para el texto)
# ---------------------------------------------------------------
print("\n--- Coeficiente de variación por par ---")
print(f"Mediana: {cv.median():.3f} | Máximo: {cv.max():.3f} ({cv.idxmax()})")
print("Pares con CV más alto:")
print(cv.sort_values(ascending=False).head(5).round(3).to_string())


# ---------------------------------------------------------------
# Split-half: primera mitad vs segunda mitad del período
# ---------------------------------------------------------------
mitad = len(series) // 2
m1 = series.iloc[:mitad].mean()
m2 = series.iloc[mitad:].mean()

r_pearson = np.corrcoef(m1, m2)[0, 1]
r_spearman = m1.corr(m2, method="spearman")
# Diferencia relativa de nivel, usando el promedio global como referencia
error_relativo = ((m1 - m2).abs() / promedio.replace(0, np.nan)).mean()

print("\n--- Split-half ---")
print(f"Primera mitad: {series.index[0].date()} a {series.index[mitad - 1].date()}")
print(f"Segunda mitad: {series.index[mitad].date()} a {series.index[-1].date()}")
print(f"Pearson r = {r_pearson:.3f} | Spearman rho = {r_spearman:.3f}")
print(f"Error relativo medio entre mitades = {error_relativo * 100:.1f} %")

# ---------------------------------------------------------------
# Tabla de los cinco pares principales
# ---------------------------------------------------------------
tabla = pd.DataFrame({
    "Peso medio": promedio[top_5_pares],
    "Desv. est.": desv[top_5_pares],
    "CV": cv.reindex(top_5_pares),
    "Mínimo": series[top_5_pares].min(),
    "Máximo": series[top_5_pares].max(),
}).round(4)
tabla.index.name = "Par"

print("\n--- Cinco pares con mayor peso promedio ---")
print(tabla.to_string())

#tabla.to_csv(PATH_RESULTADOS / "tabla_top5_estabilidad.csv")
