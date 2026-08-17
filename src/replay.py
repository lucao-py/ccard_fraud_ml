from __future__ import annotations

from pathlib import Path
from time import perf_counter, sleep

import pandas as pd

from src.persistence import (
    DEFAULT_DB_PATH,
    iniciar_run_replay,
    atualizar_progresso_replay,
    finalizar_run_replay,
    falhar_run_replay
)

from src.transaction_processor import (
    TransactionProcessor
)


class TemporalReplay:

    def __init__(
        self,
        intervalo_segundos: float = 0.2,
        caminho_banco: Path = DEFAULT_DB_PATH
    ):

        if intervalo_segundos < 0:
            raise ValueError(
                "intervalo_segundos não pode "
                "ser negativo."
            )

        self.intervalo_segundos = float(
            intervalo_segundos
        )

        self.caminho_banco = Path(
            caminho_banco
        )

        self.processador = (
            TransactionProcessor(
                caminho_banco=self.caminho_banco
            )
        )

    def executar(
        self,
        transacoes: pd.DataFrame,
        run_id: str,
        limite: int | None = None,
        atualizar_estado_a_cada: int = 1
    ) -> dict:

        if not isinstance(
            transacoes,
            pd.DataFrame
        ):
            raise TypeError(
                "transacoes deve ser "
                "um pd.DataFrame."
            )

        if atualizar_estado_a_cada <= 0:
            raise ValueError(
                "atualizar_estado_a_cada "
                "deve ser maior que zero."
            )

        dados = (
            transacoes
            .sort_values(
                "trans_date_trans_time"
            )
            .reset_index(drop=True)
            .copy()
        )

        if limite is not None:

            if limite <= 0:
                raise ValueError(
                    "limite deve ser "
                    "maior que zero."
                )

            dados = (
                dados
                .iloc[:limite]
                .copy()
            )

        total = len(
            dados
        )

        if total == 0:
            raise ValueError(
                "Nenhuma transação disponível "
                "para o replay."
            )

        iniciar_run_replay(
            run_id=run_id,
            total_transacoes=total,
            intervalo_segundos=(
                self.intervalo_segundos
            ),
            caminho_banco=(
                self.caminho_banco
            )
        )

        inicio_execucao = (
            perf_counter()
        )

        processadas = 0

        try:
            for i in range(total):

                transacao = (
                    dados
                    .iloc[[i]]
                    .copy()
                )

                self.processador.processar_transacao(
                    transacao=transacao,
                    run_id=run_id
                )

                processadas += 1

                if (
                    processadas
                    % atualizar_estado_a_cada
                    == 0
                    or processadas == total
                ):

                    atualizar_progresso_replay(
                        run_id=run_id,
                        processadas=processadas,
                        last_index=i,
                        caminho_banco=(
                            self.caminho_banco
                        )
                    )

                if (
                    self.intervalo_segundos > 0
                    and i < total - 1
                ):

                    sleep(
                        self.intervalo_segundos
                    )
                finalizar_run_replay(
                run_id=run_id,
                caminho_banco=(
                    self.caminho_banco
                )
            )

        except Exception as exc:

            falhar_run_replay(
                run_id=run_id,
                mensagem=str(exc),
                caminho_banco=(
                    self.caminho_banco
                )
            )

            raise

        tempo_total = (
            perf_counter()
            - inicio_execucao
        )

        return {
            "run_id":
                run_id,

            "status":
                "COMPLETED",

            "total_transacoes":
                total,

            "processadas":
                processadas,

            "intervalo_segundos":
                self.intervalo_segundos,

            "tempo_total_segundos":
                tempo_total,

            "transacoes_por_segundo":
                (
                    processadas
                    / tempo_total
                    if tempo_total > 0
                    else None
                )
        }        