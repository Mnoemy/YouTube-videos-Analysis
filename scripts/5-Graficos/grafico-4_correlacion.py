# Grafico 8. Estabilida estructural de la red


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

PATH_RESULTADOS = Path("../../Resultados/analisisW")

PATH_GRAFICOS = Path("../../Resultados/GraficosAnalisisW")
PATH_GRAFICOS.mkdir(parents=True, exist_ok=True)


# Países
paises = ["BR", "CA", "DE", "FR", "GB",
          "IN", "JP", "KR", "MX", "RU", "US"]


# Cargar resultados
estabilidad_diaria = pd.read_parquet(PATH_RESULTADOS / "estabilidad_diaria.parquet")

print(estabilidad_diaria.columns)

estabilidad_diaria["fecha"] = pd.to_datetime(estabilidad_diaria["fecha"])
estabilidad_diaria = estabilidad_diaria.sort_values("fecha")

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(estabilidad_diaria["fecha"],
        estabilidad_diaria["correlacion"],
        linewidth=1.2,
        label="correlación diaria")

promedio =  estabilidad_diaria["correlacion"].mean()

ax.axhline(promedio,
           linestyle="--",
           linewidth=1.5,
           label=f"Promedio = {promedio:.2f}")


ax.set_xlabel("Fecha")
ax.set_ylabel("Correlación con la red promedio")
ax.set_title("Estabilidad temporal de la estructura de la red")

#ax.set_ylim(-1, 1)
ax.legend(frameon=False)
ax.grid(axis="y", alpha=0.2)

#ax.spines["top"].set_visible(False)
#ax.spines["right"].set_visible(False)


plt.tight_layout()
#plt.savefig(PATH_GRAFICOS / "04_estabilidad_estructural.pdf")
plt.savefig(PATH_GRAFICOS / "04_estabilidad_estructural.png", dpi=300)
plt.show()
