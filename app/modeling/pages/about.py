import dash
import dash_bootstrap_components as dbc
import plotly.express as px

from dash import dcc, html, Input, Output, State, callback

dash.register_page(
    __name__,
    name='Sobre',
    path='/'
    )


layout = html.Div(
)
