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
resumen_diario = pd.read_parquet(PATH_RESULTADOS / "resumen_diario.parquet")
print(resumen_diario.columns)


resumen_diario["fecha"] = pd.to_datetime(resumen_diario["fecha"])
resumen_diario = resumen_diario.sort_values("fecha")

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(resumen_diario["fecha"],resumen_diario["media"])

ax.set_xlabel("Fecha")
ax.set_ylabel("Peso promedio")
ax.set_title("Evolución temporal del peso promedio de la red")
plt.tight_layout()
plt.savefig(PATH_GRAFICOS / "05_peso_promedio_temporal.pdf")
plt.show()
