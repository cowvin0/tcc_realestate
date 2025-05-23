from sklearn.impute import KNNImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import (
    StandardScaler,
    OneHotEncoder,
    FunctionTransformer,
    SplineTransformer,
    OrdinalEncoder,
    PowerTransformer,
    PolynomialFeatures,
    RobustScaler,
)
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np

cols_imputer = [
    "latitude",
    "longitude",
    "area",
    "quarto",
    "vaga",
    "banheiro",
    "piscina",
    "elevador",
    "salao_de_festa",
    "academia",
    "quadra_de_esporte",
    "varanda_gourmet",
    "playground",
    "espaco_gourmet",
    "area_servico",
    "sauna",
    "spa",
    "area_aluguel",
    "valor_aluguel",
    "portaria_24_horas",
]

transformar_features = [
    "quarto_area_aluguel",
    "area",
    "vaga",
    "banheiro",
    "quarto",
    "total_comodo",
    "quarto_por_area",
]


numerical = [
    "coord_valor_aluguel",
    "quarto_area_aluguel",
    "quarto_por_area",
    "banheiro",
    "latitude",
    "longitude",
    "area",
    "quarto",
    "vaga",
]


class Imputer(BaseEstimator, TransformerMixin):
    """Imputer valores ausentes com KNNImputer"""

    def __init__(self, n_neighbors=17):
        self.n_neighbors = n_neighbors
        self.imputer = ColumnTransformer(
            [("imputer", KNNImputer(n_neighbors=self.n_neighbors), cols_imputer)]
        )

    def fit(self, X, y=None):
        self.imputer.fit(X)
        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        X_copy[cols_imputer] = pd.DataFrame(
            self.imputer.transform(X_copy), columns=cols_imputer
        )

        return X_copy


class Poly(BaseEstimator, TransformerMixin):
    def __init__(self, degree=2):
        self.degree = degree
        self.poly = ColumnTransformer(
            transformers=[
                (
                    "polynomial_features",
                    PolynomialFeatures(degree=self.degree),
                    ["quarto", "banheiro"],
                )
            ]
        )

    def fit(self, X, y=None):
        self.poly.fit(X)
        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        transformed = self.poly.transform(X_copy)
        columns_remove = self.poly.get_feature_names_out()
        X_transformed = pd.DataFrame(transformed, columns=columns_remove)

        X_copy = pd.concat([X_copy, X_transformed], axis=1)

        return X_copy


class BedAreaBedToi(BaseEstimator, TransformerMixin):
    @staticmethod
    def detect_type(name):
        if name in ("apartamento", "casas", "casas_de_condominio", "flats"):
            return 2
        else:
            return 0

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        X_copy = X_copy.assign(
            quarto_area_aluguel=lambda x: x.quarto * x.area_aluguel,
            coord_valor_aluguel=lambda x: x.valor_aluguel * x.latitude * x.longitude,
            quarto_por_area=lambda x: x.quarto / x.area,
            total_comodo=lambda x: x["tipo"].apply(self.detect_type)
            + x[["quarto", "banheiro"]].sum(axis=1),
        )
        return X_copy


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
        X_copy = X_copy.assign(tamanho_imovel=self.ordinal.transform(X_copy))

        return X_copy


class OneEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.encoder = ColumnTransformer(
            transformers=[("encoder", OneHotEncoder(), None)]
        )

    def fit(self, X, y=None):
        categorical_features = X.select_dtypes(include=[object]).columns
        self.encoder.transformers = [("encoder", OneHotEncoder(), categorical_features)]
        self.encoder.fit(X)

        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        encoded = self.encoder.transform(X_copy)
        encoded_features_df = pd.DataFrame(
            encoded.toarray(), columns=self.encoder.get_feature_names_out()
        )
        X_copy = pd.concat([X_copy, encoded_features_df], axis=1)

        # return X_copy.drop(["tipo", "tamanho_imovel"], axis=1)
        return X_copy.drop(["tipo"], axis=1)


class Interpolate(BaseEstimator, TransformerMixin):
    def __init__(self, n_knots=7, degree=20):
        self.n_knots = n_knots
        self.degree = degree
        self.interpolate = ColumnTransformer(
            [
                (
                    "interpolate",
                    SplineTransformer(n_knots=self.n_knots, degree=self.degree),
                    ["latitude", "longitude"],
                )
            ]
        )

    def fit(self, X, y=None):
        self.interpolate.fit(X)
        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        X_transformed = pd.DataFrame(
            self.interpolate.transform(X_copy),
            columns=self.interpolate.get_feature_names_out(),
        )
        X_copy = pd.concat([X_copy, X_transformed], axis=1).drop(
            ["latitude", "longitude"], axis=1
        )

        return X_copy


class LogTransform(BaseEstimator, TransformerMixin):

    def __init__(self):
        self.log_transform = ColumnTransformer(
            transformers=[
                (
                    "log_transformation",
                    FunctionTransformer(np.log1p),
                    transformar_features,
                )
            ]
        )

    def fit(self, X, y=None):
        self.log_transform.fit(X)
        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        X_copy[transformar_features] = pd.DataFrame(
            self.log_transform.transform(X_copy), columns=transformar_features
        )

        return X_copy


class YeoTransform(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.yeo_transform = ColumnTransformer(
            transformers=[("yeo-johnson", PowerTransformer(), ["coord_valor_aluguel"])]
        )

    def fit(self, X, y=None):
        self.yeo_transform.fit(X)
        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        X_copy["coord_valor_aluguel"] = pd.DataFrame(
            self.yeo_transform.transform(X_copy), columns=["coord_valor_aluguel"]
        )

        return X_copy


class Scale(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.scale = ColumnTransformer(
            transformers=[("scale", StandardScaler(), numerical)]
        )

    def fit(self, X, y=None):
        self.scale.fit(X)
        return self

    def transform(self, X, y=None):
        X_copy = X.copy()
        X_copy[numerical] = pd.DataFrame(
            self.scale.transform(X_copy), columns=numerical
        )

        return X_copy


class Robust(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.scale = ColumnTransformer(
            transformers=[("scale", RobustScaler(), numerical)]
        )

    def fit(self, X, y=None):
        self.scale.fit(X)
        return self

    def transform(self, X, y=None):
        X_copy = X.copy()

        transformed_scale = pd.DataFrame(
            self.scale.transform(X_copy), columns=numerical
        )

        X_copy = X_copy.drop(numerical, axis=1)

        X_copy = pd.concat([X_copy, transformed_scale], axis=1)

        return X_copy


class GroupCord(BaseEstimator, TransformerMixin):
    def __init__(self, n_clusters=8):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=self.n_clusters)

    def fit(self, X, y=None):
        self.kmeans.fit(X[numerical])
        return self

    def transform(self, X, y=None):
        labels = self.kmeans.predict(X[numerical])
        return X.assign(k_groups=labels)
