import pandas as pd
import os

CITY = os.environ.get('CITY')
place = f'data/{CITY[3:]}.csv'
data = pd.read_csv(place)

def limpar(df):

    remove_cols = df[df.tipo != "imoveis"].\
            drop_duplicates(["id"]).\
            replace({"lancamentos_de_terrenos_lotes_e_condominios": "terrenos_lotes_e_condominios",
                     "lancamentos_de_casas_de_condominio": "casas_de_condominio",
                     "lancamentos_de_apartamentos": "apartamentos",
                     "lancamentos_de_casas_comerciais": "casas_comerciais",
                     "lancamentos_de_casas": "casas"}).\
            reset_index(drop=True)

    objects = remove_cols[["endereco", "tipo", "url"]]

    numerics = remove_cols.drop(columns=objects.columns)

    df = pd.concat([numerics.astype(float), objects], axis=1)

    df.to_csv(place, index=False)

if __name__ == "__main__":
    limpar(data)
