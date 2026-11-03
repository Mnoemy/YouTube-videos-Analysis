# Script para considerar solo las fechas en comun entre cada pais
# si a alguno le falta una fecha, se descarta.

from pathlib import Path
import pandas as pd


carpeta_entrada = Path('../../data/parquetFiltrado1/')
carpeta_salida = Path("../../data/parquetFiltrado2/")
carpeta_salida.mkdir(exist_ok=True)


# La `direccion'; a la carpeta' donde estan guardados los arhichos parquet
paises = ["BR", "CA", "DE", "FR", "GB",
          "IN", "JP", "KR", "MX", "RU", "US" ]

# Leer cada país (el nombre del archivo es el país)
datos = {}

for archivo in sorted(carpeta_entrada.glob("*.parquet")):

    df = pd.read_parquet(archivo)
    df["trending_date"] = pd.to_datetime(df["trending_date"])   # asegura un tipo uniforme
    datos[archivo.stem] = df


# Conjunto de fechas únicas por país
fechas = {pais: set(df["trending_date"].unique()) for pais, df in datos.items()}


# Unión (todas las fechas que aparecen en alguno) e intersección (en todos)
union = set.union(*fechas.values())
comunes = set.intersection(*fechas.values())


print(f"Fechas en total (unión): {len(union)}")
print(f"Fechas comunes a todos:  {len(comunes)}")


if union == comunes:
    print("Todos los países tienen exactamente las mismas fechas.")

else:
    print("\nFechas que le faltan a cada país:")

    for pais, f in fechas.items():
        faltan = sorted(union - f)

        if faltan:
            print(f"  {pais}: {len(faltan)} fechas faltantes "
                  f"(de {pd.Timestamp(faltan[0]).date()} a {pd.Timestamp(faltan[-1]).date()})")

#  Quedarse solo con las fechas comunes y guardar
for pais, df in datos.items():

    df_filtrado = df[df["trending_date"].isin(comunes)]

    df_filtrado.to_parquet(carpeta_salida / f"{pais}_filtrado2.parquet", index=False, compression="zstd")

    print(f"{pais}: {len(df)} -> {len(df_filtrado)} filas")
