import requests
import pandas as pd
import dash
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from dash import html, dcc

dash.register_page(__name__, name="Análise de imóveis", path="/realestate")

df_realestate = pd.DataFrame(
    requests.get("http://api:8050/real_data/return_data_db").json()
)

center_lat = df_realestate["latitude"].mean()
center_lon = df_realestate["longitude"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

marker_cluster = MarkerCluster().add_to(m)

for _, row in df_realestate.iterrows():
    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=f"{row['bairro']}: R$ {row['valor']:,.2f}",
    ).add_to(marker_cluster)

map_html = m.get_root().render()

layout = html.Div(
    children=[
        html.Div(
            [
                html.Div(
                    [
                        html.H3("🏘️ Quantidade de Imóveis por Bairro"),
                        dcc.Graph(
                            id="bar_qnt_imoveis",
                            figure=px.bar(
                                df_realestate["bairro"].value_counts().reset_index(),
                                x="bairro",
                                y="count",
                                labels={"bairro": "Bairro", "count": "Quantidade"},
                                title="Quantidade de Imóveis por Bairro",
                            ),
                        ),
                    ],
                    style={
                        "width": "30%",
                        "display": "inline-block",
                        "padding": "10px",
                    },
                ),
                html.Div(
                    [
                        html.Iframe(
                            srcDoc=map_html,
                            width="100%",
                            height="500px",
                            style={"border": "none"},
                        ),
                    ],
                    style={
                        "width": "40%",
                        "display": "inline-block",
                        "padding": "10px",
                    },
                ),
                html.Div(
                    [
                        html.H3("📈 Média de Preço por Tipo de Imóvel"),
                        dcc.Graph(
                            id="bar_tipo_preco",
                            figure=px.bar(
                                df_realestate.groupby("tipo")["valor"]
                                .mean()
                                .reset_index(),
                                x="tipo",
                                y="valor",
                                labels={
                                    "tipo": "Tipo de Imóvel",
                                    "valor": "Valor Médio",
                                },
                                title="Média de Preço por Tipo de Imóvel",
                            ),
                        ),
                    ],
                    style={
                        "width": "30%",
                        "display": "inline-block",
                        "padding": "10px",
                    },
                ),
            ],
            style={"display": "flex", "justify-content": "space-around"},
        ),
    ]
)
