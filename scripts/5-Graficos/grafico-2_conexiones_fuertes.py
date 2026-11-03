# Grafico 2. Las diez conexiones entre paises mas fuertes

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


PATH_RESULTADOS = Path("../../Resultados/AnalisisW")
PATH_GRAFICOS = Path("../../Resultados/GraficosAnalisisW")
PATH_GRAFICOS.mkdir(parents=True, exist_ok=True)


# Países
paises = ["BR", "CA", "DE", "FR", "GB",
          "IN", "JP", "KR", "MX", "RU", "US"]


# Cargar resultados
peso_promedio_pares2 = pd.read_parquet(PATH_RESULTADOS / "peso_promedio_pares.parquet")


# Ordenar los pares por peso promedio
top_10 = peso_promedio_pares2.sort_values(by="peso_promedio",ascending=False).head(10)

fig, ax = plt.subplots(figsize=(10, 6))

# Barras horizontales
barras = ax.barh(
    top_10["pares"],
    top_10["peso_promedio"],
    color="steelblue")

ax.invert_yaxis()
ax.set_xlabel("Peso promedio de co-consumo", fontsize=13)
ax.set_ylabel("Par de países", fontsize=13)
ax.set_title("Las diez conexiones más fuertes")

# mostrar valores al final de las barras
ax.bar_label(barras, fmt="%.2f", padding=2)


#ax.spines["top"].set_visible(False) # quita borde superior del marco
#ax.spines["right"].set_visible(False) # quita borde derecho del marco

plt.tight_layout()
#plt.savefig(PATH_GRAFICOS / "02_top10_conexiones.pdf")
plt.show()
