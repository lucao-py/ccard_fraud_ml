from pathlib import Path

from catboost import (
    CatBoostClassifier,
    Pool
)

import numpy as np
import pandas as pd

from src.features import (
    construir_features,
    FEATURES_CATEGORICAS,
    FEATURES_MODELO
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CAMINHO_MODELO = (
    PROJECT_ROOT
    / "models"
    / "catboost_v1"
    / "model.cbm"
)


NOMES_AMIGAVEIS_FEATURES = {
    "amt_log": "Valor da transação",
    "city_pop_log": "População da cidade",
    "idade": "Idade",
    "distancia_km": "Distância do estabelecimento",
    "hora_sin": "Horário da transação",
    "hora_cos": "Horário da transação",
    "dia_semana_sin": "Dia da semana",
    "dia_semana_cos": "Dia da semana",
    "fim_de_semana": "Fim de semana",
    "category": "Categoria",
    "gender": "Gênero",
    "state": "Estado",
}


def resumir_contribuicoes_shap(
    contribuicoes,
    top_n: int = 4
) -> list[dict]:
    """Agrupa conceitos relacionados e resume uma explicação local."""

    valores = np.asarray(
        contribuicoes,
        dtype=float
    ).reshape(-1)

    if len(valores) != len(FEATURES_MODELO):
        raise ValueError(
            "A explicação SHAP não corresponde ao contrato de features."
        )

    agrupadas: dict[str, float] = {}

    for feature, impacto in zip(
        FEATURES_MODELO,
        valores
    ):
        nome = NOMES_AMIGAVEIS_FEATURES[feature]
        agrupadas[nome] = (
            agrupadas.get(nome, 0.0)
            + float(impacto)
        )

    fatores = []

    for nome, impacto in agrupadas.items():
        if impacto > 0:
            direcao = "aumenta"
        elif impacto < 0:
            direcao = "reduz"
        else:
            direcao = "neutro"

        fatores.append({
            "feature": nome,
            "impacto": float(impacto),
            "direcao": direcao,
        })

    fatores.sort(
        key=lambda fator: abs(fator["impacto"]),
        reverse=True
    )

    return fatores[:max(1, int(top_n))]


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

    @staticmethod
    def _criar_pool(
        features: pd.DataFrame
    ) -> Pool:
        return Pool(
            data=features,
            cat_features=FEATURES_CATEGORICAS
        )

    def prever_scores_com_features(
        self,
        transacoes: pd.DataFrame
    ) -> tuple[np.ndarray, pd.DataFrame]:
        """Retorna scores e o mesmo vetor efetivamente enviado ao modelo."""

        features = construir_features(
            transacoes
        )

        pool = self._criar_pool(
            features
        )

        scores = (
            self.modelo
            .predict_proba(pool)[:, 1]
        )

        return scores, features

    def prever_scores(
            self,
            transacoes: pd.DataFrame
        ):
            """
            Calcula scores de fraude para uma ou mais transações.
            """

            scores, _ = (
                self.prever_scores_com_features(
                    transacoes
                )
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

    def explicar_features(
        self,
        features: pd.DataFrame,
        top_n: int = 4
    ) -> list[dict]:
        """Calcula explicações locais SHAP para vetores já construídos."""

        colunas_ausentes = (
            set(FEATURES_MODELO)
            - set(features.columns)
        )

        if colunas_ausentes:
            raise ValueError(
                "Features ausentes para explicação: "
                f"{sorted(colunas_ausentes)}"
            )

        features_modelo = features[
            FEATURES_MODELO
        ].copy()

        for coluna in FEATURES_CATEGORICAS:
            features_modelo[coluna] = (
                features_modelo[coluna]
                .astype("string")
                .fillna("__MISSING__")
                .astype(str)
            )

        pool = self._criar_pool(
            features_modelo
        )

        valores_shap = np.asarray(
            self.modelo.get_feature_importance(
                pool,
                type="ShapValues"
            ),
            dtype=float
        )

        # A última coluna é o valor-base da saída; não é uma feature.
        contribuicoes = valores_shap[
            :,
            :len(FEATURES_MODELO)
        ]

        return [
            {
                "fatores": resumir_contribuicoes_shap(
                    linha,
                    top_n=top_n
                )
            }
            for linha in contribuicoes
        ]
