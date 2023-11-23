import pandas as pd
import os

CITY = os.environ.get('CITY')
COND = os.environ.get('COND')
place = f'data/{CITY[3:]}-{COND}.csv'
data = pd.read_csv(place)

def limpar(df):

    remove_cols = df[df.tipo != "imoveis"].\
            drop_duplicates(["id"]).\
            replace({"lancamentos_de_terrenos_lotes_e_condominios": "terrenos_lotes_e_condominios",
                     "lancamentos_de_casas_de_condominio": "casas_de_condominio",
                     "lancamentos_de_apartamentos": "apartamentos",
                     "lancamentos_de_casas_comerciais": "casas_comerciais",
                     "lancamentos_de_casas": "casas",
                     "casas_para_alugar": "casas",
                     "apartamentos_para_alugar": "apartamentos",
                     "casas_comerciais_para_alugar": "casas_comerciais",
                     "casas_de_condominio_para_alugar": "casas_de_condominio",
                     "terrenos_lotes_e_condominios_para_alugar": "terrenos_lotes_e_condominios"}).\
            reset_index(drop=True)

    objects = remove_cols[["endereco", "tipo", "url", "foto_imovel"]]

    numerics = remove_cols.drop(columns=objects.columns)

    df = pd.concat([numerics.astype(float), objects], axis=1)

    df.to_csv(place, index=False)

if __name__ == "__main__":
    limpar(data)
