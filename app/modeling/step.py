from sklearn.impute import KNNImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer, SplineTransformer, OrdinalEncoder, PowerTransformer
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np

cols_imputer = ['latitude', 'longitude', 'area', 'quarto', 'vaga', 'banheiro',
                'piscina', 'elevador', 'salao_de_festa', 'academia',
                'quadra_de_esporte', 'varanda_gourmet', 'playground',
                'espaco_gourmet', 'area_servico', 'sauna', 'spa', 'valor_aluguel',
                'qnt_beneficio', 'area_aluguel'
                ]

transformar_features = ['area', 'vaga', 'banheiro',
                        'area_quarto_banheiro', 'quarto', 'total_comodo']

numerical = ['area', 'quarto', 'vaga', 'total_comodo',
             'banheiro', 'area_quarto_banheiro', 'latitude', 'longitude']

#

# KNN Imputer

class Imputer(BaseEstimator, TransformerMixin):
    """Imputer valores ausentes com KNNImputer"""
    def __init__(self, n_neighbors = 17):
        self.n_neighbors = n_neighbors
        self.imputer = ColumnTransformer(
            [("imputer", KNNImputer(n_neighbors=self.n_neighbors), cols_imputer)]
        )

    def fit(self, X, y=None):
        self.imputer.fit(X)
        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        X_copy[cols_imputer] = pd.DataFrame(self.imputer.transform(X_copy),
                                         columns=cols_imputer)

        return X_copy

# Feature Engineering

class BedAreaBedToi(BaseEstimator, TransformerMixin):
    """Passo que adiciona as combinações total de quarto e
    banheiro, quarto por área e o produto entre quarto, banheiro e área"""

    @staticmethod
    def detect_type(name):
        if (name in ("apartamento", "casas", "casas_de_condominio")):
            return 2
        else:
            return 0

    @staticmethod
    def house(area):
        if area <= 70:
            return "Pequeno"
        elif (70 < area <= 150):
            return "Médio"
        else:
            return "Grande"

    @staticmethod
    def vert_hori(specie):
        if (specie in ("apartamentos", "flat")):
            return 1
        else:
            return 0

    def fit(self, X, y=None):
        return self # nothing else to do

    def transform(self, X, y=None):
        X_copy = X.copy()
        X_copy = X_copy.assign(
            vertical_horizontal = X_copy["tipo"].apply(self.vert_hori),
            total_comodo = X_copy["tipo"].apply(self.detect_type) + X_copy[["quarto", "banheiro"]].sum(axis=1),
            area_quarto_banheiro = X["quarto"] * X["banheiro"] * X["area"],
            tamanho_imovel = X_copy["area"].apply(self.house)
                              )
        return X_copy

# Ordinal Encoder

class OrdEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.ordinal = ColumnTransformer(
            [("ord_encoder", OrdinalEncoder(), ["tamanho_imovel"])]
        )

    def fit(self, X, y=None):
        self.ordinal.fit(X)

        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        X_copy = X_copy.assign(
                tamanho_imovel = self.ordinal.transform(X_copy)
                )

        return X_copy

# One-Hot Encoding

class OneEncoder(BaseEstimator, TransformerMixin):
    """Utilizando One-Hot Encoding nas variáveis categóricas"""
    def __init__(self):
        self.encoder = ColumnTransformer(
        transformers=[
            ('encoder', OneHotEncoder(), None)
        ])

    def fit(self, X, y=None):
        categorical_features = X.select_dtypes(include=[object]).columns
        self.encoder.transformers = [('encoder',
                                      OneHotEncoder(),
                                      categorical_features)]
        self.encoder.fit(X)

        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        encoded = self.encoder.transform(X_copy)
        encoded_features_df = pd.DataFrame(
                encoded.toarray(),
                columns=self.encoder.get_feature_names_out()
                )
        X_copy = pd.concat([X_copy, encoded_features_df], axis=1)
        #X_copy[self.encoder.get_feature_names_out()] = encoded_features_df

        return X_copy.drop(['tipo'], axis=1)

# Interpolate coordinates

class Interpolate(BaseEstimator, TransformerMixin):
    def __init__(self, n_knots=7, degree=20):
        self.n_knots = n_knots
        self.degree = degree
        self.interpolate = ColumnTransformer(
            [("interpolate",
              SplineTransformer(n_knots=self.n_knots, degree=self.degree),
              ["latitude", "longitude"])]
        )

    def fit(self, X, y=None):
        self.interpolate.fit(X)
        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        X_transformed = pd.DataFrame(
                self.interpolate.transform(X_copy),
                columns = self.interpolate.get_feature_names_out())
        X_copy = (pd.concat([X_copy, X_transformed], axis=1).
                  drop(["latitude", "longitude"], axis=1))

        return X_copy

# Transformação logaritmíca

class LogTransform(BaseEstimator, TransformerMixin):
    """Adiciona transformação logaritmíca"""
    def __init__(self):
        self.log_transform = ColumnTransformer(
            transformers=[('log_transformation',
                           FunctionTransformer(np.log1p),
                           transformar_features)]
        )

    def fit(self, X, y=None):
        self.log_transform.fit(X)
        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        X_copy[transformar_features] = pd.DataFrame(
                self.log_transform.transform(X_copy),
                columns=transformar_features
                )

        return X_copy

# Transformação Yeo-Johnson

class YeoTransform(BaseEstimator, TransformerMixin):
    """Performa transformação Yeo-Johnson"""
    def __init__(self):
        self.yeo_transform = ColumnTransformer(
            transformers=[('yeo-johnson',
                           PowerTransformer(),
                           transformar_features)]
        )

    def fit(self, X, y=None):
        self.yeo_transform.fit(X)
        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        X_copy[transformar_features] = pd.DataFrame(
                self.yeo_transform.transform(X_copy),
                columns=transformar_features)

        return X_copy

# Standard Scale

class Scale(BaseEstimator, TransformerMixin):
    """Normaliza as variáveis numéricas"""
    def __init__(self):
        self.scale = ColumnTransformer(
        transformers=[('scale', StandardScaler(), numerical)])

    def fit(self, X, y=None):
        self.scale.fit(X)
        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        X_copy[numerical] = pd.DataFrame(self.scale.transform(X_copy),
                                         columns=numerical)

        return X_copy
