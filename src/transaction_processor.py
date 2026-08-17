from __future__ import annotations

from pathlib import Path
from time import perf_counter

import pandas as pd

from src.inference import FraudModel
from src.decision_policy import DecisionPolicy
from src.persistence import (
    DEFAULT_DB_PATH,
    inicializar_banco,
    salvar_resultado
)

class TransactionProcessor:
    def __init__(
            self,
            caminho_banco: Path = DEFAULT_DB_PATH
    ):
        self.caminho_banco = Path(
            caminho_banco
        )

        # Carrega uma única vez o modelo congelado
        self.modelo = FraudModel()

        # Carrega uma única vez a política congelada.
        self.politica = DecisionPolicy()

        # Garante que o banco e a tabela existam.
        inicializar_banco(
            self.caminho_banco
        )

    def processar_transacao(
    self,
    transacao: pd.DataFrame,
    run_id: str,
    persistir: bool = True
    ) -> dict:

        if not isinstance(
            transacao,
            pd.DataFrame
        ):
            raise TypeError(
                "transacao deve ser um pd.DataFrame."
            )

        transacao = transacao.copy()

        if len(transacao) != 1:
            raise ValueError(
                "O processamento individual "
                "espera exatamente uma transação."
            )

        if len(transacao) != 1:
            raise ValueError(
                "O processamento individual "
                "espera exatamente uma transacao"
            )


        colunas_obrigatorias = {
            "trans_num",
            "trans_date_trans_time"
        }

        colunas_ausentes = (
            colunas_obrigatorias - set(transacao.columns)
        )

        if colunas_ausentes:
            raise ValueError(
                "Colunas obrigatórias ausentes: "
                f"{sorted(colunas_ausentes)}"
            )

        inicio = perf_counter()

        score = (
            self.modelo
            .prever_score(
                transacao
            )
        )

        decisao = (
            self.politica
            .decidir(
                score
            )
        )

        latency_ms = (
            perf_counter() - inicio
        ) * 1000

        linha = transacao.iloc[0]

        trans_num = str(
            linha["trans_num"]
        )

        trans_date_trans_time = (
            linha[
                "trans_date_trans_time"
            ]
        )

        is_fraud = None

        if (
            "is_fraud"
            in transacao.columns
            and pd.notna(
                linha["is_fraud"]
            )
        ):
            is_fraud = int(
                linha["is_fraud"]
            )

            resultado = {
            "run_id":
                str(run_id),

            "trans_num":
                trans_num,

            "trans_date_trans_time":
                trans_date_trans_time,

            "score_fraude":
                float(score),

            "decisao":
                decisao,

            "is_fraud":
                is_fraud,

            "latency_ms":
                float(latency_ms)
        }

        if persistir:

            inserido = salvar_resultado(
                run_id=run_id,
                trans_num=trans_num,
                trans_date_trans_time=(
                    trans_date_trans_time
                ),
                score_fraude=score,
                decisao=decisao,
                is_fraud=is_fraud,
                latency_ms=latency_ms,
                model_version="catboost_v1",
                policy_version=(
                    "decision_policy_v1"
                ),
                caminho_banco=(
                    self.caminho_banco
                )
            )

            resultado[
                "persistido"
            ] = inserido

        else:

            resultado[
                "persistido"
            ] = False

        return resultado