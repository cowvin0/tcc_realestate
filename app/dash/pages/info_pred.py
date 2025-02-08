import requests
import pandas as pd
import dash
import dash_table
import plotly.express as px

from dash import html, dcc

dash.register_page(__name__, name="Análise de imóveis", path="/realestate")

df_realestate = pd.DataFrame(
    requests.get("http://app:8050/real_data/return_data_db").json()
    )

center_lat = df_realestate["latitude"].mean()
center_lon = df_realestate["longitude"].mean()


layout = html.Div(children=[
    html.H1("📊 Análise de Imóveis em João Pessoa", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.H3("🏘️ Quantidade de Imóveis por Bairro"),
            dcc.Graph(
                id="bar_qnt_imoveis",
                figure=px.bar(df_realestate["bairro"].value_counts().reset_index(),
                              x="bairro", y="count",
                              labels={"bairro": "Bairro", "count": "Quantidade"},
                              title="Quantidade de Imóveis por Bairro")
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.H3("🗺️ Localização e Valores dos Imóveis"),
            dl.Map([
                dl.TileLayer(),
                dl.LayerGroup([
                    dl.Marker(
                        position=[row["latitude"], row["longitude"]],
                        children=dl.Popup(f"{row['bairro']}: R$ {row['valor']:,.2f}")
                    ) for _, row in df_realestate.iterrows()
                ])
            ], center=[center_lat, center_lon], zoom=12, style={'height': '500px', 'width': '100%'})
        ], style={'width': '40%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.H3("📈 Média de Preço por Tipo de Imóvel"),
            dcc.Graph(
                id="bar_tipo_preco",
                figure=px.bar(df_realestate.groupby("tipo")["valor"].mean().reset_index(),
                              x="tipo", y="valor",
                              labels={"tipo": "Tipo de Imóvel", "valor": "Valor Médio"},
                              title="Média de Preço por Tipo de Imóvel")
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
    ], style={'display': 'flex', 'justify-content': 'space-around'}),

])
