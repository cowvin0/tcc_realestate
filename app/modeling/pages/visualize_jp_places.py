import geopandas as gpd
import folium
import dash
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output

dash.register_page(
    __name__,
    name='Localidades de João Pessoa',
    path='/locals'
)

sidebar = html.Div(
    [
        html.H2(
            "Localidades de JP",
            className="display-5",
            style={"font-weight": "bold"}),
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
                        id="btn-bairros",
                        color="light",
                        className="m-1",
                        style={"width": "100%"},
                    ), width=6),

                    dbc.Col(dbc.Button(
                        html.Span(dbc.Stack([
                            html.I(className="fas fa-leaf ml-2"),
                            " Praças"
                        ])),
                        id="btn-pracas",
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
                        id="btn-parques",
                        color="light",
                        className="m-1",
                        style={"width": "100%"},
                    ), width=6),

                    dbc.Col(dbc.Button(
                        html.Span(dbc.Stack([
                            html.I(className="fas fa-solid fa-water ml-2"),
                            " Rios"
                        ])),
                        id="btn-rios",
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
                        id="btn-ciclo",
                        color="light",
                        className="m-1",
                        style={"width": "100%"},
                    ), width=6),

                    dbc.Col(dbc.Button(
                        html.Span(dbc.Stack([
                            html.I(className="fas fa-solid fa-bus ml-2"),
                            " Faixas exclusivas"
                        ])),
                        id="btn-faixas_exclusivas",
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
                        id="btn-corredores",
                        color="light",
                        className="m-1",
                        style={"width": "100%"},
                    ), width=6),

                    dbc.Col(dbc.Button(
                        html.Span(dbc.Stack([
                            html.I(className="fas fa-solid fa-school ml-2"),
                            " Escolas públicas"
                        ])),
                        id="btn-escolas_publicas",
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
                        id="btn-comunidades",
                        color="light",
                        className="m-1",
                        style={"width": "100%"},
                    ), width=6),

                    dbc.Col(dbc.Button(
                        html.Span(dbc.Stack([
                            html.I(className="fas fa-sun ml-2"),
                            " Área rural"
                        ])),
                        id="btn-area_rural",
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


def generate_map(map_type):
    m = folium.Map(
      location=[-7.15, -34.85],
      zoom_control=True,
      attribution_control=False,
      zoom_start=12)

    geo_data = gpd.read_file(f"app/modeling/assets/{map_type}" + ".geojson")
    folium.GeoJson(geo_data, name="hello world").add_to(m)

    map_file = m.get_root().render()
    return map_file


map_component = html.Div(
    html.Iframe(
        id="map-iframe",
        srcDoc=generate_map('bairros'),
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


@callback(
    Output("map-iframe", "srcDoc"),
    [Input("btn-bairros", "n_clicks"),
     Input("btn-pracas", "n_clicks"),
     Input("btn-parques", "n_clicks"),
     Input("btn-area_rural", "n_clicks"),
     Input("btn-comunidades", "n_clicks"),
     Input("btn-ciclo", "n_clicks"),
     Input("btn-corredores", "n_clicks"),
     Input("btn-escolas_publicas", "n_clicks"),
     Input("btn-rios", "n_clicks"),
     Input("btn-faixas_exclusivas", "n_clicks")]
)
def update_map(
    n_bairros, n_pracas, n_parques,
    n_area_rural, n_comunidades,
    n_ciclo, n_corredores,
    n_escolas_publicas, n_rios,
    n_faixas_exclusivas):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = "bairros"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "btn-bairros":
        map_file = generate_map("bairros")
    elif button_id == "btn-pracas":
        map_file = generate_map("pracas")
    elif button_id == "btn-parques":
        map_file = generate_map("parques")
    elif button_id == "btn-area_rural":
        map_file = generate_map("area_rural")
    elif button_id == "btn-comunidades":
        map_file = generate_map("comunidades")
    elif button_id == "btn-ciclo":
        map_file = generate_map("ciclo")
    elif button_id == "btn-corredores":
        map_file = generate_map("corredores")
    elif button_id == "btn-escolas_publicas":
        map_file = generate_map("escolas_publicas")
    elif button_id == "btn-faixas_exclusivas":
        map_file = generate_map("faixas_exclusivas")
    elif button_id == "btn-rios":
        map_file = generate_map("rios")
    else:
        map_file = generate_map("bairros")

    return map_file
