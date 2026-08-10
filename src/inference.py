from pathlib import Path

from catboost import (
    CatBoostClassifier,
    Pool
)

import pandas as pd

from src.features import (
    construir_features,
    FEATURES_CATEGORICAS
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CAMINHO_MODELO = (
    PROJECT_ROOT
    / "models"
    / "catboost_v1"
    / "model.cbm"
)


class FraudModel:

    def __init__(self):

        if not CAMINHO_MODELO.exists():
            raise FileNotFoundError(
                f"Modelo não encontrado em: "
                f"{CAMINHO_MODELO}"
            )

        self.modelo = CatBoostClassifier()

        self.modelo.load_model(
            str(CAMINHO_MODELO)
        )

    def prever_scores(
            self,
            transacoes: pd.DataFrame
        ):
            """
            Calcula scores de fraude para uma ou mais transações.
            """

            features = construir_features(
                transacoes
            )

            pool = Pool(
                data=features,
                cat_features=FEATURES_CATEGORICAS
            )

            scores = (
                self.modelo
                .predict_proba(pool)[:, 1]
            )

            return scores

    def prever_score(
        self,
        transacao: pd.DataFrame
    ) -> float:
        """
        Calcula o score de fraude para uma única transação.
        """

        scores = self.prever_scores(
            transacao
        )

        return float(
            scores[0]
        )