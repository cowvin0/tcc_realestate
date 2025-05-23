import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from dash import html, dcc, Output, Input, State, ALL, callback
from dash_iconify import DashIconify


def navbar():
    return dbc.Navbar(
        dbc.Container(
            [
                dcc.Location(id="url", refresh=False),
                dmc.ActionIcon(
                    DashIconify(icon="zondicons:menu", width=25),
                    color="white",
                    variant="subtle",
                    id="nav-btn",
                    m=25,
                    className="nav-container",
                ),
                dbc.Offcanvas(
                    [
                        dmc.Stack(
                            [
                                dmc.NavLink(
                                    label=page["name"],
                                    href=page["path"],
                                    variant="subtle",
                                    style={"font-size": "16px", "color": "black"},
                                    id={"type": "dynamic-link", "index": idx},
                                )
                                for idx, page in enumerate(dash.page_registry.values())
                                if page["module"] != "pages.not_found_404"
                            ],
                            align="center",
                            justify="center",
                            spacing="lg",
                        )
                    ],
                    title="",
                    id="nav-offcanvas",
                    is_open=False,
                    placement="start",
                    backdrop=True,
                    scrollable=True,
                ),
                html.Div(id="floating-button-container", style={"marginLeft": "auto"}),
                html.Div(
                    dmc.Switch(
                        label="",
                        onLabel=DashIconify(icon="emojione:full-moon", width=15),
                        offLabel=DashIconify(icon="noto-v1:sun", width=15),
                        size="md",
                        id="theme-switch",
                        checked=False,
                    ),
                    style={
                        "marginLeft": "auto",
                        "display": "flex",
                        "alignItems": "center",
                    },
                ),
            ],
            fluid=True,
        ),
        style={
            "maxWidth": "1200px",
            "width": "100%",
            "margin": "0 auto",
            "height": "60px",
            "padding": "5px 20px",
        },
        color="transparent",
        dark=True,
        className="mb-3",
    )


@callback(
    Output("nav-offcanvas", "is_open"),
    Input("nav-btn", "n_clicks"),
    State("nav-offcanvas", "is_open"),
    prevent_initial_call=True,
)
def toggle_offcanvas(_, is_open):
    return not is_open


@callback(
    Output("nav-offcanvas", "is_open", allow_duplicate=True),
    Input({"type": "dynamic-link", "index": ALL}, "n_clicks"),
    State("nav-offcanvas", "is_open"),
    prevent_initial_call=True,
)
def close_offcanvas(n, is_open):
    if any(n):
        return False
    return is_open


@callback(Output("floating-button-container", "children"), Input("url", "pathname"))
def display_floating_button(pathname):
    if pathname == "/":

        def button(icon, id):
            return dmc.ActionIcon(
                DashIconify(icon=icon, width=25),
                color="blue",
                size="xl",
                variant="transparent",
                id=id,
                n_clicks=0,
            )

        return dbc.Stack(
            [
                button("bx:filter-alt", "open-offcanvas-btn"),
                button("lucide:file-spreadsheet", "open-offcanvas-table-btn"),
            ],
            direction="horizontal",
        )
    return ""
