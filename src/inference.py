from pathlib import Path

from catboost import (
    CatBoostClassifier,
    Pool
)

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

    def prever_score(
        self,
        transacao
    ) -> float:

        features = construir_features(
            transacao
        )

        pool = Pool(
            data=features,
            cat_features=FEATURES_CATEGORICAS
        )

        score = (
            self.modelo
            .predict_proba(pool)[0, 1]
        )

        return float(score)