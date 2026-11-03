# script para pasar a archivos que solo tengan las columnas "video_id" y "trending_date"

from pathlib import Path
import pandas as pd

# Carpeta con los .parquet de entrada y carpeta de salida
PATH_entrada = Path('../../data/parquet/')
PATH_salida = Path('../../data/parquetFiltrado1/')
PATH_salida.mkdir(exist_ok=True)

columnas = ["video_id", "trending_date"]

for archivo in sorted(carpeta_entrada.glob("*.parquet")):

	# lee solo las dos columnas
	df = pd.read_parquet(archivo, columns=columnas)

	df['trending_date'] = pd.to_datetime(df['trending_date'], utc=True).dt.date

	nuevo_nombre = f"{archivo.stem}_filtrado1.parquet"

	df.to_parquet(carpeta_salida / nuevo_nombre, index=False, compression='zstd')

	print(f'listo: {archivo.name} --> {nuevo_nombre} ({len(df)} filas')

 #    # video_id en minúsculas
 #    # df["video_id"] = df["video_id"].str.lower()

 #    # trending_date: de "2020-08-12T00:00:00Z" a solo la fecha
	# df["trending_date"] = pd.to_datetime(df["trending_date"], utc=True).dt.date
	# nuevo_nombre = f"{archivo.stem}_filtrado1.parquet"
	# df.to_parquet(carpeta_salida / nuevo_nombre, index=False, compression="zstd")
 #    print(f"Listo: {archivo.name} -> {nuevo_nombre} ({len(df)} filas)")

# nuevo_nombre = f"{archivo.stem}_filtrado.parquet"
