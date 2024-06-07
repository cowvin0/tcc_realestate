from re import split
import pandas as pd
import numpy as np
from sklearn import ensemble
from sklearn import model_selection


class Model:

    def __init__(self, data, target) -> None:
        self.data = data,
        self.target = target

    def _split_data(self):
        self.data['value_bins'] = pd.cut(
            self.data['valor'],
            bins=[0., 2e5, 4e5, 6e5, 8e5, np.inf],
            labels=[1, 2, 3, 4, 5]
        )

        X = self.data.drop(columns=[self.target_column])
        y = self.data[self.target_column]

        split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)

        for train_index, test_index in split.split(X, self.data['value_bins']):
            X_train, X_test = X.loc[train_index], X.loc[test_index]
            y_train, y_test = y.loc[train_index], y.loc[test_index]

        return X_train, X_test, y_train, y_test
