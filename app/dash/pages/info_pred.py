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
import plotly.figure_factory as ff
import httpx
import asyncio

from dash_iconify import DashIconify
from dash import html, Output, Input, dcc, callback, State
from folium.plugins import HeatMap

dash.register_page(__name__, name="Análise de imóveis", path="/realestate")


# async def fetch_data():
#     async with httpx.AsyncClient() as client:
#         response = await client.get("http://api/real_data/return_data_db")
#         return response.json()


# df_realestate = pd.DataFrame(asyncio.run(fetch_data())).assign(
#     tipo=lambda x: x.tipo.str.capitalize()
#     .str.split("_")
#     .str.join(" ")
#     .str.replace("condominio", "condomínio")
# )

df_realestate = pd.read_csv("data/cleaned/jp_limpo_bairro_correto.csv").assign(
    Tipo=lambda x: x.Tipo.str.capitalize()
    .str.split("_")
    .str.join(" ")
    .str.replace("condominio", "condomínio")
)

center_lat = df_realestate["Latitude"].mean()
center_lon = df_realestate["Longitude"].mean()


fig_bar = px.bar(
    df_realestate.groupby("Tipo")["Valor"].mean().sort_values().reset_index(),
    x="Valor",
    y="Tipo",
    labels={"Tipo": "", "Valor": "Valor Médio (R$)"},
    text_auto=".2s",
    template="plotly_white",
)

fig_bar.update_layout(
    clickmode="event+select",
    dragmode="select",
    template="plotly_white",
    margin=dict(l=0, r=0, t=0, b=0),
)

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
                                figure=fig_bar,
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
                            html.Div(id="map-container"),
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
                                        variant="subtle",
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
                                title="Informações Adicionais",
                                is_open=False,
                                style={"width": ""},
                                placement="end",
                                children=[
                                    html.P(
                                        "Aqui você pode colocar informações adicionais, filtros, etc."
                                    ),
                                    html.Hr(),
                                    dmc.Select(
                                        label="Tipo de Mapa",
                                        placeholder="Selecione o tipo de mapa",
                                        id="map-select",
                                        value="heatmap",
                                        data=[
                                            {"value": "leaflet", "label": "Sem tipo"},
                                            {
                                                "value": "heatmap",
                                                "label": "Mapa de Calor",
                                            },
                                            {
                                                "value": "markers",
                                                "label": "Mapa de pontos",
                                            },
                                            {"value": "rios", "label": "Rios"},
                                            {"value": "ciclo", "label": "Ciclo"},
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
                                            html.H4(
                                                "Preencha as informações do imóvel"
                                            ),
                                            dmc.NumberInput(
                                                id="input-area",
                                                placeholder="Insira o valor da área",
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
                                                placeholder="Insira o valor do preço médio de aluguel",
                                                icon=DashIconify(
                                                    icon="gis:measure-area-alt",
                                                    width=20,
                                                ),
                                                thousandsSeparator=".",
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.NumberInput(
                                                id="input-area-alug",
                                                placeholder="Insira o valor da área média de aluguel",
                                                icon=DashIconify(
                                                    icon="gis:measure-area-alt",
                                                    width=20,
                                                ),
                                                thousandsSeparator=".",
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.NumberInput(
                                                id="input-bedrooms",
                                                placeholder="Insira a quantidade de quartos",
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
                                                placeholder="Insira a quantidade de banheiros",
                                                icon=DashIconify(
                                                    icon="iconoir:bathroom",
                                                    width=20,
                                                ),
                                                thousandsSeparator=".",
                                                w=390,
                                                mb=10,
                                            ),
                                            dmc.Select(
                                                id="input-parking",
                                                data=[
                                                    {"value": 1, "label": "Sim"},
                                                    {"value": 0, "label": "Não"},
                                                    {
                                                        "value": None,
                                                        "label": "Sem informação",
                                                    },
                                                ],
                                                rightSection=DashIconify(
                                                    icon="radix-icons:chevron-down"
                                                ),
                                                placeholder="Insira a quantidade de vagas de garagem",
                                                icon=DashIconify(
                                                    icon="arcticons:car-parking",
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
                                                        "label": "Sem informação",
                                                    },
                                                ],
                                                rightSection=DashIconify(
                                                    icon="radix-icons:chevron-down"
                                                ),
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
                                                        "label": "Sem informação",
                                                    },
                                                ],
                                                rightSection=DashIconify(
                                                    icon="radix-icons:chevron-down"
                                                ),
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
                                                        "label": "Sem informação",
                                                    },
                                                ],
                                                rightSection=DashIconify(
                                                    icon="radix-icons:chevron-down"
                                                ),
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
                                                        "label": "Sem informação",
                                                    },
                                                ],
                                                rightSection=DashIconify(
                                                    icon="radix-icons:chevron-down"
                                                ),
                                                placeholder="Informe se o imóvel possui piscina",
                                                icon=DashIconify(
                                                    icon="lucide-lab:chairs-table-platter",
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
                                                        "label": "Sem informação",
                                                    },
                                                ],
                                                rightSection=DashIconify(
                                                    icon="radix-icons:chevron-down"
                                                ),
                                                placeholder="Informe se o imóvel possui playground",
                                                icon=DashIconify(
                                                    icon="lucide-lab:chairs-table-platter",
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
                                                        "label": "Sem informação",
                                                    },
                                                ],
                                                rightSection=DashIconify(
                                                    icon="radix-icons:chevron-down"
                                                ),
                                                placeholder="Informe se o imóvel possui quadra de esporte",
                                                icon=DashIconify(
                                                    icon="lucide-lab:chairs-table-platter",
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
                                                        "label": "Sem informação",
                                                    },
                                                ],
                                                rightSection=DashIconify(
                                                    icon="radix-icons:chevron-down"
                                                ),
                                                placeholder="Informe se o imóvel possui salão de festa",
                                                icon=DashIconify(
                                                    icon="lucide-lab:chairs-table-platter",
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
                                                        "label": "Sem informação",
                                                    },
                                                ],
                                                rightSection=DashIconify(
                                                    icon="radix-icons:chevron-down"
                                                ),
                                                placeholder="Informe se o imóvel possui sauna",
                                                icon=DashIconify(
                                                    icon="lucide-lab:chairs-table-platter",
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
                                                        "label": "Sem informação",
                                                    },
                                                ],
                                                rightSection=DashIconify(
                                                    icon="radix-icons:chevron-down"
                                                ),
                                                placeholder="Informe se o imóvel possui spa",
                                                icon=DashIconify(
                                                    icon="lucide-lab:chairs-table-platter",
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
                                                        "label": "Sem informação",
                                                    },
                                                ],
                                                placeholder="Informe se o imóvel possui varanda gourmet",
                                                icon=DashIconify(
                                                    icon="lucide-lab:chairs-table-platter",
                                                    width=20,
                                                ),
                                                rightSection=DashIconify(
                                                    icon="radix-icons:chevron-down"
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
                                                        "label": "Sem informação",
                                                    },
                                                ],
                                                placeholder="Informe se o imóvel possui área de serviço",
                                                icon=DashIconify(
                                                    icon="material-symbols-light:service-toolbox-outline-sharp",
                                                    width=20,
                                                ),
                                                rightSection=DashIconify(
                                                    icon="radix-icons:chevron-down"
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
                                                className="btn btn-success",
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


@callback(Output("bar-plot-most-expensive", "figure"), Input("filtered-data", "data"))
def make_barplot(filtered_data):
    df_filtered = pd.DataFrame(filtered_data)

    fig_bar = px.bar(
        df_filtered.groupby("Bairro")["Valor"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
        .reset_index(),
        x="Valor",
        y="Bairro",
        labels={"Tipo": "", "Valor": "Valor Médio (R$)"},
        text_auto=".2s",
        template="plotly_white",
    )

    fig_bar.update_layout(
        clickmode="event+select",
        dragmode="select",
        template="plotly_white",
        margin=dict(l=0, r=0, t=0, b=0),
        yaxis=dict(tickformat=".2f"),
    )

    return fig_bar


@callback(Output("density-plot", "figure"), Input("filtered-data", "data"))
def make_density_plot(filtered_data):
    df_filtered = pd.DataFrame(filtered_data)

    types_imo = df_filtered.Tipo.unique()

    get_groups = [df_filtered.query("Tipo == @i").Valor for i in types_imo]

    fig = ff.create_distplot(get_groups, types_imo, bin_size=10000, show_rug=False)

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        clickmode="event+select",
        dragmode="select",
        template="plotly_white",
    )

    return fig


@callback(
    Output("download-dataframe-csv", "data"),
    Input("download-btn", "n_clicks"),
    prevent_initial_call=True,
)
def download_csv(_):
    return dcc.send_data_frame(df_realestate.to_csv, "dados_imoveis.csv", index=False)


@callback(
    Output("map-container", "children"),
    [
        Input("map-select", "value"),
        Input("filtered-data", "data"),
        Input("predict-button", "n_clicks"),
    ],
)
def update_map(map_type, filtered_data, n_clicks):
    df_filtered = pd.DataFrame(filtered_data)

    city_folder = f"app/dash/assets/geo_joao_pessoa/{map_type}.geojson"
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_control=True,
        attribution_control=True,
        zoom_start=12,
    )

    if n_clicks % 2 == 1:
        map_type = None

    if map_type == "heatmap":
        data = df_filtered[["Latitude", "Longitude", "Valor"]].values.tolist()
        heatmap_map = folium.Map([center_lat, center_lon], zoom_start=12)
        HeatMap(data, radius=13).add_to(heatmap_map)
        return html.Iframe(
            srcDoc=heatmap_map._repr_html_(), width="100%", height="400px"
        )

    elif map_type == "markers":
        fig_map_marker = px.scatter_mapbox(
            df_filtered,
            lat="Latitude",
            lon="Longitude",
            color="Valor",
            size="Valor",
            hover_name="Tipo",
            hover_data={"Latitude": False, "Longitude": False, "Valor": ":.2f"},
            color_continuous_scale="Viridis",
            size_max=15,
            zoom=12,
            mapbox_style="open-street-map",
            center={
                "lat": center_lat,
                "lon": center_lon,
                # "lat": df_filtered["Latitude"].mean(),
                # "lon": df_filtered["Longitude"].mean(),
            },
        )

        fig_map_marker.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            clickmode="event+select",
            dragmode="select",
            coloraxis_colorbar=dict(
                title="Valor (R$)",
                orientation="h",
                tickformat=".2s",
                x=0,
                xanchor="left",
                y=0.85,
                yanchor="bottom",
                len=0.6,
                thickness=15,
                title_font=dict(size=12),
            ),
        )
        return dcc.Graph(
            figure=fig_map_marker,
            style={"width": "100%", "height": "400px"},
            config={"displaylogo": False},
        )
    elif map_type == "ciclo":
        geo_data = gpd.read_file(city_folder)
        for _, row in geo_data.astype({"ano_implantacao": int}).iterrows():
            popup_content = f"""
            <b>Tipo :</b> {row['tipo']} <br>
            <b>Sentido :</b> {row['sentido']} <br>
            <b>Ano de implantação :</b> {row['ano_implantacao']} <br>
            """
            folium.GeoJson(
                row.geometry,
                name=row["ano_implantacao"],
                popup=folium.Popup(popup_content, max_width=300),
            ).add_to(m)
        return html.Iframe(srcDoc=m._repr_html_(), width="100%", height="400px")

    elif map_type == "parques":
        geo_data = gpd.read_file(city_folder)
        for _, row in geo_data.iterrows():
            popup_content = f"""
            <b>Nome :</b> {row['nome']} <br>
            <b>Perímetro :</b> {row['perimetro']:.2f} m<br>
            <b>Área :</b> {row['area']:.2f} m²<br>
            <b>Hectares :</b> {row['hectares']:.2f} ha<br>
            """
            folium.GeoJson(
                row.geometry,
                name=row["nome"],
                popup=folium.Popup(popup_content, max_width=300),
            ).add_to(m)

        return html.Iframe(srcDoc=m._repr_html_(), width="100%", height="400px")

    elif map_type == "escolas_publicas":
        geo_data = gpd.read_file(city_folder)
        marker_cluster = folium.plugins.MarkerCluster().add_to(m)
        for _, row in geo_data.iterrows():
            popup_content = f"""
            <b>Nome:</b> {row['nome']}<br>
            <b>Categoria:</b> {row['categoria']}<br>
            <b>Dependência:</b> {row['dependencia']}
            """
            folium.Marker(
                location=[row.geometry.y, row.geometry.x],
                popup=folium.Popup(popup_content, max_width=300),
            ).add_to(marker_cluster)

        return html.Iframe(srcDoc=m._repr_html_(), width="100%", height="400px")

    elif map_type == "rios":

        geo_data = gpd.read_file(city_folder)
        for _, row in geo_data.iterrows():
            popup_content = f"""
            <b>Nome :</b> {row['nome']} <br>
            <b>Tipo :</b> {row['tipo']} <br>
            <b>Afluente :</b> {row['afluente']} <br>
            """
            folium.GeoJson(
                row.geometry,
                name=row["nome"],
                popup=folium.Popup(popup_content, max_width=300),
            ).add_to(m)

        return html.Iframe(srcDoc=m._repr_html_(), width="100%", height="400px")

    elif map_type == "pracas":
        geo_data = gpd.read_file(city_folder)
        geo_data["area"] = geo_data["area"].str.replace(",", ".").astype(float)
        for _, row in geo_data.iterrows():
            area_value = f"{row['area']:.2f}" if not math.isnan(row["area"]) else "N/A"
            popup_content = f"""
            <b>Bairro :</b> {row['bairro']} <br>
            <b>Nome :</b> {row['nome']} <br>
            <b>Área :</b> {area_value} <br>
            """
            folium.GeoJson(
                row.geometry,
                name=row["nome"],
                popup=folium.Popup(popup_content, max_width=300),
            ).add_to(m)

        return html.Iframe(srcDoc=m._repr_html_(), width="100%", height="400px")

    else:
        return dl.Map(
            id="map-id",
            style={"width": "100%", "height": "400px"},
            center=[center_lat, center_lon],
            zoom=12,
            children=[
                dl.TileLayer(),
                dl.LayerGroup(id="points-layer"),
            ],
        )


@callback(
    [
        Output("points-layer", "children"),
        Output("input-lat", "value"),
        Output("input-lon", "value"),
        Output("stored-coordinates", "data"),
    ],
    [Input("map-id", "clickData")],
)
def update_coordinates(clickData):
    if clickData and "latlng" in clickData:
        lat, lon = clickData["latlng"]["lat"], clickData["latlng"]["lng"]
        marker = dl.CircleMarker(
            center=[lat, lon],
            radius=6,
            color="red",
            fill=True,
            fillColor="red",
            fillOpacity=0.8,
            children=dl.Tooltip(f"Latitude: {lat:.6f}, Longitude: {lon:.6f}"),
        )
        return [marker], lat, lon, clickData
    return [], "", "", None


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


@callback(
    Output("filtered-data", "data"),
    Input("bar-graph", "selectedData"),
)
def filter_data(selectedData):
    print(f"selectedData: {selectedData}")

    if selectedData and "points" in selectedData:
        selected_types = {point["y"] for point in selectedData["points"]}
        print(f"Selected Types: {selected_types}")

        filtered_df = df_realestate[df_realestate["Tipo"].isin(selected_types)]
        return filtered_df.to_dict("records")

    return df_realestate.to_dict("records")
