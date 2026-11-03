# script para convertir los archivos .csv en formato .parquet.

import pandas as pd
from pathlib import Path


# lista de paises
paises = ["BR", "CA", "DE", "FR", "GB", "IN", "JP", "KR", "MX", "RU", "US"]

# Carpeta donde está este script
aqui = Path(__file__).resolve().parent

# Raíz del proyecto
raiz = aqui.parents[1]


for pais in paises:
	
	archivo_input  = raiz / "data" / "raw" / f"{pais}_youtube_trending_data.csv"
	archivo_output = raiz / "data" / f"{pais}_youtube_trending_data.parquet"
	
	df = pd.read_csv(archivo_input)
	df.to_parquet(archivo_output,
				 compression='zstd',
				 index = False
				 )

#for pais in paises:
	
#	df = pd.read_csv(f'../../data/raw/{pais}_youtube_trending_data.csv')
#	df.to_parquet(f'../../data/{pais}_youtube_trending_data.parquet',
#				 compression='zstd',
#				 index = False
#				 )


#df = pd.read_csv('../data/raw/US_youtube_trending_data.csv')
#df.to_parquet('../data/parquet/US_youtube_trending_data.parquet', compression="zstd", #index=False)
