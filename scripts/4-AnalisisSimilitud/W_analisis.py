# Script para analisis de las matrices de similitud.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path



PATH_W = Path("../../Resultados/matrizW/")
PATH_RESULTADOS = Path("../../Resultados/AnalisisW")
PATH_RESULTADOS.mkdir(parents=True, exist_ok=True)


# Lista de países
paises = [
    "BR", "CA", "DE", "FR", "GB", "IN",
    "JP", "KR", "MX", "RU", "US"
]


# Leer el archivo único y separarlo por fecha: {fecha: tabla del día}
W_todas = pd.read_parquet(PATH_W / "W_todas_las_fechas.parquet")
W_todas["fecha"] = pd.to_datetime(W_todas["fecha"])
W_fechas = {fecha: W for fecha, W in W_todas.groupby("fecha")}


def reconstruir_W(tabla, paises):
    """
    Reconstruye la matriz de pesos W a partir de una tabla
    con las columnas pais_i, pais_j y peso.

    Filas y columnas corresponden a los países (siempre 11x11).
    """

    # Inicializar una matriz de ceros
    W = pd.DataFrame(
        0.0,
        index=paises,
        columns=paises
    )

    # Introducir los pesos de las conexiones
    for _, fila in tabla.iterrows():

        pais_i = fila["pais_i"]
        pais_j = fila["pais_j"]
        peso = fila["peso"]

        W.loc[pais_i, pais_j] = peso
        W.loc[pais_j, pais_i] = peso

    return W


def extraer_pesos(W):
    """
    Extrae los 55 pesos de los pares de países,
    sin incluir la diagonal ni contar parejas dos veces.
    """

    pesos = []

    for i in range(len(paises)):
        for j in range(i + 1, len(paises)):

            pesos.append(W.iloc[i, j])

    return np.array(pesos)


def describir_W(W):
    """
    Entrega la estadística de los pesos para cada matriz.
    """

    pesos = extraer_pesos(W)

    return {
        "media": np.mean(pesos),
        "desviacion": np.std(pesos),
        "minimo": np.min(pesos),
        "maximo": np.max(pesos),
        "pares_positivos": np.sum(pesos > 0)
    }


def res_diario():

    resumen_diario = []

    for fecha, tabla in W_fechas.items():

        W = reconstruir_W(tabla, paises)

        resumen = describir_W(W)

        resumen["fecha"] = fecha

        resumen_diario.append(resumen)

    resumen_diario = pd.DataFrame(resumen_diario)
    resumen_diario = resumen_diario.sort_values("fecha")

    return resumen_diario


# CONSTRUIMOS SERIES TEMPORALES DE LOS 55 PARES
def extraer_pares_con_nombre(W):

    resultado = {}

    for i in range(len(paises)):
        for j in range(i + 1, len(paises)):

            pais_i = paises[i]
            pais_j = paises[j]

            nombre = f"{pais_i}-{pais_j}"

            resultado[nombre] = W.loc[pais_i, pais_j]

    return resultado


# Construir series temporales
def series_temp():

    series_pares = []

    for fecha, tabla in W_fechas.items():

        W = reconstruir_W(tabla, paises)

        pesos = extraer_pares_con_nombre(W)

        pesos["fecha"] = fecha

        series_pares.append(pesos)

    series_temporales = pd.DataFrame(series_pares)
    series_temporales = series_temporales.set_index("fecha")   # <- descomentado
    series_temporales = series_temporales.sort_index()

    return series_temporales


series_temporales = series_temp()


# Pesos promedio de cada pareja, ordenados de mayor a menor
def peso_mean():
    peso_promedio_pares = series_temporales.mean()
    peso_promedio_pares = peso_promedio_pares.sort_values(
        ascending=False)

    return peso_promedio_pares


# Estadística de pares
def resumen_pares():

    resumen_pares = pd.DataFrame({
        "peso_promedio": series_temporales.mean(),
        "desviacion": series_temporales.std(),
        "minimo": series_temporales.min(),
        "maximo": series_temporales.max()
    })

    return resumen_pares


def matriz_promedio():
    W_promedio = pd.DataFrame(
        0.0,
        index=paises,
        columns=paises)

    for i in range(len(paises)):
        for j in range(i + 1, len(paises)):

            par = f"{paises[i]}-{paises[j]}"
            peso = series_temporales[par].mean()

            W_promedio.loc[paises[i], paises[j]] = peso
            W_promedio.loc[paises[j], paises[i]] = peso

    return W_promedio


# Correlación diaria con la matriz promedio
def correlacion():
    pesos_promedio = extraer_pesos(matriz_promedio())

    correlaciones_diarias = []

    for fecha, fila in series_temporales.iterrows():

        pesos_dia = fila.to_numpy()

        # si alguno de los vectores es constante
        # la correlación de Pearson no está definida
        if (np.std(pesos_dia) == 0 or np.std(pesos_promedio) == 0):
            correlacion = np.nan

        else:
            correlacion = np.corrcoef(
                pesos_dia,
                pesos_promedio)[0, 1]

        correlaciones_diarias.append({
            "fecha": fecha,
            "correlacion": correlacion})

    correlaciones_diarias = pd.DataFrame(correlaciones_diarias)
    correlaciones_diarias = correlaciones_diarias.sort_values("fecha")

    return correlaciones_diarias


# Conexión total de cada país
def conexion_total():
    conexion_total = matriz_promedio().sum(axis=1)

    conexion_total = conexion_total.sort_values(
        ascending=False)

    return conexion_total


# Evolución temporal de la conexión total
def evol_temp_conexion():
    conexion_diaria = []

    for fecha, fila in series_temporales.iterrows():

        # inicializar las conexiones de todos los países
        conexiones = {
            pais: 0.0
            for pais in paises
        }

        # sumar el peso de cada pareja a ambos países
        for par, peso in fila.items():

            pais_i, pais_j = par.split("-")

            conexiones[pais_i] += peso
            conexiones[pais_j] += peso

        # añadir la fecha
        conexiones["fecha"] = fecha

        conexion_diaria.append(conexiones)

    conexion_diaria = pd.DataFrame(conexion_diaria)
    conexion_diaria = conexion_diaria.set_index("fecha")
    conexion_diaria = conexion_diaria.sort_index()

    return conexion_diaria


if __name__ == "__main__":

    # GUARDAMOS EN ARCHIVOS SEPARADOS LOS RESULTADOS DE INTERES

    rs = res_diario()
    st = series_temporales
    pm = peso_mean()
    mp = matriz_promedio()
    ct = conexion_total()
    ev = evol_temp_conexion()
    co = correlacion()
    rp = resumen_pares()


    rs.to_parquet(PATH_RESULTADOS / "resumen_diario.parquet", index=False)

    # Sin index=False: la fecha es el índice y se perdería
    st.reset_index().to_parquet(PATH_RESULTADOS / "series_temporales.parquet", index=False)

    pm.rename("peso_promedio").rename_axis("pares").reset_index().to_parquet(
        PATH_RESULTADOS / "peso_promedio_pares.parquet", index=False)

    mp.to_parquet(PATH_RESULTADOS / "W_promedio.parquet")

    ct.rename("conexion_total_promedio").rename_axis("pais").reset_index().to_parquet(
        PATH_RESULTADOS / "conexion_total_promedio.parquet", index=False)

    ev.to_parquet(PATH_RESULTADOS / "conexion_diaria_paises.parquet")

    co.to_parquet(PATH_RESULTADOS / "estabilidad_diaria.parquet", index=False)

    rp.to_parquet(PATH_RESULTADOS / "resumen_pares.parquet")
