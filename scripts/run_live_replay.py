from datetime import datetime
import os
from pathlib import Path
import signal
import sys
import uuid

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


from src.replay import TemporalReplay


DATA_PATH = (
    PROJECT_ROOT
    / "raw"
    / "fraudTrain.csv"
)


dtypes = {
    "cc_num": "string",
    "trans_num": "string",
    "zip": "string",
    "merchant": "string",
    "category": "category",
    "gender": "category",
    "state": "category",
    "first": "string",
    "last": "string",
    "street": "string",
    "city": "string",
    "job": "string"
}


def _gerar_run_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"runtime_{timestamp}_{uuid.uuid4().hex[:8]}"


def _interromper_processamento(_signum, _frame) -> None:
    raise KeyboardInterrupt


def _executar_processamento(run_id: str) -> int:
    df = pd.read_csv(
        DATA_PATH,
        dtype=dtypes,
        parse_dates=[
            "trans_date_trans_time",
            "dob"
        ]
    )

    colunas_indice = [
        coluna
        for coluna in df.columns
        if str(coluna).startswith("Unnamed:")
    ]

    if colunas_indice:
        df = df.drop(columns=colunas_indice)

    df = (
        df
        .sort_values("trans_date_trans_time")
        .reset_index(drop=True)
    )

    fim_validacao = int(len(df) * 0.85)
    df_teste = df.iloc[fim_validacao:].copy()

    replay = TemporalReplay(
        intervalo_segundos=0.02
    )

    print("Processamento transacional iniciado.", flush=True)
    print(
        f"Transações disponíveis: {len(df_teste):,}",
        flush=True,
    )

    resultado = replay.executar(
        transacoes=df_teste,
        run_id=run_id,
        limite=None,
        atualizar_estado_a_cada=50,
    )

    print("Processamento finalizado.", flush=True)
    print(
        f"Transações processadas: {resultado['processadas']:,}",
        flush=True,
    )
    return 0


def main() -> int:
    signal.signal(signal.SIGTERM, _interromper_processamento)

    run_id = os.getenv("FRAUD_RUN_ID") or _gerar_run_id()

    try:
        return _executar_processamento(run_id)
    except KeyboardInterrupt:
        print("Processamento interrompido.", flush=True)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
