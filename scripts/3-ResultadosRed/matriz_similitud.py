# Script para crear y guardar las matrices de similitud de co-consumo

import numpy as np
import pandas as pd
from itertools import combinations
from pathlib import Path



# Ubicacion de los datos
PATH  = Path('../../data/parquetFiltrado2/')
PATH_RESULTADOS = Path('../../Resultados/matrizW/')
PATH_RESULTADOS.mkdir(exist_ok = True)


# lista de paises (codigo)
paises = ["BR", "CA", "DE", "FR", "GB",
          "IN", "JP", "KR", "MX", "RU", "US" ]


# Funcion para leer un dia de observaicones
def leer_dia(fecha):
    '''
    Funcion para ller los 11 archivos Parquet
    y obtiene los videos que aparecen en la lista de
    tendencias para una fecha
    '''

    tablas = []

    for pais in paises:

        archivo = (PATH / f'{pais}_youtube_trending_data_filtrado1_filtrado2.parquet')

        # leer solamente las dos columnas necesarias
        df = pd.read_parquet(archivo)

        # seleccionar solamente el dia
        df = df[df['trending_date'] == fecha].copy()

        # Agregar el pais
        df['pais'] = pais

        # Solo mantener lo necesario
        df = df[['pais', 'video_id']]

        tablas.append(df)

    # Unir los 11 paises
    pais_video = pd.concat(tablas, ignore_index = True)

    # evirar diplicados
    pais_video = pais_video.drop_duplicates()

    return pais_video

# Funcion para construir B

def construir_B(pais_video):
    '''
    construir la matriz B:

        filas = paises
        columnas = videos

    B_{ij} = 1, si el pais u tiene el video j
    B_{ij} = 0, otro caso.
    '''

    B = pais_video.pivot_table(
        index = 'pais',
        columns = 'video_id',
        aggfunc = lambda x: 1,
        fill_value = 0
    )

    return B


# Funcion para construir W
def construir_W(pais_video, fecha):
    '''
    Construir la red pais-pais.
    El peso utilizado es:

        W_{ij} = sum_{k} = 1/(n_k-1)

    Para todos los videos k que comparte los paises 1 y j.
    '''

    # Contamos el numero de paises donde aparece cada video
    n_paises = (pais_video.groupby('video_id')['pais'].nunique())

    # Solamente interesan los videos que aparecen en al menos dos paises
    videos_compartidos = n_paises[n_paises >=2]

    # Si no hay videos compartidos
    if len(videos_compartidos) == 0:

        return pd.DataFrame(
            columns=[
                'fecha',
                'pais_i',
                'pais_j',
                'peso'
            ]
        )

    # Crear parejas de paises para cada video
    pares = []

    for video in videos_compartidos.index:

        # Paises donde aparece este video
        paises_video = pais_video[pais_video['video_id'] == video]['pais'].tolist()

        # todas las parejas psibles
        for pais_i, pais_j in combinations(paises_video, 2):
            pares.append({
                'video_id': video,
                'pais_i': pais_i,
                'pais_j': pais_j
            })

    # Construir DataFrame
    pares = pd.DataFrame(pares)

    # Agregar n_k
    pares = pares.merge(n_paises.rename('n_paises'), left_on = 'video_id', right_index= True)

    # peso que aporta al video
    pares['peso'] = (1 / (pares['n_paises'] - 1 ))

    # Sumar las contribuciones de todos los videos

    W = (pares.groupby(['pais_i', 'pais_j'])['peso'].sum().reset_index())

    # agregar fecha
    W['fecha'] = fecha

    # Ordenar columnas
    W = W[['fecha', 'pais_i', 'pais_j', 'peso']]

    return W


print('obteniendo fechas...')

archivo_prueba = (PATH / f'{paises[0]}_youtube_trending_data_filtrado1_filtrado2.parquet')
df_fechas = pd.read_parquet(archivo_prueba, columns = ['trending_date'])
fechas = sorted(df_fechas['trending_date'].dropna().unique())

del df_fechas


print()
print('Numero de dias', len(fechas))
print('primer dia', fechas[0])
print('Ultimo dia', fechas[-1])




lista_W = []

for numero_dia, fecha in enumerate(fechas, start=1):

    # --------------------------------------------------------
    # Leer datos del día
    # --------------------------------------------------------

    pais_video = leer_dia(fecha)

    # --------------------------------------------------------
    # Construir B
    # --------------------------------------------------------

    B = construir_B(pais_video)

    # --------------------------------------------------------
    # Construir W
    # --------------------------------------------------------

    W = construir_W(pais_video, fecha)

    lista_W.append(W)


    del pais_video
    del B
    del W



W_todas = pd.concat(lista_W, ignore_index=True)

# Tipo de fecha uniforme
W_todas["fecha"] = pd.to_datetime(W_todas["fecha"])

W_todas.to_parquet(
    PATH_RESULTADOS / "W_todas_las_fechas.parquet",
    index=False,
    compression="zstd"
)


print()
print("==========================================")
print("PROCESO TERMINADO")
print("==========================================")
