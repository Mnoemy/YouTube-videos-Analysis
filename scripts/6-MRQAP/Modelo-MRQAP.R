
# ============================================================
# SIMILITUD ENTRE PAISES A PARTIR DE VIDEOS DE YOUTUBE
#
# Analisis MRQAP
#
# Variables:
#   W       : matriz de similitud entre paises (variable dependiente)
#   D_geo   : distancia geografica
#   D_cult  : distancia cultural
#
# Modelos:
#   1. W
#   2. log(1 + W); para robustez.
#
# ============================================================


#  BIBLIOTECAS
library(sna)
library(readr)
library(readxl)
library(dplyr)
library(arrow)


# Orden de los paises.
paises <- c(
  "BR", "CA", "DE", "FR", "GB",
  "IN", "JP", "KR", "MX", "RU", "US"
)

n <- length(paises)

# Directorio donde se encuentran los archivos.
PATH_HOFSTEDE <- "../../data/4-dimensiones-hofstede-2015-08-16.csv"
PATH_CEPII <- "../../data/geo_cepii.xls"
PATH_W <- "../../Resultados/AnalisisW/W_promedio.parquet"


# ============================================================
# 2. MATRIZ DE DISTANCIA CULTURAL
# ============================================================

# Leer datos de Hofstede.
hofstede <- read_csv(PATH_HOFSTEDE, show_col_types = FALSE)


# Seleccionar los paises y dimensiones de interes.
dimensiones <- c("IDV", "PDI", "MAS", "UAI")

hofstede <- hofstede %>%
  filter(country %in% paises) %>%
  select(country, all_of(dimensiones))


# Verificar que tenemos los 11 paises.

if (nrow(hofstede) != n) {
  stop("Error: no se encontraron los 11 paises en Hofstede.")
}

if (anyDuplicated(hofstede$country)) {
  stop("Error: hay paises duplicados en los datos de Hofstede.")
}


# Ordenar los paises.

hofstede$country <- factor(
  hofstede$country,
  levels = paises
)

hofstede <- hofstede %>%
  arrange(country)


# Convertir las dimensiones culturales en matriz.

C <- as.matrix(hofstede[, dimensiones])

storage.mode(C) <- "numeric"


# Verificar datos faltantes.
if (anyNA(C)) {stop("Error: hay valores faltantes en Hofstede.")}


# Calcular la varianza de cada dimension cultural.
varianzas <- apply(C, 2, var)


# Construir matriz de distancia cultural.

# D_cult(i,j) = (1/4) * suma_k [(C_ik - C_jk)^2 / V_k]

D_cult <- matrix(
  0,
  nrow = n,
  ncol = n,
  dimnames = list(paises, paises)
)

for (i in 1:n) {

  for (j in 1:n) {

    diferencias <- (C[i, ] - C[j, ])^2

    D_cult[i, j] <- sum(
      diferencias / varianzas
    ) / length(dimensiones)

  }

}


# Comprobaciones.
stopifnot(
  all(dim(D_cult) == c(n, n)),
  isTRUE(all.equal(D_cult, t(D_cult))),
  all(diag(D_cult) == 0)
)

# ============================================================
# 3. MATRIZ DE DISTANCIA GEOGRAFICA
# ============================================================

# Leer datos geograficos de CEPII.
cepii <- read_excel(PATH_CEPII)


# Seleccionar las capitales de los 11 paises.
# cap == 1 identifica las capitales.

capitales <- cepii %>%
  filter(
    iso2 %in% paises,
    cap == 1
  ) %>%
  select(iso2, city_en, lat, lon)


# Verificar que tenemos una capital por pais.

if (nrow(capitales) != n) {
  stop("Error: no se encontraron exactamente 11 capitales.")
}

if (anyDuplicated(capitales$iso2)) {
  stop("Error: hay paises con mas de una capital seleccionada.")
}


# Ordenar las capitales.

capitales$iso2 <- factor(
  capitales$iso2,
  levels = paises
)

capitales <- capitales %>%
  arrange(iso2)


# Verificar coordenadas.

if (anyNA(capitales$lat) || anyNA(capitales$lon)) {
  stop("Error: existen coordenadas faltantes.")
}


# Funcion de distancia Haversine.
# Resultado en kilometros.

haversine <- function(lat1, lon1, lat2, lon2) {

  R <- 6371

  lat1 <- lat1 * pi / 180
  lon1 <- lon1 * pi / 180

  lat2 <- lat2 * pi / 180
  lon2 <- lon2 * pi / 180

  dlat <- lat2 - lat1
  dlon <- lon2 - lon1

  a <- sin(dlat / 2)^2 +
    cos(lat1) * cos(lat2) * sin(dlon / 2)^2

  distancia <- 2 * R * asin(sqrt(a))

  return(distancia)

}


# Construir matriz de distancia geografica.

D_geo <- matrix(
  0,
  nrow = n,
  ncol = n,
  dimnames = list(paises, paises)
)


for (i in 1:n) {

  for (j in 1:n) {

    D_geo[i, j] <- haversine(
      capitales$lat[i],
      capitales$lon[i],
      capitales$lat[j],
      capitales$lon[j]
    )

  }

}


# Comprobaciones.

stopifnot(
  all(dim(D_geo) == c(n, n)),
  isTRUE(all.equal(D_geo, t(D_geo))),
  all(diag(D_geo) == 0)
)


# ============================================================
# 4. LEER MATRIZ DE SIMILITUD W
# ============================================================

# Leer archivo Parquet.

W_df <- as.data.frame(read_parquet(PATH_W))


# Revisar nombres de columnas.

print(names(W_df))


# Recuperar los nombres de las filas.
if ("country" %in% names(W_df)) {

  rownames(W_df) <- as.character(W_df$country)

  W_df$country <- NULL

} else if ("__index_level_0__" %in% names(W_df)) {

  rownames(W_df) <- as.character(
    W_df$`__index_level_0__`
  )

  W_df$`__index_level_0__` <- NULL

} else {

  # Si el archivo no contiene los nombres de las filas,
  # se utiliza el orden de paises definido anteriormente.

  if (nrow(W_df) != n) {
    stop("Error: dimensiones inesperadas en W.")
  }

  rownames(W_df) <- paises

}


# Verificar que estan todas las columnas.

if (!all(paises %in% names(W_df))) {
  stop("Error: faltan columnas de paises en W.")
}


# Convertir a matriz numerica.
W <- as.matrix(W_df[, paises, drop = FALSE])

storage.mode(W) <- "numeric"


# Verificar el orden de los paises.
if (!setequal(rownames(W), paises)) {
  stop("Error: los nombres de las filas de W no coinciden.")
}

W <- W[paises, paises]


# Comprobaciones de la matriz W.
stopifnot(
  all(dim(W) == c(n, n)),
  identical(rownames(W), paises),
  identical(colnames(W), paises),
  isTRUE(all.equal(W, t(W), tolerance = 1e-10)),
  all(diag(W) == 0),
  !anyNA(W)
)



# ============================================================
# 5. ESTANDARIZACION Y COMPROBACIONES
# ============================================================

# Estandarizar una matriz utilizando solamente
# los valores correspondientes a las parejas unicas.
#
# Se utilizan los elementos del triangulo superior.
# Posteriormente se reconstruye la matriz simetrica.

estandarizar_matriz <- function(M) {

  valores <- M[upper.tri(M)]

  valores_std <- as.numeric(scale(valores))

  M_std <- matrix(
    0,
    nrow = nrow(M),
    ncol = ncol(M),
    dimnames = dimnames(M)
  )

  M_std[upper.tri(M_std)] <- valores_std

  M_std[lower.tri(M_std)] <- t(M_std)[lower.tri(M_std)]

  return(M_std)

}


# Estandarizar matrices explicativas.

D_geo_std <- estandarizar_matriz(D_geo)
D_cult_std <- estandarizar_matriz(D_cult)


# Correlacion entre las variables explicativas.
# Se utilizan las 55 parejas unicas.

correlacion <- cor(
  D_geo_std[upper.tri(D_geo_std)],
  D_cult_std[upper.tri(D_cult_std)]
)

cat("\nCorrelacion entre distancias:\n")
print(correlacion)


# Resumen de la matriz W.
cat("\nResumen de los pesos de W:\n")
print(summary(W[upper.tri(W)]))


# Mostrar matrices.
cat("\nMatriz de similitud W:\n")
print(round(W, 3))

cat("\nMatriz de distancia geografica:\n")
print(round(D_geo, 2))

cat("\nMatriz de distancia cultural:\n")
print(round(D_cult, 3))


# ============================================================
# 6. MODELO MRQAP CON LA MATRIZ W ORIGINAL
# ============================================================

set.seed(1234)

modelo <- netlm(
  y = W,
  x = list(D_geo_std, D_cult_std),
  intercept = TRUE,
  mode = "graph",
  diag = FALSE,
  nullhyp = "qapspp",
  test.statistic = "t-value",
  reps = 10000
)


# Resultados del primer modelo.

cat("\n========================================\n")
cat("MODELO 1: MATRIZ W ORIGINAL\n")
cat("========================================\n")

summary(modelo)


# ============================================================
# 7. MODELO MRQAP CON LA MATRIZ TRANSFORMADA
# ============================================================

# Transformacion logaritmica.

W_log <- log1p(W)


set.seed(1234)

modelo_log <- netlm(
  y = W_log,
  x = list(D_geo_std, D_cult_std),
  intercept = TRUE,
  mode = "graph",
  diag = FALSE,
  nullhyp = "qapspp",
  test.statistic = "t-value",
  reps = 10000
)


# Resultados del segundo modelo.

cat("\n========================================\n")
cat("MODELO 2: LOG(1 + W)\n")
cat("========================================\n")

summary(modelo_log)





# ============================================================
# 9. GUARDAR RESULTADOS Y MODELOS
# ============================================================


# Crear carpeta para guardar los resultados.

dir.create("../../Resultados/resultados_MRQAP", showWarnings = FALSE)


# Guardar resumen del modelo original.

sink("../../Resultados/resultados_MRQAP/modelo_W.txt")

cat("MODELO 1: MATRIZ W ORIGINAL\n\n")

print(summary(modelo))

sink()


# Guardar resumen del modelo transformado.

sink("../../Resultados/resultados_MRQAP/modelo_W_log.txt")

cat("MODELO 2: MATRIZ LOG(1 + W)\n\n")

print(summary(modelo_log))

sink()


# Guardar los objetos completos de ambos modelos.

#save(modelo, modelo_log, file = "../../Resultados/resultados_MRQAP/modelos_MRQAP.RData")


# Guardar también cada modelo por separado.
#saveRDS(modelo, file = "../../Resultados/resultados_MRQAP/modelo_W.rds")

#saveRDS(modelo_log, file = "../../Resultados/resultados_MRQAP/modelo_W_log.rds")


cat("\nResultados guardados en la carpeta resultados_MRQAP\n")
