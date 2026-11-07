# DESCRIPCION DE LA MATRIZ PROMEDIO
# Figura de dos paneles: (a) mapa de colores de la matriz de similitud promedio,
# (b) las diez conexiones con mayor peso promedio

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

PATH_RESULTADOS = Path("../../Resultados/AnalisisW")
PATH_GRAFICOS = Path("../../Resultados/GraficosAnalisisW")
#PATH_GRAFICOS.mkdir(parents=True, exist_ok=True)

# Opciones
MASCARA_DIAGONAL = False   # True: no colorea la diagonal (útil si distorsiona la escala de color)
MOSTRAR_VALORES = False    # True: escribe el valor dentro de cada celda del mapa

# Países
paises = ["BR", "CA", "DE", "FR", "GB",
          "IN", "JP", "KR", "MX", "RU", "US"]

# ---------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------
W_promedio = pd.read_parquet(PATH_RESULTADOS / "W_promedio.parquet")
W_promedio = W_promedio.loc[paises, paises]          # orden elegido de países

peso_promedio_pares = pd.read_parquet(PATH_RESULTADOS / "peso_promedio_pares.parquet")
top_10 = (
    peso_promedio_pares
    .sort_values(by="peso_promedio", ascending=False)
    .head(10)
)

valores = W_promedio.values.astype(float)
if MASCARA_DIAGONAL:
    valores = valores.copy()
    np.fill_diagonal(valores, np.nan)

# ---------------------------------------------------------------
# Figura de dos paneles
# ---------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(
    1, 2,
    figsize=(15, 5.8),
    gridspec_kw={"width_ratios": [1.0, 1.0]},
    constrained_layout=True
)
fig.get_layout_engine().set(wspace=0.10, w_pad=0.25)

# Panel (a): mapa de colores
imagen = ax1.imshow(valores, cmap="viridis", aspect="equal")

ax1.set_xticks(range(len(paises)))
ax1.set_yticks(range(len(paises)))
ax1.set_xticklabels(paises)
ax1.set_yticklabels(paises)
ax1.set_xlabel("País", fontsize=12)
ax1.set_ylabel("País", fontsize=12)
ax1.set_title("(a) Matriz de similitud promedio", loc="left", fontsize=11)

if MOSTRAR_VALORES:
    umbral = np.nanmax(valores) * 0.5
    for i in range(len(paises)):
        for j in range(len(paises)):
            if np.isnan(valores[i, j]):
                continue
            ax1.text(
                j, i, f"{valores[i, j]:.2f}",
                ha="center", va="center", fontsize=7,
                color="white" if valores[i, j] < umbral else "black"
            )

barra = fig.colorbar(imagen, ax=ax1, fraction=0.046, pad=0.04)
barra.set_label("Peso promedio de co-consumo")

# Panel (b): diez conexiones más fuertes
barras = ax2.barh(top_10["pares"], top_10["peso_promedio"], color="steelblue")
ax2.invert_yaxis()                                   # el par más fuerte arriba
ax2.set_xlabel("Peso promedio de co-consumo", fontsize=12)
ax2.set_ylabel("Par de países", fontsize=12)
ax2.set_title("(b) Las diez conexiones más fuertes", loc="left", fontsize=11)
ax2.bar_label(barras, fmt="%.2f", padding=2)
ax2.margins(x=0.1)                                   # espacio para las etiquetas de las barras

plt.savefig(PATH_GRAFICOS / "01_descripcion_matriz_promedio.pdf")
plt.savefig(PATH_GRAFICOS / "01_descripcion_matriz_promedio.png", dpi=300)
plt.show()
