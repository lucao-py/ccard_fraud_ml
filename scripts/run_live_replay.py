from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


from src.replay import TemporalReplay


# ==========================================================
# DATASET
# ==========================================================

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
    df = df.drop(
        columns=colunas_indice
    )


df = (
    df
    .sort_values(
        "trans_date_trans_time"
    )
    .reset_index(drop=True)
)


# ==========================================================
# TESTE TEMPORAL
# ==========================================================

fim_validacao = int(
    len(df) * 0.85
)

df_teste = (
    df.iloc[
        fim_validacao:
    ]
    .copy()
)


# ==========================================================
# REPLAY
# ==========================================================

from datetime import datetime


RUN_ID = (
    "replay_live_"
    + datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
)


replay = TemporalReplay(
    intervalo_segundos=0.02
)


print(
    f"Iniciando replay: {RUN_ID}"
)

print(
    f"Transações disponíveis: {len(df_teste):,}"
)


resultado = replay.executar(
    transacoes=df_teste,
    run_id=RUN_ID,

    # Começaria com 10 mil para nossa demonstração.
    limite=10_000,

    atualizar_estado_a_cada=50
)


print()
print("Replay finalizado.")
print(resultado)