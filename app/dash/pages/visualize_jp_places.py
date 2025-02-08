import geopandas as gpd
import folium
import dash
import dash_bootstrap_components as dbc
import math
import os

from folium.plugins import MarkerCluster
from dash import html, callback, Input, Output, ctx, dcc, ALL

dash.register_page(__name__, name="Locais importantes", path="/locals")


def get_available_datasets():
    city_folder = "app/dash/assets/geo_joao_pessoa"
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

    city_folder = f"app/dash/assets/geo_joao_pessoa/{map_type}.geojson"
    geo_data = gpd.read_file(city_folder)

    if map_type == "escolas_publicas":
        marker_cluster = MarkerCluster().add_to(m)
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
    elif map_type == "bairros":
        for _, row in geo_data.iterrows():
            popup_content = f"""
            <b>Bairro:</b> {row['nome']}<br>
            <b>Perímetro:</b> {row['perimetro']:.2f} m<br>
            <b>Área:</b> {row['area']:.2f} m²<br>
            <b>Hectares:</b> {row['hectares']:.2f} ha<br>
            """
            folium.GeoJson(
                row.geometry,
                name=row["nome"],
                popup=folium.Popup(popup_content, max_width=300),
            ).add_to(m)
    elif map_type == "rios":
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
    elif map_type == "pracas":
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
    elif map_type == "parques":
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
    elif map_type == "faixas_exclusivas":
        for _, row in geo_data.iterrows():
            popup_content = f"""
            <b>Ano de implantação :</b> {row['ano_implantacao']} <br>
            <b>Percurso :</b> {row['percurso']} <br>
            """
            folium.GeoJson(
                row.geometry,
                name=row["percurso"],
                popup=folium.Popup(popup_content, max_width=300),
            ).add_to(m)
    elif map_type == "comunidades":
        for _, row in geo_data.iterrows():
            popup_content = f"""
            <b>Comunidade :</b> {row['comunidade']} <br>
            <b>Área :</b> {row['area']:.2f} m²<br>
            """
            folium.GeoJson(
                row.geometry,
                name=row["comunidade"],
                popup=folium.Popup(popup_content, max_width=300),
            ).add_to(m)
    elif map_type == "corredores":
        for _, row in geo_data.iterrows():
            popup_content = f"""
            <b>Corredor :</b> {row['corredor']} <br>
            <b>Descrição :</b> {row['descricao']} <br>
            """
            folium.GeoJson(
                row.geometry,
                name=row["descricao"],
                popup=folium.Popup(popup_content, max_width=300),
            ).add_to(m)
    elif map_type == "ciclo":
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
