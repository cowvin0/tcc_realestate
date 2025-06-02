import json
import folium.plugins
import geopandas as gpd
import pandas as pd
import dash
import math
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.express as px
import dash_ag_grid as dag
import folium

import requests

from shapely.geometry import Point
from dash_iconify import DashIconify
from dash import (
    ALL,
    html,
    Output,
    Input,
    dcc,
    callback,
    State,
    callback_context,
    no_update,
    clientside_callback,
    ClientsideFunction,
)
from folium.plugins import HeatMap

dash.register_page(__name__, name="Análise de imóveis", path="/")


def predict_house_price(payload):
    url = "http://api:8050/real_data/predict"
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# def fetch_data():
#     response = requests.get("http://api:8050/real_data/return_data_db")
#     return response.json()


# df_realestate = pd.DataFrame(fetch_data()).assign(
#     tipo=lambda x: x.tipo.str.capitalize()
#     .str.split("_")
#     .str.join(" ")
#     .str.replace("condominio", "condomínio")
# )

df_realestate = (
    pd.read_csv("data/cleaned/jp_limpo_bairro_correto3.csv")
    .assign(
        tipo=lambda x: x.tipo.str.capitalize()
        .str.split("_")
        .str.join(" ")
        .str.replace("condominio", "condomínio")
    )
    .drop(columns="qnt_beneficio")
)

# bairro_geojson = gpd.read_file("app/dash/assets/geo_joao_pessoa/bairros.geojson")

CENTER_LAT = df_realestate["latitude"].mean()
CENTER_LON = df_realestate["longitude"].mean()


layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            [
                dbc.Col(
                    dmc.Card(
                        children=[
                            dcc.Graph(
                                id="bar-graph",
                                style={"height": "400px", "width": "100%"},
                                config={
                                    "displaylogo": False,
                                    "displayModeBar": False,
                                    "scrollZoom": False,
                                    "doubleClick": "reset",
                                    "modeBarButtonsToRemove": [
                                        "zoom",
                                        "zoomIn",
                                        "zoomOut",
                                        "pan",
                                        "lasso2d",
                                        "autoScale",
                                    ],
                                },
                            )
                        ],
                        withBorder=True,
                        shadow="sm",
                        radius="md",
                        style={"padding": "10px"},
                    ),
                    width=6,
                ),
                dbc.Col(
                    dmc.Card(
                        children=[
                            html.Div(
                                [
                                    dcc.Graph(
                                        id="plotly-map-container",
                                        style={"height": "400px", "width": "100%"},
                                        config={
                                            "displaylogo": False,
                                            "displayModeBar": False,
                                            "scrollZoom": True,
                                            "doubleClick": "reset",
                                            "modeBarButtonsToRemove": [
                                                "zoom",
                                                "zoomIn",
                                                "zoomOut",
                                                "pan",
                                                "lasso2d",
                                                "autoScale",
                                            ],
                                        },
                                    ),
                                    html.Div(
                                        id="leaflet-map-container",
                                        style={
                                            "height": "400px",
                                            "width": "100%",
                                        },
                                    ),
                                ]
                            ),
                            dcc.Store(
                                id="rios-geojson",
                                data=gpd.read_file(
                                    "app/dash/assets/geo_joao_pessoa/rios.geojson"
                                ).to_json(),
                            ),
                            dcc.Store(
                                id="pracas-geojson",
                                data=gpd.read_file(
                                    "app/dash/assets/geo_joao_pessoa/pracas.geojson"
                                ).to_json(),
                            ),
                            dcc.Store(
                                id="parques-geojson",
                                data=gpd.read_file(
                                    "app/dash/assets/geo_joao_pessoa/parques.geojson"
                                ).to_json(),
                            ),
                            dcc.Store(
                                id="faixas_exclusivas-geojson",
                                data=gpd.read_file(
                                    "app/dash/assets/geo_joao_pessoa/faixas_exclusivas.geojson"
                                ).to_json(),
                            ),
                            dcc.Store(
                                id="escolas_publicas-geojson",
                                data=gpd.read_file(
                                    "app/dash/assets/geo_joao_pessoa/escolas_publicas.geojson"
                                ).to_json(),
                            ),
                            dcc.Store(
                                id="corredores-geojson",
                                data=gpd.read_file(
                                    "app/dash/assets/geo_joao_pessoa/corredores.geojson"
                                ).to_json(),
                            ),
                            dcc.Store(
                                id="comunidades-geojson",
                                data=gpd.read_file(
                                    "app/dash/assets/geo_joao_pessoa/comunidades.geojson"
                                ).to_json(),
                            ),
                            dcc.Store(
                                id="ciclo-geojson",
                                data=gpd.read_file(
                                    "app/dash/assets/geo_joao_pessoa/ciclo.geojson"
                                ).to_json(),
                            ),
                            dcc.Store(
                                id="area_rural-geojson",
                                data=gpd.read_file(
                                    "app/dash/assets/geo_joao_pessoa/area_rural.geojson"
                                ).to_json(),
                            ),
                            dcc.Store(
                                id="bairro-geojson",
                                data=gpd.read_file(
                                    "app/dash/assets/geo_joao_pessoa/bairros.geojson"
                                ).to_json(),
                            ),
                            dcc.Store(
                                id="filtered-data-all",
                                data=df_realestate.to_dict("records"),
                            ),
                            dcc.Store(
                                id="filtered-data",
                                data=df_realestate.to_dict("records"),
                            ),
                            dcc.Store(id="stored-coordinates"),
                            dcc.Store(id="show-prediction-form", data=False),
                            dbc.Offcanvas(
                                id="offcanvas-table",
                                title="",
                                is_open=False,
                                scrollable=True,
                                placement="bottom",
                                style={"height": "53vh"},
                                children=[
                                    dag.AgGrid(
                                        id="realestate-table",
                                        columnDefs=[
                                            {
                                                "headerName": col,
                                                "field": col,
                                                "sortable": True,
                                                "filter": True,
                                            }
                                            for col in df_realestate.columns
                                        ],
                                        rowData=df_realestate.to_dict("records"),
                                        columnSize="autoSize",
                                        defaultColDef={"resizable": True},
                                        className="ag-theme-balham",
                                        style={"width": "100%"},
                                        dashGridOptions={
                                            "pagination": True,
                                            "paginationPageSize": 50,
                                        },
                                    ),
                                    dmc.Button(
                                        "Extraia os dados",
                                        id="download-btn",
                                        leftIcon=DashIconify(
                                            icon="material-symbols-light:download-rounded",
                                            width=25,
                                        ),
                                        m=0,
                                        className="mt-2",
                                    ),
                                    dcc.Download(id="download-dataframe-csv"),
                                ],
                            ),
                            dbc.Offcanvas(
                                id="offcanvas",
                                title=html.H5(
                                    "Controles",
                                    style={
                                        "color": "#2780e3",
                                        "fontSize": "2.5rem",
                                    },
                                ),
                                is_open=False,
                                style={"width": "25%"},
                                placement="end",
                                children=[
                                    html.P(
                                        "Utilize os controles abaixo para ajustar os filtros do mapa e"
                                        " realizar previsões dos valores de imóveis.",
                                        style={
                                            "marginBottom": "1rem",
                                            "fontSize": "1.2rem",
                                        },
                                    ),
                                    html.Hr(),
                                    dmc.Select(
                                        label=html.H5(
                                            "Tipos de mapa",
                                            style={
                                                "color": "#2780e3",
                                                "fontSize": "1.5rem",
                                            },
                                        ),
                                        placeholder="Selecione o tipo de mapa",
                                        id="map-select",
                                        value="heatmap",
                                        data=[
                                            {"value": "sem_tipo", "label": "Sem tipo"},
                                            {
                                                "value": "heatmap",
                                                "label": "Mapa de Calor",
                                            },
                                            {
                                                "value": "markers",
                                                "label": "Mapa de pontos",
                                            },
                                            {
                                                "value": "faixas_exclusivas",
                                                "label": "Faixas exclusivas",
                                            },
                                            {
                                                "value": "corredores",
                                                "label": "Corredores",
                                            },
                                            {
                                                "value": "comunidades",
                                                "label": "Comunidades",
                                            },
                                            {"value": "bairros", "label": "Bairros"},
                                            {"value": "rios", "label": "Rios"},
                                            {"value": "ciclo", "label": "Ciclovias"},
                                            {
                                                "value": "escolas_publicas",
                                                "label": "Escolas públicas",
                                            },
                                            {"value": "pracas", "label": "Praças"},
                                            {"value": "parques", "label": "Parques"},
                                        ],
                                        w=200,
                                        mb=10,
                                    ),
                                    html.Hr(),
                                    html.H5(
                                        "Simule o valor do imóvel",
                                        style={
                                            "color": "#2380e3",
                                            "fontSize": "1.5rem",
                                        },
                                    ),
                                    dmc.Button(
                                        "Estimar valor de imóvel",
                                        id="predict-button",
                                        n_clicks=0,
                                        className="btn btn-primary",
                                    ),
                                    html.Div(
                                        id="prediction-form",
                                        style={"display": "none"},
                                        children=[
                                            html.Hr(),
                                            html.H5(
                                                "Preencha as informações do imóvel",
                                                style={
                                                    "color": "#2380e3",
                                                    "fontSize": "1.5rem",
                                                },
                                            ),
                                            dmc.Select(
                                                id="input-tipo",
                                                data=[
                                                    {
                                                        "value": None,
                                                        "label": "Apartamento",
                                                    },
                                                    {"value": "casas", "label": "Casa"},
                                                    {
                                                        "value": "casas_de_condominio",
                                                        "label": "Casa de condomínio",
                                                    },
                                                    {
                                                        "value": "flats",
                                                        "label": "Flats",
                                                    },
                                                    {
                                                        "value": "terrenos_e_lotes_comerciais",
                                                        "label": "Terreno/Lote comercial",
                                                    },
                                                    {
                                                        "value": "terrenos_lotes_e_condominios",
                                                        "label": "Terreno/Lote condomínio",
                                                    },
                                                ],
                                                clearable=True,
                                                placeholder="Informe o tipo de imóvel",
                                                icon=DashIconify(
                                                    icon="ph:city",
                                                    width=20,
                                                ),
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.NumberInput(
                                                id="input-area",
                                                placeholder="Deixe vazio ou insira o valor da área",
                                                icon=DashIconify(
                                                    icon="gis:measure-area-alt",
                                                    width=20,
                                                ),
                                                thousandsSeparator=".",
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.NumberInput(
                                                id="input-price-alug",
                                                placeholder="Deixe vazio ou insira o valor do preço médio de aluguel",
                                                icon=DashIconify(
                                                    icon="material-symbols-light:house-outline",
                                                    width=20,
                                                ),
                                                thousandsSeparator=".",
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.NumberInput(
                                                id="input-area-alug",
                                                placeholder="Deixe vazio ou insira o valor da área média de aluguel",
                                                icon=DashIconify(
                                                    icon="mingcute:text-area-line",
                                                    width=20,
                                                ),
                                                thousandsSeparator=".",
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.NumberInput(
                                                id="input-bedrooms",
                                                placeholder="Deixe vazio ou insira a quantidade de quartos",
                                                icon=DashIconify(
                                                    icon="game-icons:bed",
                                                    width=20,
                                                ),
                                                thousandsSeparator=".",
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.NumberInput(
                                                id="input-bathrooms",
                                                placeholder="Deixe vazio ou insira a quantidade de banheiros",
                                                icon=DashIconify(
                                                    icon="iconoir:bathroom",
                                                    width=20,
                                                ),
                                                thousandsSeparator=".",
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.NumberInput(
                                                id="input-parking",
                                                placeholder="Deixe vazio ou insira a quantidade de vagas de garagem",
                                                icon=DashIconify(
                                                    icon="arcticons:car-parking",
                                                    width=20,
                                                ),
                                                thousandsSeparator=".",
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.Select(
                                                id="input-portaria",
                                                data=[
                                                    {"value": 1, "label": "Sim"},
                                                    {"value": 0, "label": "Não"},
                                                    {
                                                        "value": None,
                                                        "label": "Sem informação de portaria 24 horas",
                                                    },
                                                ],
                                                clearable=True,
                                                placeholder="Informe se o imóvel possui portaria 24 horas",
                                                icon=DashIconify(
                                                    icon="material-symbols-light:concierge-outline-rounded",
                                                    width=20,
                                                ),
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.Select(
                                                id="input-gym",
                                                data=[
                                                    {"value": 1, "label": "Sim"},
                                                    {"value": 0, "label": "Não"},
                                                    {
                                                        "value": None,
                                                        "label": "Sem informação de academia",
                                                    },
                                                ],
                                                clearable=True,
                                                placeholder="Informe se o imóvel possuí academia",
                                                icon=DashIconify(
                                                    icon="iconoir:gym",
                                                    width=20,
                                                ),
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.Select(
                                                id="input-elevator",
                                                data=[
                                                    {"value": 1, "label": "Sim"},
                                                    {"value": 0, "label": "Não"},
                                                    {
                                                        "value": None,
                                                        "label": "Sem informação de elevador",
                                                    },
                                                ],
                                                clearable=True,
                                                placeholder="Informe se o imóvel possui elevador",
                                                icon=DashIconify(
                                                    icon="material-symbols-light:elevator-outline-rounded",
                                                    width=20,
                                                ),
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.Select(
                                                data=[
                                                    {"value": 1, "label": "Sim"},
                                                    {"value": 0, "label": "Não"},
                                                    {
                                                        "value": None,
                                                        "label": "Sem informação de espaço gourmet",
                                                    },
                                                ],
                                                clearable=True,
                                                id="input-gourmet",
                                                placeholder="Informe se o imóvel possui espaço gourmet",
                                                icon=DashIconify(
                                                    icon="lucide-lab:chairs-table-platter",
                                                    width=20,
                                                ),
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.Select(
                                                id="input-pool",
                                                data=[
                                                    {"value": 1, "label": "Sim"},
                                                    {"value": 0, "label": "Não"},
                                                    {
                                                        "value": None,
                                                        "label": "Sem informação de piscina",
                                                    },
                                                ],
                                                clearable=True,
                                                placeholder="Informe se o imóvel possui piscina",
                                                icon=DashIconify(
                                                    icon="streamline:pool-ladder",
                                                    width=20,
                                                ),
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.Select(
                                                id="input-playground",
                                                data=[
                                                    {"value": 1, "label": "Sim"},
                                                    {"value": 0, "label": "Não"},
                                                    {
                                                        "value": None,
                                                        "label": "Sem informação playground",
                                                    },
                                                ],
                                                clearable=True,
                                                placeholder="Informe se o imóvel possui playground",
                                                icon=DashIconify(
                                                    icon="fluent-emoji-high-contrast:playground-slide",
                                                    width=20,
                                                ),
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.Select(
                                                id="input-sport",
                                                data=[
                                                    {"value": 1, "label": "Sim"},
                                                    {"value": 0, "label": "Não"},
                                                    {
                                                        "value": None,
                                                        "label": "Sem informação quadra de esporte",
                                                    },
                                                ],
                                                clearable=True,
                                                placeholder="Informe se o imóvel possui quadra de esporte",
                                                icon=DashIconify(
                                                    icon="icon-park-outline:sport",
                                                    width=20,
                                                ),
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.Select(
                                                id="input-party",
                                                data=[
                                                    {"value": 1, "label": "Sim"},
                                                    {"value": 0, "label": "Não"},
                                                    {
                                                        "value": None,
                                                        "label": "Sem informação salão de festa",
                                                    },
                                                ],
                                                clearable=True,
                                                placeholder="Informe se o imóvel possui salão de festa",
                                                icon=DashIconify(
                                                    icon="streamline:champagne-party-alcohol",
                                                    width=20,
                                                ),
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.Select(
                                                id="input-sauna",
                                                data=[
                                                    {"value": 1, "label": "Sim"},
                                                    {"value": 0, "label": "Não"},
                                                    {
                                                        "value": None,
                                                        "label": "Sem informação de sauna",
                                                    },
                                                ],
                                                clearable=True,
                                                placeholder="Informe se o imóvel possui sauna",
                                                icon=DashIconify(
                                                    icon="fluent-emoji-high-contrast:person-in-steamy-room",
                                                    width=20,
                                                ),
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.Select(
                                                id="input-spa",
                                                data=[
                                                    {"value": 1, "label": "Sim"},
                                                    {"value": 0, "label": "Não"},
                                                    {
                                                        "value": None,
                                                        "label": "Sem informação de spa",
                                                    },
                                                ],
                                                clearable=True,
                                                placeholder="Informe se o imóvel possui spa",
                                                icon=DashIconify(
                                                    icon="map:spa",
                                                    width=20,
                                                ),
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.Select(
                                                id="input-gourmet-varan",
                                                data=[
                                                    {"value": 1, "label": "Sim"},
                                                    {"value": 0, "label": "Não"},
                                                    {
                                                        "value": None,
                                                        "label": "Sem informação varanda gourmet",
                                                    },
                                                ],
                                                clearable=True,
                                                placeholder="Informe se o imóvel possui varanda gourmet",
                                                icon=DashIconify(
                                                    icon="ic:outline-outdoor-grill",
                                                    width=20,
                                                ),
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.Select(
                                                id="input-service",
                                                data=[
                                                    {"value": 1, "label": "Sim"},
                                                    {"value": 0, "label": "Não"},
                                                    {
                                                        "value": None,
                                                        "label": "Sem informação de área de serviço",
                                                    },
                                                ],
                                                clearable=True,
                                                placeholder="Informe se o imóvel possui área de serviço",
                                                icon=DashIconify(
                                                    icon="material-symbols-light:service-toolbox-outline-sharp",
                                                    width=20,
                                                ),
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.NumberInput(
                                                id="input-lat",
                                                precision=10,
                                                decimalSeparator=",",
                                                placeholder="Insira a latitude ou selecione diretamente do mapa",
                                                icon=DashIconify(
                                                    icon="mingcute:earth-latitude-line",
                                                    width=20,
                                                ),
                                                thousandsSeparator=".",
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.NumberInput(
                                                id="input-lon",
                                                precision=10,
                                                decimalSeparator=",",
                                                placeholder="Insira a longitude ou selecione diretamente do mapa",
                                                icon=DashIconify(
                                                    icon="mingcute:earth-longitude-line",
                                                    width=20,
                                                ),
                                                thousandsSeparator=".",
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.Button(
                                                "Calcular Previsão",
                                                id="calculate-prediction",
                                            ),
                                            html.Div(
                                                id="prediction-result",
                                                style={
                                                    "marginTop": "10px",
                                                    "fontSize": "18px",
                                                    "color": "green",
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                        withBorder=True,
                        shadow="sm",
                        radius="md",
                        style={"padding": "10px"},
                    ),
                    width=6,
                ),
            ]
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    dmc.Card(
                        children=[
                            dcc.Graph(
                                id="density-plot",
                                style={"height": "400px", "width": "100%"},
                                config={
                                    "displaylogo": False,
                                    "scrollZoom": False,
                                    "displayModeBar": False,
                                    "doubleClick": "reset",
                                    "modeBarButtonsToRemove": [
                                        "zoom",
                                        "zoomIn",
                                        "zoomOut",
                                        "pan",
                                        "lasso2d",
                                        "autoScale",
                                    ],
                                },
                            )
                        ],
                        withBorder=True,
                        shadow="sm",
                        radius="md",
                        style={"padding": "10px"},
                    ),
                    width=6,
                ),
                dbc.Col(
                    dmc.Card(
                        children=[
                            dcc.Graph(
                                id="bar-plot-most-expensive",
                                style={"height": "400px", "width": "100%"},
                                config={
                                    "displaylogo": False,
                                    "scrollZoom": False,
                                    "displayModeBar": False,
                                    "doubleClick": "reset",
                                    "modeBarButtonsToRemove": [
                                        "zoom",
                                        "zoomIn",
                                        "zoomOut",
                                        "pan",
                                        "lasso2d",
                                        "autoScale",
                                    ],
                                },
                            ),
                        ],
                        withBorder=True,
                        shadow="sm",
                        radius="md",
                        style={"padding": "10px"},
                    ),
                    width=6,
                ),
            ]
        ),
    ],
)


clientside_callback(
    ClientsideFunction(
        namespace="clientside_barplot_up_left", function_name="make_barplot_up_left"
    ),
    Output("bar-graph", "figure"),
    Input("filtered-data", "data"),
    Input("bar-graph", "selectedData"),
)


clientside_callback(
    ClientsideFunction(
        namespace="clientside_barplot_bottom_right",
        function_name="make_barplot_bottom_right",
    ),
    Output("bar-plot-most-expensive", "figure"),
    Input("filtered-data", "data"),
    Input("bar-plot-most-expensive", "selectedData"),
)


clientside_callback(
    ClientsideFunction(
        namespace="clientside_density", function_name="make_density_plot"
    ),
    Output("density-plot", "figure"),
    Input("filtered-data", "data"),
    Input("density-plot", "selectedData"),
)


@callback(
    Output("download-dataframe-csv", "data"),
    Input("download-btn", "n_clicks"),
    prevent_initial_call=True,
)
def download_csv(_):
    return dcc.send_data_frame(df_realestate.to_csv, "dados_imoveis.csv", index=False)


clientside_callback(
    ClientsideFunction(namespace="clientside_update_map", function_name="update_map"),
    Output("plotly-map-container", "figure"),
    Output("input-price-alug", "value"),
    Output("input-area-alug", "value"),
    Output("input-lat", "value"),
    Output("input-lon", "value"),
    Output("leaflet-map-container", "children"),
    Input("map-select", "value"),
    Input("filtered-data", "data"),
    Input("filtered-data-all", "data"),
    Input("predict-button", "n_clicks"),
    Input("plotly-map-container", "selectedData"),
    State("bairro-geojson", "data"),
    State("faixas_exclusivas-geojson", "data"),
    State("ciclo-geojson", "data"),
    State("comunidades-geojson", "data"),
    State("corredores-geojson", "data"),
    State("parques-geojson", "data"),
    State("rios-geojson", "data"),
    State("pracas-geojson", "data"),
    State("escolas_publicas-geojson", "data"),
)


@callback(
    Output("offcanvas-table", "is_open"),
    [Input("open-offcanvas-table-btn", "n_clicks")],
    prevent_initial_call=True,
)
def toggle_offcanvas_table(_):
    return True


@callback(
    Output("offcanvas", "is_open"),
    [
        Input("open-offcanvas-btn", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def toggle_offcanvas(_):
    return True


@callback(
    [Output("prediction-form", "style"), Output("show-prediction-form", "data")],
    [Input("predict-button", "n_clicks")],
    [State("show-prediction-form", "data")],
)
def toggle_prediction_form(n_clicks, is_visible):
    if n_clicks % 2 == 1:
        return {"display": "block"}, True
    else:
        return {"display": "none"}, False


clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="filter_data"),
    Output("filtered-data", "data"),
    Input("bar-graph", "selectedData"),
    Input("bar-plot-most-expensive", "selectedData"),
    Input("density-plot", "selectedData"),
    Input("map-select", "value"),
    Input("plotly-map-container", "selectedData"),
    State("filtered-data-all", "data"),
    prevent_initial_call=True,
)


@callback(
    Output("prediction-result", "children"),
    Input("calculate-prediction", "n_clicks"),
    State("input-area", "value"),
    State("input-price-alug", "value"),
    State("input-area-alug", "value"),
    State("input-bedrooms", "value"),
    State("input-bathrooms", "value"),
    State("input-parking", "value"),
    State("input-gym", "value"),
    State("input-elevator", "value"),
    State("input-gourmet", "value"),
    State("input-pool", "value"),
    State("input-playground", "value"),
    State("input-sport", "value"),
    State("input-party", "value"),
    State("input-sauna", "value"),
    State("input-spa", "value"),
    State("input-gourmet-varan", "value"),
    State("input-service", "value"),
    State("input-lat", "value"),
    State("input-lon", "value"),
    State("input-tipo", "value"),
    State("input-portaria", "value"),
)
def get_inputs_to_predict(
    n_clicks,
    area,
    price_alug,
    area_alug,
    bedrooms,
    bathrooms,
    parking,
    gym,
    elevator,
    space_gourmet,
    pool,
    playground,
    sport,
    party,
    sauna,
    spa,
    gourmet_varan,
    service,
    lat,
    lon,
    tipo,
    portaria,
):
    if n_clicks:
        payload = {
            "academia": gym,
            "area": area,
            "area_servico": service,
            "banheiro": bathrooms,
            "elevador": elevator,
            "espaco_gourmet": space_gourmet,
            "portaria_24_horas": portaria,
            "piscina": pool,
            "playground": playground,
            "quadra_de_esporte": sport,
            "quarto": bedrooms,
            "salao_de_festa": party,
            "sauna": sauna,
            "spa": spa,
            "tipo": tipo if tipo is not None else "apartamentos",
            "vaga": parking,
            "varanda_gourmet": gourmet_varan,
            "latitude": lat if lat != "" else None,
            "longitude": lon if lon != "" else None,
            "area_aluguel": area_alug if area_alug != "" else None,
            "valor_aluguel": price_alug if price_alug != "" else None,
        }

        return predict_house_price(payload)
