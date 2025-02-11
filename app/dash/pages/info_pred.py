# import requests
import pandas as pd
import dash
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html, Output, Input, dcc, callback
from dash_iconify import DashIconify

dash.register_page(__name__, name="Análise de imóveis", path="/realestate")

df_realestate = pd.read_csv("data/cleaned/jp_limpo.csv")
# df_realestate = pd.DataFrame(
#     requests.get("http://api:8050/real_data/return_data_db").json()
# )

center_lat = df_realestate["latitude"].mean()
center_lon = df_realestate["longitude"].mean()

layout = html.Div(
    [
        dl.Map(
            id="map-id",
            style={"width": "100%", "height": "600px"},
            center=[center_lat, center_lon],
            zoom=12,
            children=[
                dl.TileLayer(),
                dl.LayerGroup(id="points-layer"),
            ],
        ),
        dcc.Store(id="stored-coordinates"),
        html.P("Clique no mapa para obter as coordenadas:"),
        html.Div(id="coordinate-click-id", style={"fontSize": "18px", "color": "blue"}),

        html.Div(
            dmc.ActionIcon(
                DashIconify(icon="clarity:settings-line", width=25),
                color="blue",
                size="xl",
                variant="outline",
                id="open-offcanvas-btn",
                n_clicks=0,
            ),
            style={
                "position": "fixed",
                "bottom": "20px",
                "right": "20px",
                "zIndex": "1000",
            },
        ),

        dbc.Offcanvas(
            id="offcanvas",
            title="Informações Adicionais",
            is_open=False,
            placement="end",
            children=[
                html.P("Aqui você pode colocar informações adicionais, filtros, etc."),
                html.Hr(),
                html.P("Coordenadas clicadas:"),
                html.Div(id="offcanvas-coordinates"),
            ],
        ),
    ]
)


@callback(
    [
        Output("points-layer", "children"),
        Output("coordinate-click-id", "children"),
        Output("stored-coordinates", "data"),
        Output("offcanvas-coordinates", "children"),
    ],
    [Input("map-id", "clickData")],
    prevent_initial_call=True
)
def update_map(clickData):
    points = []
    # points = [
    #     dl.CircleMarker(
    #         center=[row["latitude"], row["longitude"]],
    #         radius=4,
    #         color="blue",
    #         fill=True,
    #         fillColor="blue",
    #         fillOpacity=0.7,
    #         children=dl.Tooltip(f"{row['bairro']}: R$ {row['valor']:,.2f}")
    #     )
    #     for _, row in df_realestate.iterrows()
    # ]

    if clickData and "latlng" in clickData:
        lat, lon = clickData["latlng"]["lat"], clickData["latlng"]["lng"]
        points.append(dl.CircleMarker(
            center=[lat, lon],
            radius=6,
            color="red",
            fill=True,
            fillColor="red",
            fillOpacity=0.8,
            children=dl.Tooltip(f"Coordenadas clicadas: {lat:.6f}, {lon:.6f}")
        ))
        coords_text = f"Latitude {lat:.6f}, Longitude {lon:.6f}"
        return points, f"Coordenadas clicadas: {coords_text}", clickData, coords_text

    return points, "Clique no mapa para obter as coordenadas.", None, "-"


@callback(
    Output("offcanvas", "is_open"),
    [Input("open-offcanvas-btn", "n_clicks")],
    prevent_initial_call=True
)
def toggle_offcanvas(n_clicks):
    return True
