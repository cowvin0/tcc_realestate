library(rvest)
library(dplyr)
library(purrr)

base_url <- "https://cran.r-project.org/web/packages/"

first_package_link <- read_html(paste0(base_url, "index.html")) |>
    html_elements("a[target=_top]") |>
    html_attr("href") |>
    first()

package_url <- paste0(base_url, first_package_link)
package_page <- read_html(package_url)

packages_info <- package_page |>
    html_elements("tr") |>
    html_text2() |>
    tail(-1) |>
    map(~ strsplit(.x, "\t")[[1]])

packages_df <- tibble(
    publication_date = map_chr(packages_info, 1),
    package_name = map_chr(packages_info, 2),
    description_packs = map_chr(packages_info, 3)
)
