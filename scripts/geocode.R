ENV <- Sys.getenv("CITY") |>
  stringr::str_sub(start = 4)

COND <- Sys.getenv("COND")

loc <- glue::glue("data/{ENV}-{COND}.csv")

df <- glue::glue(loc) |>
  readr::read_csv()

df_new <- df |>
  tidygeocoder::geocode(
    address = endereco, method = "arcgis",
    lat = "latitude", long = "longitude"
  )

df_new <- df_new |>
  dplyr::mutate(
    lat_norm = (latitude - mean(latitude)) / sd(latitude),
    long_norm = (longitude - mean(longitude)) / sd(longitude)
  ) |>
  dplyr::filter(lat_norm <= 2.5 & lat_norm >= - 2.5 & long_norm <= 2.5 & long_norm >= - 2.5) |>
  dplyr::select(
    -c(lat_norm, long_norm)
  )

df_new |> write.csv(loc, row.names = FALSE)
