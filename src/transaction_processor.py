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

        scores, features_modelo = (
            self.modelo
            .prever_scores_com_features(
                transacao
            )
        )

        score = float(
            scores[0]
        )

        model_features_json = (
            features_modelo
            .iloc[0]
            .to_json(
                force_ascii=False,
                double_precision=15
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

        def valor_opcional(
            coluna
        ):

            if (
                coluna not in transacao.columns
                or pd.isna(linha[coluna])
            ):
                return None

            return linha[coluna]

        first = valor_opcional(
            "first"
        )

        last = valor_opcional(
            "last"
        )

        merchant = valor_opcional(
            "merchant"
        )

        category = valor_opcional(
            "category"
        )

        amt = valor_opcional(
            "amt"
        )

        city = valor_opcional(
            "city"
        )

        state = valor_opcional(
            "state"
        )
        
        trans_num = str(
            linha["trans_num"]
        )

        trans_date_trans_time = (
            linha[
                "trans_date_trans_time"
            ]
        )
        cc_last4 = None

        cc_num = valor_opcional(
            "cc_num"
        )

        if cc_num is not None:

            cc_texto = str(
                cc_num
            )

            cc_last4 = (
                cc_texto[-4:]
                if len(cc_texto) >= 4
                else cc_texto
            )
        if amt is not None:
            amt = float(amt)

        first = (
            str(first)
            if first is not None
            else None
        )

        last = (
            str(last)
            if last is not None
            else None
        )

        merchant = (
            str(merchant)
            if merchant is not None
            else None
        )

        category = (
            str(category)
            if category is not None
            else None
        )

        city = (
            str(city)
            if city is not None
            else None
        )

        state = (
            str(state)
            if state is not None
            else None
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

            "first":
                first,

            "last":
                last,

            "merchant":
                merchant,

            "category":
                category,

            "amt":
                amt,

            "city":
                city,

            "state":
                state,

            "cc_last4":
                cc_last4,

            "model_features_json":
                model_features_json,

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

            first=first,
            last=last,

            merchant=merchant,
            category=category,

            amt=amt,

            city=city,
            state=state,

            cc_last4=cc_last4,

            model_features_json=(
                model_features_json
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
