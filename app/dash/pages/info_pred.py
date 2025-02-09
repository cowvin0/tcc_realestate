import json
import requests
import pandas as pd
import dash
import dash_leaflet as dl
from dash import html, dcc, Output, Input, callback

dash.register_page(__name__, name="Análise de imóveis", path="/realestate")

df_realestate = pd.DataFrame(
    requests.get("http://api:8050/real_data/return_data_db").json()
)


MAP_ID = "map-id"
COORDINATE_CLICK_ID = "coordinate-click-id"

layout = html.Div(
    [
        html.H1("Example: Gettings coordinates from click"),
        dl.Map(
            id=MAP_ID,
            style={"width": "1000px", "height": "500px"},
            center=[32.7, -96.8],
            zoom=5,
            children=[dl.TileLayer()],
        ),
        html.P("Coordinate (click on map):"),
        html.Div(id=COORDINATE_CLICK_ID),
    ]
)


@callback(Output(COORDINATE_CLICK_ID, "children"), [Input(MAP_ID, "clickData")])
def click_coord(e):
    if e is not None:
        return json.dumps(e)
    else:
        return "-"
