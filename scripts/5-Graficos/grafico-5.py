# Grafico 3. conectividad promedio de cada pais

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
conexion_total_promedio2 = pd.read_parquet(PATH_RESULTADOS / "conexion_total_promedio2.parquet")





# Ordenar países por conexión total promedio
conexion_ordenada = conexion_total_promedio2.sort_values(
    by="conexion_total_promedio",
    ascending=False
)

fig, ax = plt.subplots(figsize=(9, 6))
ax.barh(conexion_ordenada["pais"],conexion_ordenada["conexion_total_promedio"])
ax.invert_yaxis()
ax.set_xlabel("País")
ax.set_ylabel("Conexión total promedio")
ax.set_title("Conectividad promedio por país")

plt.tight_layout()
plt.savefig(PATH_GRAFICOS / "03_conectividad_paises.pdf")
plt.show()
