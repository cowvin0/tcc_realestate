import requests
import pandas as pd
import dash
import dash_leaflet as dl
from dash import html, Output, Input, dcc, callback

dash.register_page(__name__, name="Análise de imóveis", path="/realestate")

# Fetch real estate data
df_realestate = pd.DataFrame(
    requests.get("http://api:8050/real_data/return_data_db").json()
)

# Calculate center of the map based on property locations
center_lat = df_realestate["latitude"].mean()
center_lon = df_realestate["longitude"].mean()

# Layout with map and coordinate display
layout = html.Div(
    [
        dl.Map(
            id="map-id",
            style={"width": "100%", "height": "600px"},
            center=[center_lat, center_lon],
            zoom=12,
            children=[
                dl.TileLayer(),
                dl.LayerGroup(id="points-layer"),  # Property points
            ],
        ),
        dcc.Store(id="stored-coordinates"),  # Hidden store for clicked coordinates
        html.P("Clique no mapa para obter as coordenadas:"),
        html.Div(id="coordinate-click-id", style={"fontSize": "18px", "color": "blue"}),
    ]
)


@callback(
    [
        Output("points-layer", "children"),
        Output("coordinate-click-id", "children"),
        Output("stored-coordinates", "data")
    ],
    [Input("map-id", "clickData")],
    prevent_initial_call=True
)
def update_map(clickData):
    points = [
        dl.CircleMarker(
            center=[row["latitude"], row["longitude"]],
            radius=4,
            color="blue",
            fill=True,
            fillColor="blue",
            fillOpacity=0.7,
            children=dl.Tooltip(f"{row['bairro']}: R$ {row['valor']:,.2f}")
        )
        for _, row in df_realestate.iterrows()
    ]

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
        return points, f"Coordenadas clicadas: Latitude {lat:.6f}, Longitude {lon:.6f}", clickData

    return points, "Clique no mapa para obter as coordenadas.", None
