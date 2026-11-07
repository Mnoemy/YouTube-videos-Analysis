# GRAFICOS DE DISPERSION PARA EL MRQAP
# (a) similitud (W) vs distancia geográfica; (b) similitud (W) vs distancia cultural.
# Un punto por par de países (55 pares). Recrea las matrices del script de R.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PATH_HOFSTEDE = Path("../../data/4-dimensiones-hofstede-2015-08-16.csv")
PATH_CEPII = Path("../../data/geo_cepii.xls")          # pd.read_excel de .xls requiere el paquete xlrd
PATH_W = Path("../../Resultados/AnalisisW/W_promedio.parquet")
PATH_GRAFICOS = Path("../../Resultados/GraficosAnalisisW")
PATH_GRAFICOS.mkdir(parents=True, exist_ok=True)

# Opciones
USAR_LOG = True        # True: eje Y = log(1 + W); False: eje Y = W
N_ETIQUETAS = 5        # cuántos pares (los más alejados de la recta) se etiquetan en cada panel

paises = ["BR", "CA", "DE", "FR", "GB",
          "IN", "JP", "KR", "MX", "RU", "US"]
n = len(paises)
dimensiones = ["IDV", "PDI", "MAS", "UAI"]

# ---------------------------------------------------------------
# Distancia cultural (Kogut y Singh con las 4 dimensiones de Hofstede)
# ---------------------------------------------------------------
hof = pd.read_csv(PATH_HOFSTEDE)
hof = hof[hof["country"].isin(paises)][["country"] + dimensiones]
if len(hof) != n or hof["country"].duplicated().any():
    raise ValueError("Hofstede: faltan países o hay duplicados.")
hof = hof.set_index("country").loc[paises]
if hof.isna().any().any():
    raise ValueError("Hofstede: hay valores faltantes.")

C = hof[dimensiones].to_numpy(dtype=float)
V = C.var(axis=0, ddof=1)                      # varianza muestral entre los 11 países (igual que var() de R)
D_cult = (((C[:, None, :] - C[None, :, :]) ** 2) / V).sum(axis=2) / len(dimensiones)

# ---------------------------------------------------------------
# Distancia geográfica (Haversine entre capitales, CEPII), en km
# ---------------------------------------------------------------
cepii = pd.read_excel(PATH_CEPII)
cap = cepii[(cepii["iso2"].isin(paises)) & (cepii["cap"] == 1)][["iso2", "city_en", "lat", "lon"]]
if len(cap) != n or cap["iso2"].duplicated().any():
    raise ValueError("CEPII: no se encontró exactamente una capital por país.")
cap = cap.set_index("iso2").loc[paises]

lat = np.radians(cap["lat"].to_numpy(dtype=float))
lon = np.radians(cap["lon"].to_numpy(dtype=float))
dlat = lat[None, :] - lat[:, None]
dlon = lon[None, :] - lon[:, None]
a = np.sin(dlat / 2) ** 2 + np.cos(lat)[:, None] * np.cos(lat)[None, :] * np.sin(dlon / 2) ** 2
D_geo = 2 * 6371 * np.arcsin(np.sqrt(a))

# ---------------------------------------------------------------
# Matriz de similitud W
# ---------------------------------------------------------------
W_df = pd.read_parquet(PATH_W)
if "country" in W_df.columns:
    W_df = W_df.set_index("country")
W = W_df.loc[paises, paises].to_numpy(dtype=float)

# ---------------------------------------------------------------
# Pares únicos (triángulo superior): 55 diadas
# ---------------------------------------------------------------
iu = np.triu_indices(n, k=1)
w = W[iu]
y = np.log1p(w) if USAR_LOG else w
x_geo = D_geo[iu]
x_cult = D_cult[iu]
etiquetas = [f"{paises[i]}-{paises[j]}" for i, j in zip(*iu)]

print(f"Pares: {len(w)}")
print(f"Correlación entre distancia geográfica y cultural: {np.corrcoef(x_geo, x_cult)[0, 1]:.3f}")


def panel(ax, x, y, xlabel, titulo):
    """Dispersión con recta de ajuste simple y etiquetas de los pares más alejados."""
    pendiente, intercepto = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 100)
    ax.scatter(x, y, s=24, alpha=0.8, edgecolor="white", linewidth=0.4)
    ax.plot(xs, intercepto + pendiente * xs, color="black", linewidth=1)

    residuos = y - (intercepto + pendiente * x)
    for k in np.argsort(-np.abs(residuos))[:N_ETIQUETAS]:
        ax.annotate(etiquetas[k], (x[k], y[k]), xytext=(4, 4),
                    textcoords="offset points", fontsize=8)

    r = np.corrcoef(x, y)[0, 1]
    ax.text(0.97, 0.95, f"r = {r:.2f}", transform=ax.transAxes,
            ha="right", va="top", fontsize=9)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_title(titulo, loc="left", fontsize=11)
    ax.grid(alpha=0.2)
    print(f"{titulo}: r = {r:.3f}")


# ---------------------------------------------------------------
# Figura de dos paneles
# ---------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True,
                               constrained_layout=True)
fig.get_layout_engine().set(wspace=0.08, w_pad=0.2)

panel(ax1, x_geo, y, "Distancia entre capitales (km)", "(a) Distancia geográfica")
panel(ax2, x_cult, y, "Distancia cultural (Kogut y Singh)", "(b) Distancia cultural")

ax1.set_ylabel("log(1 + W)" if USAR_LOG else "Peso promedio de co-consumo (W)", fontsize=11)

sufijo = "log" if USAR_LOG else "W"
#plt.savefig(PATH_GRAFICOS / f"05_dispersion_mrqap_{sufijo}.pdf")
#plt.savefig(PATH_GRAFICOS / f"05_dispersion_mrqap_{sufijo}.png", dpi=300)
plt.show()
