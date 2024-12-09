import dash
import dash_bootstrap_components as dbc
import plotly.express as px

from dash import dcc, html, Input, Output, State, callback

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
                dbc.Button(
                    html.Span(
                        dbc.Stack([
                            html.I(className="fas fa-solid fa-map ml-2"),
                            " Bairros"
                        ])
                    ),
                    color="light",
                    className="m-1",
                    style={"width": "100%"},
                ),
                dbc.Button(
                    html.Span(
                        dbc.Stack([
                            html.I(className="fas fa-leaf ml-2"),
                            " Praças"
                        ])
                    ),
                    color="light",
                    className="m-1",
                    style={"width": "100%"},
                ),
                dbc.Button(
                    html.Span(
                        dbc.Stack([
                            html.I(className="fas fa-solid fa-tree ml-2"),
                            " Parques"
                        ])
                    ),
                    color="light",
                    className="m-1",
                    style={"width": "100%"},
                ),
                dbc.Button(
                    html.Span(
                        dbc.Stack([
                            html.I(className="fas fa-solid fa-water ml-2"),
                            " Rios"
                        ])
                    ),
                    color="light",
                    className="m-1",
                    style={"width": "100%"},
                ),
                dbc.Button(
                    html.Span(
                        dbc.Stack([
                            html.I(className="fas fa-solid fa-bicycle ml-2"),
                            " Ciclovário"
                        ])
                    ),
                    color="light",
                    className="m-1",
                    style={"width": "100%"},
                ),
                dbc.Button(
                    html.Span(
                        dbc.Stack([
                            html.I(className="fas fa-solid fa-bus ml-2"),
                            " Faixas exclusivas"
                        ])
                    ),
                    color="light",
                    className="m-1",
                    style={"width": "100%"},
                ),
            ],
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
    },
)

main_content = html.Div(
    [
        html.Iframe(
            srcDoc="<iframe src='https://www.openstreetmap.org' width='100%' height='100%'></iframe>",
            style={"width": "100%", "height": "100vh", "border": "none"},
        )
    ],
    style={"margin-left": "20%", "padding": "0px"},
)

layout = [sidebar, main_content]
