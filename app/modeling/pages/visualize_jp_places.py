import geopandas as gpd
import folium
import dash
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(
    __name__,
    name='Localidades de João Pessoa',
    path='/locals'
)

sidebar = html.Div(
    [
        html.H2("Localidades de JP", className="display-5", style={"font-weight": "bold"}),
        html.P(
            "Veja dados geográficos da cidade de João Pessoa, "
            "como bairros, praças, parques, escolas, ciclovias etc.",
            className="lead",
            style={"textAlign": "justify"},
        ),
        html.Div(
            [
                dbc.Row([
                    dbc.Col(dbc.Button(
                        html.Span(dbc.Stack([
                            html.I(className="fas fa-solid fa-map ml-2"),
                            " Bairros"
                        ])),
                        color="light",
                        className="m-1",
                        style={"width": "100%"},
                    ), width=6),

                    dbc.Col(dbc.Button(
                        html.Span(dbc.Stack([
                            html.I(className="fas fa-leaf ml-2"),
                            " Praças"
                        ])),
                        color="light",
                        className="m-1",
                        style={"width": "100%"},
                    ), width=6),
                ]),

                dbc.Row([
                    dbc.Col(dbc.Button(
                        html.Span(dbc.Stack([
                            html.I(className="fas fa-solid fa-tree ml-2"),
                            " Parques"
                        ])),
                        color="light",
                        className="m-1",
                        style={"width": "100%"},
                    ), width=6),

                    dbc.Col(dbc.Button(
                        html.Span(dbc.Stack([
                            html.I(className="fas fa-solid fa-water ml-2"),
                            " Rios"
                        ])),
                        color="light",
                        className="m-1",
                        style={"width": "100%"},
                    ), width=6),
                ]),

                dbc.Row([
                    dbc.Col(dbc.Button(
                        html.Span(dbc.Stack([
                            html.I(className="fas fa-solid fa-bicycle ml-2"),
                            " Ciclovário"
                        ])),
                        color="light",
                        className="m-1",
                        style={"width": "100%"},
                    ), width=6),

                    dbc.Col(dbc.Button(
                        html.Span(dbc.Stack([
                            html.I(className="fas fa-solid fa-bus ml-2"),
                            " Faixas exclusivas"
                        ])),
                        color="light",
                        className="m-1",
                        style={"width": "100%"},
                    ), width=6),
                ]),

                dbc.Row([
                    dbc.Col(dbc.Button(
                        html.Span(dbc.Stack([
                            html.I(className="fas fa-solid fa-road ml-2"),
                            " Corredores"
                        ])),
                        color="light",
                        className="m-1",
                        style={"width": "100%"},
                    ), width=6),

                    dbc.Col(dbc.Button(
                        html.Span(dbc.Stack([
                            html.I(className="fas fa-solid fa-school ml-2"),
                            " Escolas públicas"
                        ])),
                        color="light",
                        className="m-1",
                        style={"width": "100%"},
                    ), width=6),
                ]),

                dbc.Row([
                    dbc.Col(dbc.Button(
                        html.Span(dbc.Stack([
                            html.I(className="fas fa-solid fa-home ml-2"),
                            " Comunidades"
                        ])),
                        color="light",
                        className="m-1",
                        style={"width": "100%"},
                    ), width=6),

                    dbc.Col(dbc.Button(
                        html.Span(dbc.Stack([
                            html.I(className="fas fa-sun ml-2"),
                            " Área rural"
                        ])),
                        color="light",
                        className="m-1",
                        style={"width": "100%"},
                    ), width=6),
                ]),
            ]
        ),
    ],
    style={
        "padding": "20px",
        "background-color": "#f8f9fa",
        "height": "100vh",
        "width": "20%",
        "position": "fixed",
        "left": 0,
        "top": "56px",
        "overflow-y": "auto",
    },
)

geo_data = gpd.read_file('https://raw.githubusercontent.com/paulovitorweb/geodata-jp/refs/heads/main/data/bairros.geojson')
map_folium = folium.Map(location=[-7.1195, -34.845], zoom_start=13)
folium.GeoJson(geo_data, name="hello world").add_to(map_folium)

map_component = html.Div(
    html.Iframe(
        srcDoc=map_folium.get_root().render(),
        style={
            "height": "92.5vh",
            "width": "80vw",
            "border": "none",
            },
    ),
    style={
        "position": "fixed",
        "top": "56px",
        "left": "20%"
        },
)

layout = [sidebar, map_component]
