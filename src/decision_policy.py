import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CAMINHO_POLITICA = (
    PROJECT_ROOT
    / "models"
    / "catboost_v1"
    / "decision_policy.json"
)


class DecisionPolicy:

    def __init__(self):

        if not CAMINHO_POLITICA.exists():
            raise FileNotFoundError(
                f"Política não encontrada em: "
                f"{CAMINHO_POLITICA}"
            )

        with open(
            CAMINHO_POLITICA,
            "r",
            encoding="utf-8"
        ) as arquivo:
            config = json.load(
                arquivo
            )

        self.threshold_revisao = (
            config["threshold_revisao"]
        )

        self.threshold_critico = (
            config[
                "threshold_alerta_critico"
            ]
        )

    def decidir(
        self,
        score: float
    ) -> str:

        if score >= self.threshold_critico:
            return "ALERTA_CRITICO"

        if score >= self.threshold_revisao:
            return "REVISAR"

        return "APROVAR"

    @staticmethod
    def _formatar_threshold(valor: float) -> str:
        percentual = valor * 100
        casas = 0 if percentual.is_integer() else 1
        return (
            f"{percentual:.{casas}f}%"
            .replace(".", ",")
        )

    def descrever_regra(
        self,
        decisao: str
    ) -> str:
        """Descreve a faixa usando os thresholds carregados da política."""

        revisao = self._formatar_threshold(
            float(self.threshold_revisao)
        )
        critico = self._formatar_threshold(
            float(self.threshold_critico)
        )

        if decisao == "APROVAR":
            return f"Score < {revisao}"

        if decisao == "REVISAR":
            return f"Entre {revisao} e {critico}"

        if decisao == "ALERTA_CRITICO":
            return f"Score ≥ {critico}"

        return "Faixa operacional indisponível"
