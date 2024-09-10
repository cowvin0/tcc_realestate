import pandas as pd
import numpy as np
import optuna
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score, KFold

drop_cols = [
    'endereco', 'bairro',
    'qnt_beneficio', 'iptu',
    'condominio'
    ]

train_df = pd.read_csv('data/cleaned/train.csv').drop(columns=drop_cols)
test_df = pd.read_csv('data/cleaned/test.csv').drop(columns=drop_cols)


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
                random_state=42,
                n_estimators=trial.suggest_int('n_estimators', low=200, high=2500),
                num_leaves=trial.suggest_int('num_leaves', low=100, high=700),
                max_depth=trial.suggest_int('max_depth', low=10, high=100),
            )

            model = LGBMRegressor(
                **params,
                n_jobs=3
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
