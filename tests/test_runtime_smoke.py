from __future__ import annotations

from collections import OrderedDict
import json
from threading import RLock

import pandas as pd
import pytest

import main
from dashboard.styles import APP_CSS
from dashboard.ui import (
    categories_card,
    commercial_flow_card,
    detection_area,
    financial_categories_card,
    financial_efficiency_card,
    quality_card,
    transaction_feed,
)
from dashboard.views.overview import (
    _adicionar_explicacoes_locais,
    _build_financial_timeline,
    _build_flagged_timeline,
)
from src.decision_policy import DecisionPolicy
from src.features import FEATURES_MODELO
from src.inference import FraudModel, resumir_contribuicoes_shap
from src.persistence import buscar_ultimas_transacoes, inicializar_banco
from src.transaction_processor import TransactionProcessor


class _ModeloStub:
    def prever_scores_com_features(self, _transacao):
        features = pd.DataFrame([{
            "amt_log": 1.0,
            "city_pop_log": 2.0,
            "idade": 35,
            "distancia_km": 4.0,
            "hora_sin": 0.5,
            "hora_cos": 0.5,
            "dia_semana_sin": 0.2,
            "dia_semana_cos": 0.8,
            "fim_de_semana": 0,
            "category": "shopping_net",
            "gender": "F",
            "state": "SP",
        }], columns=FEATURES_MODELO)
        return [0.42], features


class _ModeloExplicacaoStub:
    def __init__(self):
        self.chamadas: list[list[float]] = []

    def explicar_features(self, features, top_n=4):
        self.chamadas.append(
            features["amt_log"].tolist()
        )
        return [
            {
                "fatores": [{
                    "feature": f"Valor {valor}",
                    "impacto": float(valor),
                    "direcao": "aumenta",
                }]
            }
            for valor in features["amt_log"]
        ]


class _PoliticaStub:
    def decidir(self, _score: float) -> str:
        return "REVISAR"


def test_componentes_dashboard_suportam_estado_vazio() -> None:
    vazio = pd.DataFrame()
    metricas = {
        "volume_processado": 0.0,
        "volume_liberado": 0.0,
        "valor_revisao": 0.0,
        "valor_critico": 0.0,
        "valor_fraudulento_identificado": 0.0,
        "valor_fraudulento_nao_interceptado": 0.0,
        "cobertura_financeira": None,
        "friccao_financeira": None,
        "taxa_retencao_financeira": None,
    }

    componentes = [
        detection_area(vazio),
        transaction_feed(vazio),
        categories_card(vazio),
        financial_categories_card(vazio),
        commercial_flow_card(metricas),
        financial_efficiency_card(metricas),
        quality_card({}, {}, {}),
    ]

    assert _build_flagged_timeline(vazio) is None
    assert _build_financial_timeline(vazio) is None
    assert all("None" not in componente for componente in componentes)
    assert all("us$ nan" not in componente.lower() for componente in componentes)
    assert all(">nan<" not in componente.lower() for componente in componentes)
    assert all(">nan%" not in componente.lower() for componente in componentes)
    assert "Nenhuma operação sinalizada" in componentes[0]
    assert "Nenhuma transação encontrada" in componentes[1]


def test_processador_suporta_transacao_sem_rotulo_historico(tmp_path) -> None:
    caminho_banco = tmp_path / "processor.db"
    inicializar_banco(caminho_banco)

    processador = TransactionProcessor.__new__(TransactionProcessor)
    processador.caminho_banco = caminho_banco
    processador.modelo = _ModeloStub()
    processador.politica = _PoliticaStub()

    transacao = pd.DataFrame([{
        "trans_num": "tx-sem-rotulo",
        "trans_date_trans_time": pd.Timestamp("2026-08-23 10:00:00"),
        "first": "Ana",
        "last": "Silva",
        "merchant": "Loja",
        "category": "shopping_net",
        "amt": 80.0,
        "city": "São Paulo",
        "state": "SP",
        "cc_num": "1234567890123456",
    }])

    resultado = processador.processar_transacao(
        transacao=transacao,
        run_id="run_sem_rotulo",
    )

    assert resultado["is_fraud"] is None
    assert resultado["score_fraude"] == 0.42
    assert resultado["decisao"] == "REVISAR"
    assert resultado["persistido"] is True
    persistida = buscar_ultimas_transacoes(
        limite=1,
        run_id="run_sem_rotulo",
        caminho_banco=caminho_banco,
    )[0]
    assert persistida["is_fraud"] is None
    assert json.loads(persistida["model_features_json"])["amt_log"] == 1.0


def test_politica_e_tooltip_exibem_score_thresholds_e_fatores() -> None:
    politica = DecisionPolicy()
    assert politica.descrever_regra("APROVAR") == "Score < 20%"
    assert politica.descrever_regra("REVISAR") == "Entre 20% e 90%"
    assert politica.descrever_regra("ALERTA_CRITICO") == "Score ≥ 90%"

    explicacao = {
        "fatores": [
            {"feature": "Valor da transação", "impacto": 1.2, "direcao": "aumenta"},
            {"feature": "Distância do estabelecimento", "impacto": -0.6, "direcao": "reduz"},
        ]
    }
    feed = pd.DataFrame([
        {"trans_num": "a", "score_fraude": 0.043, "decisao": "APROVAR", "explicacao_local": explicacao},
        {"trans_num": "b", "score_fraude": 0.752, "decisao": "REVISAR", "explicacao_local": explicacao},
        {"trans_num": "c", "score_fraude": 0.958, "decisao": "ALERTA_CRITICO", "explicacao_local": explicacao},
    ])

    componente = transaction_feed(feed)

    assert "4,3%" in componente
    assert "75,2%" in componente
    assert "95,8%" in componente
    assert "Score &lt; 20%" in componente
    assert "Entre 20% e 90%" in componente
    assert "Score ≥ 90%" in componente
    assert "Valor da transação" in componente
    assert "Distância do estabelecimento" in componente
    assert "↑ aumenta o score" in componente
    assert "↓ reduz o score" in componente
    assert "is_fraud" not in componente


def test_tooltip_tem_fallback_e_css_preserva_scroll() -> None:
    componente = transaction_feed(pd.DataFrame([{
        "trans_num": "sem-explicacao",
        "score_fraude": 0.1,
        "decisao": "APROVAR",
    }]))

    assert "Explicação local ainda não disponível" in componente
    assert "role=\"tooltip\"" in componente
    assert "overflow-y: auto" in APP_CSS
    assert "position: fixed" in APP_CSS
    assert "z-index: 10000" in APP_CSS
    assert "tbody tr:hover .decision-explanation" in APP_CSS


def test_contribuicoes_agregam_features_ciclicas_e_preservam_sinal() -> None:
    contribuicoes = [
        0.1,
        -0.2,
        0.05,
        -0.7,
        0.4,
        -0.1,
        0.08,
        0.12,
        0.01,
        0.6,
        0.02,
        0.03,
    ]

    fatores = resumir_contribuicoes_shap(
        contribuicoes,
        top_n=5
    )
    por_nome = {
        fator["feature"]: fator
        for fator in fatores
    }

    assert por_nome["Horário da transação"]["impacto"] == pytest.approx(0.3)
    assert por_nome["Horário da transação"]["direcao"] == "aumenta"
    assert por_nome["Distância do estabelecimento"]["direcao"] == "reduz"
    assert all("_sin" not in fator["feature"] for fator in fatores)
    assert all("_cos" not in fator["feature"] for fator in fatores)
    assert [abs(fator["impacto"]) for fator in fatores] == sorted(
        [abs(fator["impacto"]) for fator in fatores],
        reverse=True
    )


def test_cache_shap_mapeia_transacao_e_calcula_somente_pendentes() -> None:
    modelo = _ModeloExplicacaoStub()
    runtime = {
        "modelo": modelo,
        "cache": OrderedDict(),
        "lock": RLock(),
    }

    def payload(valor: float) -> str:
        registro = {
            feature: 0.0
            for feature in FEATURES_MODELO
        }
        registro.update({
            "amt_log": valor,
            "category": "shopping_net",
            "gender": "F",
            "state": "SP",
        })
        return json.dumps(registro)

    primeiro_feed = pd.DataFrame([
        {"trans_num": "tx-1", "model_features_json": payload(1.0)},
        {"trans_num": "tx-2", "model_features_json": payload(2.0)},
    ])
    primeiro = _adicionar_explicacoes_locais(
        primeiro_feed,
        run_id="run-cache",
        runtime=runtime
    )
    segundo = _adicionar_explicacoes_locais(
        primeiro_feed,
        run_id="run-cache",
        runtime=runtime
    )

    assert modelo.chamadas == [[1.0, 2.0]]
    assert primeiro.iloc[0]["explicacao_local"]["fatores"][0]["feature"] == "Valor 1.0"
    assert primeiro.iloc[1]["explicacao_local"]["fatores"][0]["feature"] == "Valor 2.0"
    assert segundo["explicacao_local"].tolist() == primeiro["explicacao_local"].tolist()

    terceiro_feed = pd.DataFrame([
        {"trans_num": "tx-2", "model_features_json": payload(2.0)},
        {"trans_num": "tx-3", "model_features_json": payload(3.0)},
    ])
    _adicionar_explicacoes_locais(
        terceiro_feed,
        run_id="run-cache",
        runtime=runtime
    )
    assert modelo.chamadas == [[1.0, 2.0], [3.0]]


def test_shap_nativo_corresponde_ao_vetor_persistido() -> None:
    transacoes = pd.read_csv(
        "raw/fraudTrain.csv",
        nrows=2
    )
    modelo = FraudModel()
    scores, features = modelo.prever_scores_com_features(
        transacoes
    )
    persistidas = pd.DataFrame([
        json.loads(
            row.to_json(
                force_ascii=False,
                double_precision=15
            )
        )
        for _, row in features.iterrows()
    ], columns=FEATURES_MODELO)

    explicacoes_lote = modelo.explicar_features(
        persistidas,
        top_n=4
    )
    explicacao_individual = modelo.explicar_features(
        persistidas.head(1),
        top_n=4
    )[0]

    assert len(scores) == 2
    assert len(explicacoes_lote) == 2
    for fator_lote, fator_individual in zip(
        explicacoes_lote[0]["fatores"],
        explicacao_individual["fatores"]
    ):
        assert fator_lote["feature"] == fator_individual["feature"]
        assert fator_lote["direcao"] == fator_individual["direcao"]
        assert fator_lote["impacto"] == pytest.approx(
            fator_individual["impacto"]
        )
    assert all(len(item["fatores"]) == 4 for item in explicacoes_lote)
    assert all(
        fator["direcao"] == (
            "aumenta"
            if fator["impacto"] > 0
            else "reduz"
            if fator["impacto"] < 0
            else "neutro"
        )
        for item in explicacoes_lote
        for fator in item["fatores"]
    )


def test_lock_impede_dupla_inicializacao_e_eh_reutilizavel(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(main, "LOCK_PATH", tmp_path / ".main.lock")

    primeiro = main._adquirir_lock_sistema()
    try:
        assert primeiro is not None
        assert main._adquirir_lock_sistema() is None
    finally:
        main._liberar_lock_sistema(primeiro)

    segundo = main._adquirir_lock_sistema()
    assert segundo is not None
    main._liberar_lock_sistema(segundo)
