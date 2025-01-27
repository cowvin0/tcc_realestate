import geopandas as gpd
import folium
import dash
import dash_bootstrap_components as dbc
import os

from folium.plugins import MarkerCluster
from dash import html, callback, Input, Output, ctx, dcc, ALL

dash.register_page(__name__, name="Locais importantes", path="/locals")


def get_available_datasets():
    city_folder = "app/modeling/assets/geo_joao_pessoa"
    if not os.path.exists(city_folder):
        return []
    return [
        os.path.splitext(file)[0]
        for file in os.listdir(city_folder)
        if file.endswith(".geojson")
    ]


def generate_sidebar():
    datasets = get_available_datasets()
    buttons = []
    for dataset in datasets:
        label = dataset.replace("_", " ").capitalize()
        button_id = {"type": "dynamic-button", "dataset": dataset}
        buttons.append(
            dbc.Col(
                dbc.Button(
                    html.Span(
                        dbc.Stack(
                            [
                                html.I(className="fas fa-map-marker-alt ml-2"),
                                f" {label}",
                            ]
                        )
                    ),
                    id=button_id,
                    color="light",
                    className="m-1",
                    style={"width": "100%"},
                ),
                xs=12,
                sm=6,
            )
        )

    sidebar_content = [
        html.H2(
            "Pontos estratégicos", className="display-5", style={"font-weight": "bold"}
        ),
        html.P(
            "Veja dados geográficos de João Pessoa, como bairros, praças, "
            "parques, escolas, etc.",
            className="lead",
            style={"textAlign": "justify"},
        ),
        dbc.Row(buttons),
    ]

    return html.Div(
        sidebar_content,
        style={
            "padding": "20px",
            "background-color": "#f8f9fa",
            "height": "100vh",
            "width": "100%",
            "max-width": "300px",
            "position": "fixed",
            "left": 0,
            "top": "56px",
            "overflow-y": "auto",
        },
    )


def generate_map(map_type):
    m = folium.Map(
        location=[-7.15, -34.85],
        zoom_control=True,
        attribution_control=False,
        zoom_start=12,
    )

    city_folder = f"app/modeling/assets/geo_joao_pessoa/{map_type}.geojson"
    geo_data = gpd.read_file(city_folder)

    if map_type == "escolas_públicas":
        marker_cluster = MarkerCluster().add_to(m)
        for _, row in geo_data.iterrows():
            folium.Marker(
                location=[row.geometry.y, row.geometry.x],
            ).add_to(marker_cluster)
    else:
        folium.GeoJson(geo_data, name="geojson").add_to(m)

    map_file = m.get_root().render()
    return map_file


map_component = html.Div(
    dcc.Loading(
        id="loading-map",
        type="circle",
        children=html.Iframe(
            id="map-iframe",
            srcDoc=generate_map("bairros"),
            style={
                "height": "92.5vh",
                "width": "100%",
                "border": "none",
            },
        ),
    ),
    style={
        "position": "fixed",
        "top": "56px",
        "left": "300px",
        "right": 0,
    },
)


layout = html.Div(
    [
        html.Div(id="sidebar-container", children=generate_sidebar()),
        map_component,
        dcc.Store(id="map-config", data={"dataset": "bairros"}),
    ]
)


@callback(
    Output("map-config", "data"),
    Input({"type": "dynamic-button", "dataset": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def update_map_config(button_clicks):
    ctx_id = ctx.triggered_id

    if isinstance(ctx_id, dict) and ctx_id.get("type") == "dynamic-button":
        dataset = ctx_id["dataset"]
        return {"dataset": dataset}

    return dash.no_update


@callback(
    Output("map-iframe", "srcDoc"),
    Input("map-config", "data"),
)
def update_map(map_config):
    dataset = map_config["dataset"]
    return generate_map(dataset)
