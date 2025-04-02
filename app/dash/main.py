import dash
import dash_bootstrap_components as dbc

from app.dash.pages.navbar import navbar

# from pages.navbar import navbar
from dash import html, dcc, Output, Input

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"

app = dash.Dash(
    __name__,
    title="Imóveis",
    external_stylesheets=[dbc.themes.COSMO, FONT_AWESOME],
    use_pages=True,
    update_title=False,
    suppress_callback_exceptions=True,
    requests_pathname_prefix="/",
)

app.layout = html.Div(
    [
        navbar(),
        dash.page_container,
        dcc.Store(id="theme-store", data="light"),
        html.Link(id="theme-link", rel="stylesheet", href=dbc.themes.COSMO),
    ]
)


@app.callback(
    Output("theme-store", "data"),
    Output("theme-link", "href"),
    Input("theme-switch", "checked"),
    prevent_initial_call=True,
)
def toggle_theme(is_checked):
    if is_checked:
        return "dark", dbc.themes.DARKLY
    return "light", dbc.themes.COSMO


if __name__ == "__main__":
    # app.run(debug=False)
    app.run(debug=True)
# server = app.server
