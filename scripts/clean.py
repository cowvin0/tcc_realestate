import pandas as pd
import os

CITY = os.environ.get('CITY')
data = pd.read_csv(f'data/{CITY[3:]}.csv')

def limpar(df):

    remove_cols = df[df.academia != "academia" and df.tipo != "imoveis"].\
            drop_duplicates(["id"]).\
            replace({"lancamentos_de_terrenos_lotes_e_condominios": "terrenos_lotes_e_condominios",
                     "lancamentos_de_casas_de_condominio": "casas_de_condominio",
                     "lancamentos_de_apartamentos": "apartamentos",
                     "lancamentos_de_casas_comerciais": "casas_comerciais",
                     "lancamentos_de_casas": "casas"}).\
            query("sauna == 1 or spa == 1 or quadra_de_esporte == 1 or varanda_gourmet == 1 or academia == 1").\
            query("valor > 230000").\
            reset_index(drop=True)
            

    objects = remove_cols[["endereco", "tipo", "url"]]

    numerics = remove_cols.drop(columns=objects.columns)

    df = pd.concat([numerics.astype(float), objects], axis=1)

    df.to_csv(place, index=False)

if __name__ == "__main__":
    limpar(data)
