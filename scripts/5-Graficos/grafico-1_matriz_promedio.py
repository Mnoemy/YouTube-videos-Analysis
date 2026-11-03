# Grfico 1: mapas de colores de la matriz de similitud promedio para los 55 pares
# de paises.

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


# Cargar resultados matriz promedio
W_promedio = pd.read_parquet(PATH_RESULTADOS / "W_promedio.parquet")

# Asegura que los paises aparezcan en el orden elegido
W_promedio = W_promedio.loc[paises, paises]


fig, ax = plt.subplots(figsize=(9, 7))

imagen = ax.imshow(
    W_promedio.values,
    cmap="viridis", # a1
    aspect="equal")

ax.set_xticks(range(len(paises)))
ax.set_yticks(range(len(paises)))

ax.set_xticklabels(paises)
ax.set_yticklabels(paises)

ax.set_xlabel("País", fontsize=13)
ax.set_ylabel("País", fontsize=13)
ax.set_title("Matriz de similitud promedio entre países")


# Agregar valores dentro de las celdas
for i in range(len(paises)):
    for j in range(len(paises)):
        ax.text(
            j, i,
            f"{W_promedio.iloc[i, j]:.2f}",
            ha="center",
            va="center",
            color="white" if W_promedio.iloc[i, j]>W_promedio.values.max() * 0.5 else "black",
            fontsize=8)

barra = fig.colorbar(imagen, ax=ax)
barra.set_label("Peso promedio de co-consumo")

plt.tight_layout()
#plt.savefig(PATH_GRAFICOS / "01_matriz_promedio.pdf")
plt.show()
