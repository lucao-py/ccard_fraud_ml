from __future__ import annotations

import pytest

from src.dashboard_queries import (
    buscar_alertas_criticos,
    buscar_detalhe_transacao,
    buscar_execucao_ativa,
    buscar_metricas_comerciais,
    buscar_opcoes_filtros_transacoes,
    buscar_resumo_execucao,
    buscar_transacoes,
    buscar_transacoes_recentes,
    buscar_transacoes_sinalizadas,
    carregar_snapshot_dashboard,
    contar_transacoes_filtradas,
)
from src.persistence import (
    atualizar_progresso_replay,
    falhar_run_replay,
    finalizar_run_replay,
    iniciar_run_replay,
    inicializar_banco,
    salvar_resultado,
)


TRANSACOES = [
    {
        "trans_num": "tx-aprovada-legitima",
        "first": "Ana",
        "last": "Silva",
        "merchant": "Mercado Central",
        "category": "grocery_pos",
        "amt": 100.0,
        "city": "São Paulo",
        "state": "SP",
        "cc_last4": "1001",
        "model_features_json": '{"amt_log":4.62}',
        "score_fraude": 0.10,
        "decisao": "APROVAR",
        "is_fraud": 0,
    },
    {
        "trans_num": "tx-revisao-fraude",
        "first": "Bruno",
        "last": "Costa",
        "merchant": "Loja Online",
        "category": "shopping_net",
        "amt": 200.0,
        "city": "Rio de Janeiro",
        "state": "RJ",
        "cc_last4": "2002",
        "score_fraude": 0.50,
        "decisao": "REVISAR",
        "is_fraud": 1,
    },
    {
        "trans_num": "tx-critica-fraude",
        "first": "Carla",
        "last": "Lima",
        "merchant": "Shopping Digital",
        "category": "shopping_net",
        "amt": 300.0,
        "city": "Rio de Janeiro",
        "state": "RJ",
        "cc_last4": "3003",
        "score_fraude": 0.95,
        "decisao": "ALERTA_CRITICO",
        "is_fraud": 1,
    },
    {
        "trans_num": "tx-revisao-legitima",
        "first": "Diego",
        "last": "Souza",
        "merchant": "Posto Avenida",
        "category": "gas_transport",
        "amt": 50.0,
        "city": "Belo Horizonte",
        "state": "MG",
        "cc_last4": "4004",
        "score_fraude": 0.25,
        "decisao": "REVISAR",
        "is_fraud": 0,
    },
    {
        "trans_num": "tx-aprovada-fraude",
        "first": "Eva",
        "last": "Melo",
        "merchant": "Agência Viagem",
        "category": "travel",
        "amt": 25.0,
        "city": "Campinas",
        "state": "SP",
        "cc_last4": "5005",
        "score_fraude": 0.15,
        "decisao": "APROVAR",
        "is_fraud": 1,
    },
]


def _banco_populado(tmp_path):
    caminho_banco = tmp_path / "dashboard.db"
    inicializar_banco(caminho_banco)
    iniciar_run_replay(
        run_id="run_dashboard",
        total_transacoes=len(TRANSACOES),
        intervalo_segundos=0.0,
        caminho_banco=caminho_banco,
    )

    for indice, transacao in enumerate(TRANSACOES):
        salvar_resultado(
            run_id="run_dashboard",
            trans_date_trans_time=f"2026-08-23T10:0{indice}:00",
            latency_ms=2.0 + indice,
            caminho_banco=caminho_banco,
            **transacao,
        )

    atualizar_progresso_replay(
        run_id="run_dashboard",
        processadas=len(TRANSACOES),
        last_index=len(TRANSACOES) - 1,
        caminho_banco=caminho_banco,
    )
    return caminho_banco


def test_localizacao_automatica_da_execucao(tmp_path) -> None:
    caminho_banco = tmp_path / "runs.db"
    inicializar_banco(caminho_banco)
    assert buscar_execucao_ativa(caminho_banco) is None

    iniciar_run_replay(
        run_id="run_antigo",
        total_transacoes=1,
        intervalo_segundos=0.0,
        caminho_banco=caminho_banco,
    )
    finalizar_run_replay(run_id="run_antigo", caminho_banco=caminho_banco)
    iniciar_run_replay(
        run_id="run_ativo",
        total_transacoes=1,
        intervalo_segundos=0.0,
        caminho_banco=caminho_banco,
    )

    assert buscar_execucao_ativa(caminho_banco)["run_id"] == "run_ativo"

    falhar_run_replay(
        run_id="run_ativo",
        mensagem="interrupção simulada",
        caminho_banco=caminho_banco,
    )
    assert buscar_execucao_ativa(caminho_banco)["run_id"] == "run_ativo"


def test_snapshot_vazio_e_divisoes_seguras(tmp_path) -> None:
    caminho_banco = tmp_path / "vazio.db"
    inicializar_banco(caminho_banco)
    iniciar_run_replay(
        run_id="run_vazio",
        total_transacoes=10,
        intervalo_segundos=0.0,
        caminho_banco=caminho_banco,
    )

    snapshot = carregar_snapshot_dashboard("run_vazio", caminho_banco)
    resumo = snapshot["resumo"]
    comerciais = snapshot["metricas_comerciais"]

    assert resumo["total_processadas"] == 0
    assert resumo["percentual_aprovadas"] == 0.0
    assert comerciais["volume_processado"] == 0.0
    assert comerciais["volume_liberado"] == 0.0
    assert comerciais["valor_revisao"] == 0.0
    assert comerciais["valor_critico"] == 0.0
    assert comerciais["percentual_liberado"] is None
    assert comerciais["cobertura_financeira"] is None
    assert comerciais["friccao_financeira"] is None
    assert snapshot["transacoes_recentes"] == []
    assert snapshot["transacoes_sinalizadas"] == []
    assert snapshot["alertas_criticos"] == []
    assert snapshot["exposicao_por_categoria"] == []
    assert snapshot["evolucao_financeira"] == []


def test_snapshot_operacional_e_metricas_comerciais(tmp_path) -> None:
    caminho_banco = _banco_populado(tmp_path)
    snapshot = carregar_snapshot_dashboard("run_dashboard", caminho_banco)
    resumo = buscar_resumo_execucao("run_dashboard", caminho_banco)
    comerciais = buscar_metricas_comerciais("run_dashboard", caminho_banco)

    assert resumo["total_processadas"] == 5
    assert resumo["aprovadas"] == 2
    assert resumo["revisar"] == 2
    assert resumo["alertas_criticos"] == 1
    assert comerciais["volume_processado"] == 675.0
    assert comerciais["volume_liberado"] == 125.0
    assert comerciais["valor_revisao"] == 250.0
    assert comerciais["valor_critico"] == 300.0
    assert comerciais["exposicao_sinalizada"] == 550.0
    assert comerciais["valor_fraudulento_identificado"] == 500.0
    assert comerciais["valor_fraudulento_nao_interceptado"] == 25.0
    assert comerciais["cobertura_financeira"] == pytest.approx(500 / 525)
    assert comerciais["friccao_financeira"] == pytest.approx(50 / 150)
    assert comerciais["volume_processado"] == pytest.approx(
        comerciais["volume_liberado"]
        + comerciais["valor_revisao"]
        + comerciais["valor_critico"]
    )

    assert len(buscar_transacoes_recentes("run_dashboard", 20, caminho_banco)) == 5
    assert len(buscar_transacoes_sinalizadas("run_dashboard", 20, caminho_banco)) == 3
    assert len(buscar_alertas_criticos("run_dashboard", 20, caminho_banco)) == 1
    recentes = buscar_transacoes_recentes("run_dashboard", 20, caminho_banco)
    por_transacao = {
        linha["trans_num"]: linha
        for linha in recentes
    }
    assert por_transacao["tx-aprovada-legitima"]["model_features_json"] == '{"amt_log":4.62}'
    assert snapshot["exposicao_por_categoria"][0]["category"] == "shopping_net"
    assert snapshot["exposicao_por_categoria"][0]["exposicao_sinalizada"] == 500.0
    assert snapshot["evolucao_financeira"][-1]["exposicao_sinalizada_acumulada"] == 550.0


def test_busca_filtros_opcoes_e_detalhe(tmp_path) -> None:
    caminho_banco = _banco_populado(tmp_path)

    assert len(buscar_transacoes("run_dashboard", caminho_banco=caminho_banco)) == 5
    assert len(buscar_transacoes(
        "run_dashboard",
        decisoes=["REVISAR"],
        caminho_banco=caminho_banco,
    )) == 2
    assert len(buscar_transacoes(
        "run_dashboard",
        categoria="shopping_net",
        caminho_banco=caminho_banco,
    )) == 2
    assert len(buscar_transacoes(
        "run_dashboard",
        estado="RJ",
        caminho_banco=caminho_banco,
    )) == 2
    assert len(buscar_transacoes(
        "run_dashboard",
        busca="Ana Silva",
        caminho_banco=caminho_banco,
    )) == 1
    assert len(buscar_transacoes(
        "run_dashboard",
        score_min=0.9,
        caminho_banco=caminho_banco,
    )) == 1
    assert len(buscar_transacoes(
        "run_dashboard",
        score_max=0.2,
        caminho_banco=caminho_banco,
    )) == 2

    combinadas = buscar_transacoes(
        "run_dashboard",
        decisoes=["REVISAR"],
        categoria="shopping_net",
        estado="RJ",
        score_min=0.2,
        score_max=0.8,
        caminho_banco=caminho_banco,
    )
    assert [linha["trans_num"] for linha in combinadas] == ["tx-revisao-fraude"]
    assert contar_transacoes_filtradas(
        "run_dashboard",
        decisoes=["REVISAR"],
        caminho_banco=caminho_banco,
    ) == 2

    detalhe = buscar_detalhe_transacao(
        "run_dashboard",
        "tx-critica-fraude",
        caminho_banco,
    )
    assert detalhe["score_fraude"] == 0.95
    assert detalhe["decisao"] == "ALERTA_CRITICO"
    assert detalhe["model_version"] == "catboost_v1"
    assert detalhe["policy_version"] == "decision_policy_v1"
    assert "is_fraud" not in detalhe
    assert buscar_detalhe_transacao(
        "run_dashboard",
        "inexistente",
        caminho_banco,
    ) is None

    opcoes = buscar_opcoes_filtros_transacoes("run_dashboard", caminho_banco)
    assert opcoes["categorias"] == [
        "gas_transport",
        "grocery_pos",
        "shopping_net",
        "travel",
    ]
    assert opcoes["estados"] == ["MG", "RJ", "SP"]


def test_decisao_invalida_e_resultado_vazio(tmp_path) -> None:
    caminho_banco = _banco_populado(tmp_path)

    with pytest.raises(ValueError, match="Decisões inválidas"):
        buscar_transacoes(
            "run_dashboard",
            decisoes=["BLOQUEAR"],
            caminho_banco=caminho_banco,
        )

    assert buscar_transacoes(
        "run_dashboard",
        busca="cliente inexistente",
        caminho_banco=caminho_banco,
    ) == []
