import dash
import dash_bootstrap_components as dbc
# import plotly.express as px

from pages.navbar import navbar
from dash import dcc, html, Input, Output, State
from flask_caching import Cache

app = dash.Dash(
    __name__,
    title='Imóveis',
    external_stylesheets=[
        dbc.themes.COSMO
    ],
    use_pages=True,
    update_title=False,
    suppress_callback_exceptions=True,
    requests_pathname_prefix='/'
)

app.layout = html.Div(
    [
        navbar(),
        dash.page_container
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
