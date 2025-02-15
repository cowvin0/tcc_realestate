import pandas as pd
import dash
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.express as px
import dash_ag_grid as dag
from dash import html, Output, Input, dcc, callback, State
from dash_iconify import DashIconify

dash.register_page(__name__, name="Análise de imóveis", path="/realestate")

df_realestate = pd.read_csv("data/cleaned/jp_limpo.csv")

center_lat = df_realestate["latitude"].mean()
center_lon = df_realestate["longitude"].mean()

fig_bar = px.bar(
    df_realestate.groupby("tipo")["valor"].mean().sort_values().reset_index(),
    x="valor",
    y="tipo",
    labels={"tipo": "", "valor": "Valor Médio (R$)"},
    text_auto=".2s",
    template="plotly_white",
)

layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            [
                dbc.Col(
                    dmc.Card(
                        children=[
                            dcc.Graph(
                                figure=fig_bar,
                                style={"height": "400px"},
                                config={"displaylogo": False},
                            )
                        ],
                        withBorder=True,
                        shadow="sm",
                        radius="md",
                        style={"padding": "10px"},
                    ),
                    width=6,
                ),
                dbc.Col(
                    dmc.Card(
                        children=[
                            dl.Map(
                                id="map-id",
                                style={"width": "100%", "height": "400px"},
                                center=[center_lat, center_lon],
                                zoom=12,
                                children=[
                                    dl.TileLayer(),
                                    dl.LayerGroup(id="points-layer"),
                                ],
                            ),
                            dcc.Store(id="stored-coordinates"),
                            html.Div(
                                dmc.ActionIcon(
                                    DashIconify(icon="clarity:settings-line", width=25),
                                    color="blue",
                                    size="xl",
                                    variant="outline",
                                    id="open-offcanvas-btn",
                                    n_clicks=0,
                                ),
                                style={
                                    "position": "fixed",
                                    "bottom": "20px",
                                    "right": "20px",
                                    "zIndex": "1000",
                                },
                            ),
                            dcc.Store(id="show-prediction-form", data=False),
                            dbc.Offcanvas(
                                id="offcanvas",
                                title="Informações Adicionais",
                                is_open=False,
                                placement="end",
                                children=[
                                    html.P(
                                        "Aqui você pode colocar informações adicionais, filtros, etc."
                                    ),
                                    html.Hr(),
                                    html.Button(
                                        "Previsão",
                                        id="predict-button",
                                        n_clicks=0,
                                        className="btn btn-primary",
                                    ),
                                    html.Div(
                                        id="prediction-form",
                                        style={"display": "none"},
                                        children=[
                                            html.Hr(),
                                            html.H4(
                                                "Preencha as informações do imóvel"
                                            ),
                                            dcc.Input(
                                                id="input-area",
                                                type="number",
                                                placeholder="Área (m²)",
                                            ),
                                            dcc.Input(
                                                id="input-bedrooms",
                                                type="number",
                                                placeholder="Quartos",
                                            ),
                                            dcc.Input(
                                                id="input-bathrooms",
                                                type="number",
                                                placeholder="Banheiros",
                                            ),
                                            dcc.Input(
                                                id="input-lat",
                                                type="text",
                                                placeholder="Latitude",
                                                disabled=True,
                                            ),
                                            dcc.Input(
                                                id="input-lon",
                                                type="text",
                                                placeholder="Longitude",
                                                disabled=True,
                                            ),
                                            html.Button(
                                                "Calcular Previsão",
                                                id="calculate-prediction",
                                                className="btn btn-success",
                                            ),
                                            html.Div(
                                                id="prediction-result",
                                                style={
                                                    "marginTop": "10px",
                                                    "fontSize": "18px",
                                                    "color": "green",
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                        withBorder=True,
                        shadow="sm",
                        radius="md",
                        style={"padding": "10px"},
                    ),
                    width=6,
                ),
            ]
        ),
        html.Hr(),
        dag.AgGrid(
            id="realestate-table",
            columnDefs=[
                {"headerName": col, "field": col, "sortable": True, "filter": True}
                for col in df_realestate.columns
            ],
            rowData=df_realestate.to_dict("records"),
            columnSize="autoSize",
            defaultColDef={"resizable": True},
            className="ag-theme-balham",
            style={"height": "370px", "width": "100%"},
            dashGridOptions={"pagination": True, "paginationPageSize": 50},
        ),
    ],
)


@callback(
    [
        Output("points-layer", "children"),
        Output("input-lat", "value"),
        Output("input-lon", "value"),
        Output("stored-coordinates", "data"),
    ],
    [Input("map-id", "clickData")],
    prevent_initial_call=True,
)
def update_map(clickData):
    if clickData and "latlng" in clickData:
        lat, lon = clickData["latlng"]["lat"], clickData["latlng"]["lng"]
        marker = dl.CircleMarker(
            center=[lat, lon],
            radius=6,
            color="red",
            fill=True,
            fillColor="red",
            fillOpacity=0.8,
            children=dl.Tooltip(f"Latitude: {lat:.6f}, Longitude: {lon:.6f}"),
        )
        return [marker], f"{lat:.6f}", f"{lon:.6f}", clickData

    return [], "", "", None


@callback(
    Output("offcanvas", "is_open"),
    [Input("open-offcanvas-btn", "n_clicks")],
    prevent_initial_call=True,
)
def toggle_offcanvas(n_clicks):
    return True


@callback(
    [Output("prediction-form", "style"), Output("show-prediction-form", "data")],
    [Input("predict-button", "n_clicks")],
    [State("show-prediction-form", "data")],
)
def toggle_prediction_form(n_clicks, is_visible):
    if n_clicks % 2 == 1:
        return {"display": "block"}, True
    else:
        return {"display": "none"}, False
