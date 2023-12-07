library(corrplot)
library(visdat)
library(tidyverse)
library(vip)
library(tidymodels)

tidymodels::tidymodels_prefer()

# banco de dados

df <- vroom::vroom("../../../data/joao_pessoa.csv") |>
  filter(!(tipo %in% c("sobrados", "coberturas")), !is.na(valor), !is.na(area)) |>
  select(-c(iptu, condominio, id, andar, url))

# dividindo teste e treinamento

train_test_split <- initial_split(df, strata = valor)

train <- training(train_test_split)
test <- testing(train_test_split)

train <- train |>
  mutate(
    academia = replace_na(academia, 0),
    area_servico = replace_na(area_servico, 0),
    elevador = replace_na(elevador, 0),
    playground = replace_na(playground, 0),
    spa = replace_na(spa, 0),
    portaria_24_horas = replace_na(portaria_24_horas, 0),
    salao_de_festa = replace_na(salao_de_festa, 0),
    espaco_gourmet = replace_na(espaco_gourmet, 0),
    piscina = replace_na(piscina, 0),
    quadra_de_esporte = replace_na(quadra_de_esporte, 0),
    sauna = replace_na(sauna, 0),
    varanda_gourmet = replace_na(varanda_gourmet, 0)
  )

test <- test |>
  mutate(
    academia = replace_na(academia, 0),
    area_servico = replace_na(area_servico, 0),
    elevador = replace_na(elevador, 0),
    playground = replace_na(playground, 0),
    spa = replace_na(spa, 0),
    portaria_24_horas = replace_na(portaria_24_horas, 0),
    salao_de_festa = replace_na(salao_de_festa, 0),
    espaco_gourmet = replace_na(espaco_gourmet, 0),
    piscina = replace_na(piscina, 0),
    quadra_de_esporte = replace_na(quadra_de_esporte, 0),
    sauna = replace_na(sauna, 0),
    varanda_gourmet = replace_na(varanda_gourmet, 0)
  )

# remover outliers

remove_outlier <- function(df, feature, threshold = 1.5) {
  df_copy <- df
  q3 <- quantile(unlist(df_copy[feature]), .99, na.rm = TRUE)
  q1 <- quantile(unlist(df_copy[feature]), .01, na.rm = TRUE)
  iqr <- q3 - q1
  upper <- q3 + iqr * threshold
  remove_rows <- which(df_copy[feature] > upper)

  if (feature == "valor") {
    df_copy[-c(remove_rows), ] |>
      dplyr::filter(valor >= 1e5)
  } else {
    df_copy[-c(remove_rows), ]
  }
}


train |>
  mutate(valor_area = log1p(valor * area)) |>
  remove_outlier("valor") |>
  remove_outlier("area") |>
  filter(area >= 25 & valor >= 40000)

remove_outlier(train, "valor")
remove_outlier(test, "valor")
