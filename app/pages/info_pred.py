import dash

from dash import html

dash.register_page(__name__, name="Análise de imóveis", path="/realestate")

layout = html.Div()
