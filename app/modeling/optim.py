import pandas as pd
import numpy as np
import optuna
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, StackingRegressor
from sklearn.model_selection import StratifiedShuffleSplit, cross_val_score, KFold
df = pd.read_csv("data/cleaned/jp_limpo.csv")

df['valor_cut'] = pd.cut(df['valor'],
    bins=[0.,2e5, 4e5, 6e5, 8e5, np.inf],
    labels=[1, 2, 3, 4, 5])

split = StratifiedShuffleSplit(n_splits=20, test_size=0.2, random_state=42)
for train_index, test_index in split.split(df, df.valor_cut):
    train_df = df.loc[train_index]
    test_df = df.loc[test_index]

train_df = train_df.drop(columns=['valor_cut', 'endereco', 'bairro', 'qnt_beneficio', 'iptu', 'condominio']).reset_index(drop=True)
test_df = test_df.drop(columns=['valor_cut', 'endereco', 'bairro', 'qnt_beneficio', 'iptu', 'condominio']).reset_index(drop=True)

def objective(trial, model_name):

    match model_name:
        case 'rf':
            params = dict(
                n_estimators=trial.suggest_int(name='n_estimators', low=300, high=1200),
                max_depth=trial.suggest_int(name='max_depth', low=10, high=100),
                max_features='sqrt',
                random_state=42
            )

            model = RandomForestRegressor(
                **params,
                n_jobs=3
            )
            model.fit(X=train_df.drop('valor', axis=1), y=train_df.valor)

        case 'gb':
            params = dict(
                n_estimators=trial.suggest_int('n_estimators', low=200, high=1200),
                learning_rate=trial.suggest_float('learning_rate', low=1e-4, low=0.01),
                max_depth=trial.suggest_int('max_depth', low=10, high=100),
                max_features='sqrt',
                random_state=42
            )

            model = GradientBoostingRegressor(
                **params
            )

        case 'xgb':
            params = dict(
                n_estimators=trial.suggest_int('n_estimators', low=200, high=1200),
                learning_rate=trial.suggest_float('learning_rate', low=1e-4, low=0.01),
                max_depth=trial.suggest_int('max_depth', low=10, high=100),
                random_state=42
            )

            model = XGBRegressor(
                **params,
                n_jobs=3
            )

        case 'lgbm':
            params = dict(
                learning_rate=trial.suggest_float('learning_rate', low=1e-4, low=0.01),
                n_estimators=trial.suggest_int('n_estimators', low=200, high=1200),
                max_depth=trial.suggest_int('max_depth', low=10, high=100),
            )

    cv_scores = np.exp(np.sqrt(-cross_val_score(
        estimator=model,
        X=train_df.drop("valor", axis=1),
        y=train_df.valor,
        scoring="neg_mean_squared_error",
        n_jobs=3,
        cv=KFold(n_splits=20))))

    return np.mean(cv_scores)


if __name__ == "__main__":
    study = optuna.create_study(direction='minimize')
    study.optimize(
        lambda trial: objective(trial=trial, model_name='rf'),
        n_trials=100,
        show_progress_bar=True,
        n_jobs=3
    )
