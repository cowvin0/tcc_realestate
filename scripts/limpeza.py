import pandas as pd
import geopy


cidade = input()
place = f"{cidade}.csv"
dados = pd.read_csv(place)

def limpar(dados):

    objects = dados.loc[dados.academia != "academia", ["endereco", "tipo", "url"]]. \
            reset_index(drop=True).

    numerics = dados.drop(columns=objects.columns).loc[dados.academia != "academia", :]. \
            reset_index(drop=True)

    dados = pd.concat([numerics, objects], axis=1)

    dados.to_csv(place)
