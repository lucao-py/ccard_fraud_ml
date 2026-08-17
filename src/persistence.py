from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_DB_PATH = (
    PROJECT_ROOT
    / "runtime"
    / "fraud_detection.db"
)


DECISOES_VALIDAS = {
    "APROVAR",
    "REVISAR",
    "ALERTA_CRITICO"
}


def conectar_banco(
    caminho_banco: Path = DEFAULT_DB_PATH
) -> sqlite3.Connection:

    caminho_banco = Path(caminho_banco)

    caminho_banco.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conexao = sqlite3.connect(
        caminho_banco,
        timeout=5
    )

    conexao.row_factory = sqlite3.Row

    # Permite melhor convivência entre escrita
    # do processador e leitura do dashboard.
    conexao.execute(
        "PRAGMA journal_mode=WAL;"
    )

    conexao.execute(
        "PRAGMA synchronous=NORMAL;"
    )

    conexao.execute(
        "PRAGMA busy_timeout=5000;"
    )

    return conexao


def inicializar_banco(
    caminho_banco: Path = DEFAULT_DB_PATH
) -> Path:

    with conectar_banco(
        caminho_banco
    ) as conexao:

        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS transacoes_processadas (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                run_id TEXT NOT NULL,

                trans_num TEXT NOT NULL,

                trans_date_trans_time TEXT NOT NULL,

                score_fraude REAL NOT NULL
                    CHECK (
                        score_fraude >= 0
                        AND score_fraude <= 1
                    ),

                decisao TEXT NOT NULL
                    CHECK (
                        decisao IN (
                            'APROVAR',
                            'REVISAR',
                            'ALERTA_CRITICO'
                        )
                    ),

                is_fraud INTEGER
                    CHECK (
                        is_fraud IN (0, 1)
                        OR is_fraud IS NULL
                    ),

                processed_at TEXT NOT NULL,

                latency_ms REAL,

                model_version TEXT NOT NULL,

                policy_version TEXT NOT NULL,

                UNIQUE (
                    run_id,
                    trans_num
                )
            )
            """
        )
        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_transacoes_run_data
            ON transacoes_processadas (
                run_id,
                trans_date_trans_time
            )
            """
        )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_transacoes_run_decisao
            ON transacoes_processadas (
                run_id,
                decisao
            )
            """
        )

        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS replay_runs (

                run_id TEXT PRIMARY KEY,

                status TEXT NOT NULL
                    CHECK (
                        status IN (
                            'RUNNING',
                            'COMPLETED',
                            'FAILED'
                        )
                    ),

                total_transacoes INTEGER NOT NULL,

                processadas INTEGER NOT NULL DEFAULT 0,

                last_index INTEGER NOT NULL DEFAULT -1,

                intervalo_segundos REAL NOT NULL,

                started_at TEXT NOT NULL,

                updated_at TEXT NOT NULL,

                completed_at TEXT,

                error_message TEXT,

                model_version TEXT NOT NULL,

                policy_version TEXT NOT NULL
            )
            """
        )
    return Path(
        caminho_banco
    )
        

def salvar_resultado(
    *,
    run_id: str,
    trans_num: str,
    trans_date_trans_time,
    score_fraude: float,
    decisao: str,
    is_fraud: int | None = None,
    latency_ms: float | None = None,
    model_version: str = "catboost_v1",
    policy_version: str = "decision_policy_v1",
    caminho_banco: Path = DEFAULT_DB_PATH
) -> bool:

    score_fraude = float(
        score_fraude
    )

    if not 0 <= score_fraude <= 1:
        raise ValueError(
            "score_fraude deve estar "
            "entre 0 e 1."
        )

    if decisao not in DECISOES_VALIDAS:
        raise ValueError(
            f"Decisão inválida: {decisao}"
        )

    if (
        is_fraud is not None
        and int(is_fraud) not in (0, 1)
    ):
        raise ValueError(
            "is_fraud deve ser 0, 1 "
            "ou None."
        )

    if hasattr(
        trans_date_trans_time,
        "isoformat"
    ):
        data_transacao = (
            trans_date_trans_time
            .isoformat()
        )
    else:
        data_transacao = str(
            trans_date_trans_time
        )

    processed_at = (
        datetime.now(
            timezone.utc
        )
        .isoformat()
    )

    with conectar_banco(
        caminho_banco
    ) as conexao:

        cursor = conexao.execute(
            """
            INSERT INTO transacoes_processadas (
                run_id,
                trans_num,
                trans_date_trans_time,
                score_fraude,
                decisao,
                is_fraud,
                processed_at,
                latency_ms,
                model_version,
                policy_version
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT (
                run_id,
                trans_num
            )
            DO NOTHING
            """,
            (
                str(run_id),
                str(trans_num),
                data_transacao,
                score_fraude,
                decisao,
                (
                    None
                    if is_fraud is None
                    else int(is_fraud)
                ),
                processed_at,
                latency_ms,
                model_version,
                policy_version
            )
        )

        inserido = (
            cursor.rowcount == 1
        )

    return inserido

def contar_transacoes(
    run_id: str | None = None,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> int:

    with conectar_banco(
        caminho_banco
    ) as conexao:

        if run_id is None:

            resultado = conexao.execute(
                """
                SELECT COUNT(*)
                FROM transacoes_processadas
                """
            ).fetchone()

        else:

            resultado = conexao.execute(
                """
                SELECT COUNT(*)
                FROM transacoes_processadas
                WHERE run_id = ?
                """,
                (run_id,)
            ).fetchone()

    return int(
        resultado[0]
    )

def buscar_ultimas_transacoes(
    limite: int = 10,
    run_id: str | None = None,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> list[dict]:

    with conectar_banco(
        caminho_banco
    ) as conexao:

        if run_id is None:

            linhas = conexao.execute(
                """
                SELECT *
                FROM transacoes_processadas
                ORDER BY id DESC
                LIMIT ?
                """,
                (limite,)
            ).fetchall()

        else:

            linhas = conexao.execute(
                """
                SELECT *
                FROM transacoes_processadas
                WHERE run_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    run_id,
                    limite
                )
            ).fetchall()

    return [
        dict(linha)
        for linha in linhas
    ]

def iniciar_run_replay(
    *,
    run_id: str,
    total_transacoes: int,
    intervalo_segundos: float,
    model_version: str = "catboost_v1",
    policy_version: str = "decision_policy_v1",
    caminho_banco: Path = DEFAULT_DB_PATH
) -> None:

    agora = (
        datetime.now(
            timezone.utc
        )
        .isoformat()
    )

    try:

        with conectar_banco(
            caminho_banco
        ) as conexao:

            conexao.execute(
                """
                INSERT INTO replay_runs (
                    run_id,
                    status,
                    total_transacoes,
                    processadas,
                    last_index,
                    intervalo_segundos,
                    started_at,
                    updated_at,
                    model_version,
                    policy_version
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(run_id),
                    "RUNNING",
                    int(total_transacoes),
                    0,
                    -1,
                    float(intervalo_segundos),
                    agora,
                    agora,
                    model_version,
                    policy_version
                )
            )

    except sqlite3.IntegrityError as exc:

        raise ValueError(
            f"O run_id '{run_id}' já existe."
        ) from exc

def atualizar_progresso_replay(
    *,
    run_id: str,
    processadas: int,
    last_index: int,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> None:

    agora = (
        datetime.now(
            timezone.utc
        )
        .isoformat()
    )

    with conectar_banco(
        caminho_banco
    ) as conexao:

        conexao.execute(
            """
            UPDATE replay_runs

            SET
                processadas = ?,
                last_index = ?,
                updated_at = ?

            WHERE run_id = ?
            """,
            (
                int(processadas),
                int(last_index),
                agora,
                str(run_id)
            )
        )

def finalizar_run_replay(
    *,
    run_id: str,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> None:

    agora = (
        datetime.now(
            timezone.utc
        )
        .isoformat()
    )

    with conectar_banco(
        caminho_banco
    ) as conexao:

        conexao.execute(
            """
            UPDATE replay_runs

            SET
                status = 'COMPLETED',
                updated_at = ?,
                completed_at = ?

            WHERE run_id = ?
            """,
            (
                agora,
                agora,
                str(run_id)
            )
        )

def falhar_run_replay(
    *,
    run_id: str,
    mensagem: str,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> None:

    agora = (
        datetime.now(
            timezone.utc
        )
        .isoformat()
    )

    with conectar_banco(
        caminho_banco
    ) as conexao:

        conexao.execute(
            """
            UPDATE replay_runs

            SET
                status = 'FAILED',
                updated_at = ?,
                error_message = ?

            WHERE run_id = ?
            """,
            (
                agora,
                str(mensagem),
                str(run_id)
            )
        )

def buscar_run_replay(
    run_id: str,
    caminho_banco: Path = DEFAULT_DB_PATH
) -> dict | None:

    with conectar_banco(
        caminho_banco
    ) as conexao:

        linha = conexao.execute(
            """
            SELECT *
            FROM replay_runs
            WHERE run_id = ?
            """,
            (str(run_id),)
        ).fetchone()

    if linha is None:
        return None

    return dict(
        linha
    )