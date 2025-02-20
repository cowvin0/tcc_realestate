import pandas as pd
import dash
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.express as px
import dash_ag_grid as dag
import folium

from dash import html, Output, Input, dcc, callback, State
from folium.plugins import HeatMap

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
                                id="bar-graph",
                                figure=fig_bar,
                                style={"height": "400px"},
                                config={
                                    "displaylogo": False,
                                    "scrollZoom": False,
                                    "doubleClick": "reset",
                                    "modeBarButtonsToRemove": [
                                        "zoom",
                                        "zoomIn",
                                        "zoomOut",
                                        "pan",
                                        "lasso2d",
                                        "autoScale",
                                    ],
                                },
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
                            html.Div(id="map-container"),
                            dcc.Store(
                                id="filtered-data",
                                data=df_realestate.to_dict("records"),
                            ),
                            dcc.Store(id="stored-coordinates"),
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
                                    dmc.Select(
                                        label="Tipo de Mapa",
                                        placeholder="Selecione o tipo de mapa",
                                        id="map-select",
                                        value="heatmap",
                                        data=[
                                            {"value": "leaflet", "label": "Sem tipo"},
                                            {
                                                "value": "heatmap",
                                                "label": "Mapa de Calor",
                                            },
                                            {
                                                "value": "markers",
                                                "label": "Mapa de pontos",
                                            },
                                        ],
                                        w=200,
                                        mb=10,
                                    ),
                                    html.Button(
                                        "Estimar valor de imóvel",
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
                                                disabled=False,
                                            ),
                                            dcc.Input(
                                                id="input-lon",
                                                type="text",
                                                placeholder="Longitude",
                                                disabled=False,
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
    Output("map-container", "children"),
    [
        Input("map-select", "value"),
        Input("filtered-data", "data"),
        Input("predict-button", "n_clicks"),
    ],
)
def update_map(map_type, filtered_data, n_clicks):
    df_filtered = pd.DataFrame(filtered_data)

    if n_clicks % 2 == 1:
        map_type = None

    if map_type == "heatmap":
        data = df_filtered[["latitude", "longitude", "valor"]].values.tolist()
        heatmap_map = folium.Map([center_lat, center_lon], zoom_start=12)
        HeatMap(data, radius=13).add_to(heatmap_map)
        return html.Iframe(
            srcDoc=heatmap_map._repr_html_(), width="100%", height="400px"
        )
    elif map_type == "markers":
        fig_map_marker = px.scatter_mapbox(
            df_filtered,
            lat="latitude",
            lon="longitude",
            color="valor",
            size="valor",
            hover_name="tipo",
            hover_data={"latitude": False, "longitude": False, "valor": ":.2f"},
            color_continuous_scale="Viridis",
            size_max=15,
            zoom=12,
            mapbox_style="open-street-map",
            center={
                "lat": df_filtered["latitude"].mean(),
                "lon": df_filtered["longitude"].mean(),
            },
        )

        fig_map_marker.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            coloraxis_colorbar=dict(
                title="Valor (R$)",
                orientation="h",
                tickformat=".2s",
                x=0,
                xanchor="left",
                y=0.85,
                yanchor="bottom",
                len=0.6,
                thickness=15,
                title_font=dict(size=12),
            ),
        )
        return dcc.Graph(
            figure=fig_map_marker,
            style={"width": "100%", "height": "400px"},
            config={"displaylogo": False},
        )
    else:
        return dl.Map(
            id="map-id",
            style={"width": "100%", "height": "400px"},
            center=[center_lat, center_lon],
            zoom=12,
            children=[
                dl.TileLayer(),
                dl.LayerGroup(id="points-layer"),
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
)
def update_coordinates(clickData):
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
        return [marker], f"{lat}", f"{lon}", clickData
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


@callback(
    Output("filtered-data", "data"),
    [Input("bar-graph", "selectedData")],
    # [State("filtered-data", "data")],
)
def filter_data(selectedData):
    print(f"selectedData: {selectedData}")

    if selectedData and "points" in selectedData:
        selected_types = {point["y"] for point in selectedData["points"]}
        print(f"Selected Types: {selected_types}")

        filtered_df = df_realestate[df_realestate["tipo"].isin(selected_types)]
        return filtered_df.to_dict("records")

    return df_realestate.to_dict("records")
