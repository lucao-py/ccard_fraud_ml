from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import sqlite3

from src.dashboard_queries import buscar_resumo_execucao
from src.persistence import (
    buscar_run_replay,
    buscar_ultimas_transacoes,
    conectar_banco,
    contar_transacoes,
    iniciar_run_replay,
    inicializar_banco,
    limpar_estado_operacional,
    salvar_resultado,
)


def _iniciar_run(caminho_banco, run_id: str = "run_teste") -> None:
    iniciar_run_replay(
        run_id=run_id,
        total_transacoes=100,
        intervalo_segundos=0.0,
        caminho_banco=caminho_banco,
    )


def test_schema_persistencia_duplicidade_e_limpeza(tmp_path) -> None:
    caminho_banco = tmp_path / "runtime.db"
    inicializar_banco(caminho_banco)
    _iniciar_run(caminho_banco)

    argumentos = {
        "run_id": "run_teste",
        "trans_num": "tx-001",
        "trans_date_trans_time": "2026-08-23T10:00:00",
        "first": "Ana",
        "last": "Silva",
        "merchant": "Loja Exemplo",
        "category": "shopping_net",
        "amt": 149.90,
        "city": "São Paulo",
        "state": "SP",
        "cc_last4": "1234",
        "model_features_json": '{"amt_log":5.01}',
        "score_fraude": 0.42,
        "decisao": "REVISAR",
        "is_fraud": None,
        "latency_ms": 3.5,
        "caminho_banco": caminho_banco,
    }

    assert salvar_resultado(**argumentos) is True
    assert salvar_resultado(**argumentos) is False
    assert contar_transacoes(caminho_banco=caminho_banco) == 1

    ultima = buscar_ultimas_transacoes(
        limite=1,
        run_id="run_teste",
        caminho_banco=caminho_banco,
    )[0]
    assert ultima["trans_num"] == "tx-001"
    assert ultima["decisao"] == "REVISAR"
    assert ultima["score_fraude"] == 0.42
    assert ultima["cc_last4"] == "1234"
    assert ultima["model_features_json"] == '{"amt_log":5.01}'
    assert ultima["model_version"] == "catboost_v1"
    assert buscar_run_replay("run_teste", caminho_banco)["status"] == "RUNNING"

    with conectar_banco(caminho_banco) as conexao:
        schema_antes = {
            linha["name"]: linha["sql"]
            for linha in conexao.execute(
                """
                SELECT name, sql
                FROM sqlite_master
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                """
            )
        }

    limpar_estado_operacional(caminho_banco)

    with conectar_banco(caminho_banco) as conexao:
        schema_depois = {
            linha["name"]: linha["sql"]
            for linha in conexao.execute(
                """
                SELECT name, sql
                FROM sqlite_master
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                """
            )
        }
        sequencia = conexao.execute(
            """
            SELECT seq FROM sqlite_sequence
            WHERE name = 'transacoes_processadas'
            """
        ).fetchone()
        integridade = conexao.execute("PRAGMA integrity_check").fetchone()[0]

    assert contar_transacoes(caminho_banco=caminho_banco) == 0
    assert buscar_run_replay("run_teste", caminho_banco) is None
    assert schema_depois == schema_antes
    assert sequencia is None
    assert integridade == "ok"

    _iniciar_run(caminho_banco, run_id="run_novo")
    assert buscar_run_replay("run_novo", caminho_banco)["status"] == "RUNNING"


def test_schema_existente_recebe_coluna_de_features_sem_perder_dados(tmp_path) -> None:
    caminho_banco = tmp_path / "legado.db"

    with sqlite3.connect(caminho_banco) as conexao:
        conexao.execute("""
            CREATE TABLE transacoes_processadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                trans_num TEXT NOT NULL,
                trans_date_trans_time TEXT NOT NULL,
                score_fraude REAL NOT NULL,
                decisao TEXT NOT NULL,
                is_fraud INTEGER,
                processed_at TEXT NOT NULL,
                latency_ms REAL,
                model_version TEXT NOT NULL,
                policy_version TEXT NOT NULL,
                UNIQUE (run_id, trans_num)
            )
        """)
        conexao.execute("""
            INSERT INTO transacoes_processadas (
                run_id, trans_num, trans_date_trans_time,
                score_fraude, decisao, processed_at,
                model_version, policy_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "run-legado",
            "tx-legada",
            "2026-08-23T10:00:00",
            0.1,
            "APROVAR",
            "2026-08-23T10:00:01",
            "catboost_v1",
            "decision_policy_v1",
        ))

    inicializar_banco(caminho_banco)

    with conectar_banco(caminho_banco) as conexao:
        colunas = {
            linha["name"]
            for linha in conexao.execute(
                "PRAGMA table_info(transacoes_processadas)"
            )
        }
        existente = conexao.execute(
            "SELECT trans_num, model_features_json FROM transacoes_processadas"
        ).fetchone()

    assert "model_features_json" in colunas
    assert existente["trans_num"] == "tx-legada"
    assert existente["model_features_json"] is None


def test_wal_permite_leituras_durante_escritas(tmp_path) -> None:
    caminho_banco = tmp_path / "concorrencia.db"
    inicializar_banco(caminho_banco)
    _iniciar_run(caminho_banco, run_id="run_concorrente")

    def escrever() -> None:
        for indice in range(40):
            salvar_resultado(
                run_id="run_concorrente",
                trans_num=f"tx-{indice:03d}",
                trans_date_trans_time=f"2026-08-23T10:00:{indice:02d}",
                score_fraude=0.1,
                decisao="APROVAR",
                amt=10.0,
                caminho_banco=caminho_banco,
            )

    def ler() -> None:
        for _ in range(40):
            resumo = buscar_resumo_execucao(
                "run_concorrente",
                caminho_banco,
            )
            assert resumo["total_processadas"] >= 0

    with ThreadPoolExecutor(max_workers=2) as executor:
        tarefas = [executor.submit(escrever), executor.submit(ler)]
        for tarefa in tarefas:
            tarefa.result()

    assert contar_transacoes("run_concorrente", caminho_banco) == 40
