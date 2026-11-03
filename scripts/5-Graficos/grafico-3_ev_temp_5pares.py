# EVOLUCION TEMPORAL DE ALGUNAS CONEXIONES ENTRE PAISES

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
series_temporales = pd.read_parquet(PATH_RESULTADOS / "series_temporales.parquet")
peso_promedio_pares = pd.read_parquet(PATH_RESULTADOS / "peso_promedio_pares.parquet")

# Seleccionar los cinco pares con mayor peso promedio
top_5_pares = peso_promedio_pares.sort_values(by="peso_promedio",  ascending=False).head(5)["pares"].tolist()

# Asegurar orden cronológico
series_temporales["fecha"] = pd.to_datetime(series_temporales["fecha"])

series_temporales = series_temporales.sort_values("fecha")



fig, ax = plt.subplots(figsize=(12, 6))

for par in top_5_pares:
    ax.plot(
        series_temporales["fecha"],
        series_temporales[par],
        label=par,
        linewidth=1.0
    )


ax.set_xlabel("Fecha")
ax.set_ylabel("Peso de co-consumo")
ax.set_title("Evolución temporal de las cinco conexiones más fuertes")
ax.legend(title="Par de países", frameon=False)

ax.grid(axis="y", alpha=0.15)

#ax.spines["top"].set_visible(False)
#ax.spines["right"].set_visible(False)

#fig.autofmt_xdate()
plt.tight_layout()
#plt.savefig(PATH_GRAFICOS / "03_evolucion_top5_pares.pdf")
plt.show()



fig, ax = plt.subplots(figsize=(12, 6))

for par in top_5_pares:
    valores = series_temporales[par]

    promedio_movil = valores.rolling(
        window=10,
        min_periods=1
    ).mean()

    ax.plot(
        series_temporales["fecha"],
        promedio_movil,
        label=par,
        linewidth=1.5
    )

ax.set_xlabel("Fecha")
ax.set_ylabel("Peso promedio móvil (10 días)")
ax.set_title("Evolución temporal suavizada de las cinco conexiones principales")

ax.legend(title="Par de países", frameon=False)
ax.grid(axis="y", alpha=0.3)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

#fig.autofmt_xdate()
plt.tight_layout()
plt.show()
