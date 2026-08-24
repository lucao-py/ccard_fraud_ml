"""Visão geral operacional do monitoramento."""

from __future__ import annotations

from collections import OrderedDict
import json
from threading import RLock

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from catboost import CatBoostError

from dashboard.ui import (
    categories_card,
    commercial_flow_card,
    detection_area,
    financial_categories_card,
    financial_efficiency_card,
    formatar_moeda,
    formatar_numero,
    formatar_percentual,
    kpi_card,
    page_header,
    quality_card,
    section_head,
    transaction_feed,
)
from src.dashboard_queries import carregar_snapshot_dashboard
from src.features import FEATURES_MODELO
from src.inference import FraudModel


EXPLANATION_CACHE_LIMIT = 2048


@st.cache_resource(show_spinner=False)
def _local_explanation_runtime() -> dict:
    return {
        "modelo": FraudModel(),
        "cache": OrderedDict(),
        "lock": RLock(),
    }


def _ler_features_persistidas(valor) -> dict | None:
    if valor is None:
        return None

    try:
        registro = (
            json.loads(valor)
            if isinstance(valor, str)
            else dict(valor)
        )
    except (TypeError, ValueError, json.JSONDecodeError):
        return None

    if not isinstance(registro, dict):
        return None

    if not set(FEATURES_MODELO).issubset(registro):
        return None

    return {
        feature: registro[feature]
        for feature in FEATURES_MODELO
    }


def _adicionar_explicacoes_locais(
    dataframe: pd.DataFrame,
    run_id: str,
    runtime: dict | None = None
) -> pd.DataFrame:
    """Enriquece só o feed visível e reaproveita explicações por transação."""

    resultado = dataframe.copy()

    if resultado.empty:
        resultado["explicacao_local"] = []
        return resultado

    itens_validos = []

    for posicao, (_, row) in enumerate(
        resultado.iterrows()
    ):
        payload = row.get("model_features_json")
        features = _ler_features_persistidas(
            payload
        )

        if features is None:
            continue

        chave = (
            str(run_id),
            str(row.get("trans_num"))
        )
        itens_validos.append({
            "posicao": posicao,
            "chave": chave,
            "payload": str(payload),
            "features": features,
        })

    explicacoes: list[dict | None] = [
        None
        for _ in range(len(resultado))
    ]

    if not itens_validos:
        resultado["explicacao_local"] = explicacoes
        return resultado

    recurso = (
        runtime
        if runtime is not None
        else _local_explanation_runtime()
    )
    cache: OrderedDict = recurso["cache"]
    lock = recurso["lock"]

    with lock:
        pendentes = []

        for item in itens_validos:
            armazenada = cache.get(
                item["chave"]
            )

            if (
                armazenada is not None
                and armazenada["payload"] == item["payload"]
            ):
                cache.move_to_end(
                    item["chave"]
                )
                explicacoes[item["posicao"]] = (
                    armazenada["explicacao"]
                )
            else:
                pendentes.append(item)

        if pendentes:
            features_lote = pd.DataFrame(
                [item["features"] for item in pendentes],
                columns=FEATURES_MODELO
            )

            try:
                novas = recurso["modelo"].explicar_features(
                    features_lote,
                    top_n=4
                )
            except (
                CatBoostError,
                TypeError,
                ValueError,
                RuntimeError
            ):
                novas = [
                    None
                    for _ in pendentes
                ]

            for item, explicacao in zip(
                pendentes,
                novas
            ):
                explicacoes[item["posicao"]] = explicacao
                cache[item["chave"]] = {
                    "payload": item["payload"],
                    "explicacao": explicacao,
                }
                cache.move_to_end(
                    item["chave"]
                )

        while len(cache) > EXPLANATION_CACHE_LIMIT:
            cache.popitem(last=False)

    resultado["explicacao_local"] = explicacoes
    return resultado


def _build_flagged_timeline(dataframe: pd.DataFrame) -> go.Figure | None:
    if dataframe.empty:
        return None

    evolution = dataframe.copy()
    evolution["trans_date_trans_time"] = pd.to_datetime(
        evolution["trans_date_trans_time"],
        errors="coerce",
    )
    evolution = (
        evolution.dropna(subset=["trans_date_trans_time"])
        .sort_values("trans_date_trans_time")
        .reset_index(drop=True)
    )
    if evolution.empty:
        return None

    evolution["revisao_acumulada"] = (
        evolution["decisao"].eq("REVISAR").astype(int).cumsum()
    )
    evolution["criticos_acumulados"] = (
        evolution["decisao"].eq("ALERTA_CRITICO").astype(int).cumsum()
    )

    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=evolution["trans_date_trans_time"],
        y=evolution["revisao_acumulada"],
        mode="lines+markers",
        name="Revisão",
        line={"color": "#F4BD50", "width": 2.5, "shape": "hv"},
        marker={"size": 5, "color": "#F4BD50"},
        hovertemplate="<b>Revisão</b><br>%{y} acumuladas<extra></extra>",
    ))
    figure.add_trace(go.Scatter(
        x=evolution["trans_date_trans_time"],
        y=evolution["criticos_acumulados"],
        mode="lines+markers",
        name="Alertas críticos",
        line={"color": "#FB7185", "width": 2.8, "shape": "hv"},
        marker={"size": 6, "color": "#FB7185"},
        hovertemplate="<b>Críticos</b><br>%{y} acumulados<extra></extra>",
    ))
    figure.update_layout(
        height=380,
        margin={"l": 48, "r": 18, "t": 96, "b": 48},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        title={
            "text": (
                "Evolução recente das sinalizações"
                "<br><span style='font-size:10px;color:#596274'>"
                "Acumulado das operações encaminhadas"
                "</span>"
            ),
            "x": 0.035,
            "xanchor": "left",
            "y": 0.95,
            "yanchor": "top",
            "font": {"color": "#F4F6FB", "size": 14},
        },
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": 0.82,
            "xanchor": "right",
            "x": 0.99,
            "font": {"color": "#8B94A7", "size": 9},
        },
        xaxis={
            "showgrid": False,
            "zeroline": False,
            "tickformat": "%H:%M<br>%d/%m",
            "tickfont": {"color": "#596274", "size": 9},
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "rgba(255,255,255,.04)",
            "zeroline": False,
            "rangemode": "tozero",
            "tickfont": {"color": "#596274", "size": 9},
            "dtick": 1,
            "title": {
                "text": "Acumulado",
                "font": {"color": "#596274", "size": 9},
            },
        },
        hoverlabel={
            "bgcolor": "#151A24",
            "bordercolor": "rgba(255,255,255,.08)",
            "font_color": "#F4F6FB",
        },
    )
    return figure


def _build_financial_timeline(dataframe: pd.DataFrame) -> go.Figure | None:
    if dataframe.empty:
        return None

    evolution = dataframe.copy()
    evolution["momento"] = pd.to_datetime(
        evolution["momento"],
        errors="coerce",
        utc=True,
    ).dt.tz_convert("America/Sao_Paulo")
    evolution = evolution.dropna(subset=["momento"])
    if evolution.empty:
        return None

    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=evolution["momento"],
        y=evolution["exposicao_sinalizada_acumulada"],
        mode="lines",
        name="Exposição sinalizada",
        line={"color": "#9567F5", "width": 3},
        fill="tozeroy",
        fillcolor="rgba(149,103,245,.09)",
        hovertemplate="<b>Exposição sinalizada</b><br>US$ %{y:,.2f}<extra></extra>",
    ))
    figure.add_trace(go.Scatter(
        x=evolution["momento"],
        y=evolution["valor_critico_acumulado"],
        mode="lines",
        name="Exposição crítica",
        line={"color": "#FB7185", "width": 2.2},
        hovertemplate="<b>Exposição crítica</b><br>US$ %{y:,.2f}<extra></extra>",
    ))
    figure.update_layout(
        height=360,
        margin={"l": 62, "r": 18, "t": 92, "b": 48},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        title={
            "text": (
                "Evolução da exposição"
                "<br><span style='font-size:10px;color:#596274'>"
                "Valor sinalizado acumulado ao longo do processamento"
                "</span>"
            ),
            "x": 0.035,
            "xanchor": "left",
            "y": 0.95,
            "yanchor": "top",
            "font": {"color": "#F4F6FB", "size": 14},
        },
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": 0.82,
            "xanchor": "right",
            "x": 0.99,
            "font": {"color": "#8B94A7", "size": 9},
        },
        xaxis={
            "showgrid": False,
            "zeroline": False,
            "tickformat": "%H:%M",
            "tickfont": {"color": "#596274", "size": 9},
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "rgba(255,255,255,.04)",
            "zeroline": False,
            "rangemode": "tozero",
            "tickprefix": "US$ ",
            "tickformat": ",.0f",
            "tickfont": {"color": "#596274", "size": 9},
        },
        hoverlabel={
            "bgcolor": "#151A24",
            "bordercolor": "rgba(255,255,255,.08)",
            "font_color": "#F4F6FB",
        },
    )
    return figure


@st.fragment(run_every="2s")
def render_overview_page(run_id: str) -> None:
    snapshot = carregar_snapshot_dashboard(run_id)
    replay = snapshot.get("replay") or {}
    resumo = snapshot.get("resumo") or {}
    fraudes = snapshot.get("fraudes") or {}
    valores = snapshot.get("valores") or {}

    recentes = pd.DataFrame(snapshot.get("transacoes_recentes") or [])
    sinalizadas = pd.DataFrame(snapshot.get("transacoes_sinalizadas") or [])
    criticas = pd.DataFrame(snapshot.get("alertas_criticos") or [])
    categorias = pd.DataFrame(snapshot.get("top_categorias_risco") or [])
    metricas_comerciais = snapshot.get("metricas_comerciais") or {}
    evolucao_financeira = pd.DataFrame(snapshot.get("evolucao_financeira") or [])
    exposicao_por_categoria = pd.DataFrame(snapshot.get("exposicao_por_categoria") or [])

    st.html(page_header(
        eyebrow="Monitoramento de fraudes",
        title="Inteligência de Transações",
        subtitle="Volume, decisões operacionais e operações que exigem atenção — em uma leitura contínua do fluxo transacional.",
        status=replay.get("status"),
        model_version=replay.get("model_version"),
        policy_version=replay.get("policy_version"),
    ))

    total = int(resumo.get("total_processadas") or 0)
    approved = int(resumo.get("aprovadas") or 0)
    review = int(resumo.get("revisar") or 0)
    critical = int(resumo.get("alertas_criticos") or 0)

    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1:
        st.html(kpi_card(
            "TRANSAÇÕES PROCESSADAS",
            formatar_numero(total),
            "Volume total analisado",
            "▣",
        ))
    with k2:
        st.html(kpi_card(
            "APROVADAS",
            formatar_numero(approved),
            f"{float(resumo.get('percentual_aprovadas') or 0) * 100:.2f}% do total",
            "✓",
        ))
    with k3:
        st.html(kpi_card(
            "EM REVISÃO",
            formatar_numero(review),
            f"{float(resumo.get('percentual_revisar') or 0) * 100:.3f}% das transações",
            "◇",
            "review",
        ))
    with k4:
        st.html(kpi_card(
            "ALERTAS CRÍTICOS",
            formatar_numero(critical),
            f"{float(resumo.get('percentual_criticos') or 0) * 100:.3f}% do volume",
            "!",
            "critical",
        ))

    st.html('<div class="spacer-22"></div>')
    st.html(section_head(
        "Última Detecção",
        "Operação sinalizada mais recente e contexto dos alertas anteriores",
        "Atualização automática · 2 s",
    ))
    st.html(detection_area(sinalizadas))

    st.html('<div class="spacer-28"></div>')
    header_col, control_col = st.columns([2.15, 1], gap="medium", vertical_alignment="bottom")
    with header_col:
        st.html(section_head(
            "Fluxo de Transações",
            "Operações mais recentes, com risco e decisão em uma única leitura",
        ))
    with control_col:
        feed_filter = st.segmented_control(
            "Recorte do fluxo",
            ["Todas", "Sinalizadas", "Críticas"],
            default="Todas",
            key=f"overview_feed_{run_id}",
            label_visibility="collapsed",
            width="stretch",
        ) or "Todas"

    if feed_filter == "Sinalizadas":
        feed = sinalizadas
    elif feed_filter == "Críticas":
        feed = criticas
    else:
        feed = recentes
    feed = _adicionar_explicacoes_locais(
        feed.head(14),
        run_id=run_id
    )
    st.html(transaction_feed(feed))

    st.html('<div class="spacer-28"></div>')
    st.html(section_head(
        "Análise Operacional",
        "Evolução temporal, qualidade da triagem e concentração do risco",
    ))
    timeline_col, quality_col, category_col = st.columns(
        [1.75, .92, 1.08],
        gap="large",
        vertical_alignment="top",
    )

    with timeline_col:
        timeline = _build_flagged_timeline(sinalizadas)
        if timeline is None:
            st.html(
                '<div class="empty-state timeline-empty">'
                "Aguardando as primeiras sinalizações."
                "</div>"
            )
        else:
            st.plotly_chart(
                timeline,
                width="stretch",
                theme=None,
                config={"displayModeBar": False},
                key=f"flagged_timeline_{run_id}",
            )

    with quality_col:
        st.html(quality_card(fraudes, resumo, valores))

    with category_col:
        st.html(categories_card(categorias))

    st.html('<div class="spacer-28"></div>')
    st.html(section_head(
        "Análise Comercial",
        "Impacto financeiro, exposição e eficiência econômica da política",
        "Atualização automática · 2 s",
    ))

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        st.html(kpi_card(
            "VOLUME PROCESSADO",
            formatar_moeda(metricas_comerciais.get("volume_processado")),
            "Volume transacionado analisado",
            "▣",
            "commercial-kpi commercial-volume",
        ))
    with c2:
        st.html(kpi_card(
            "VOLUME LIBERADO",
            formatar_moeda(metricas_comerciais.get("volume_liberado")),
            f"{formatar_percentual(metricas_comerciais.get('percentual_liberado'), 1)} do volume processado",
            "✓",
            "commercial-kpi released",
        ))
    with c3:
        st.html(kpi_card(
            "VALOR SOB REVISÃO",
            formatar_moeda(metricas_comerciais.get("valor_revisao")),
            "Aguardando análise",
            "◇",
            "commercial-kpi review",
        ))
    with c4:
        st.html(kpi_card(
            "EXPOSIÇÃO CRÍTICA",
            formatar_moeda(metricas_comerciais.get("valor_critico")),
            "Operações de risco máximo",
            "!",
            "commercial-kpi critical",
        ))

    st.html('<div class="spacer-22"></div>')
    flow_col, efficiency_col = st.columns(
        [1.55, 1],
        gap="large",
        vertical_alignment="top",
    )
    with flow_col:
        st.html(commercial_flow_card(metricas_comerciais))
    with efficiency_col:
        st.html(financial_efficiency_card(metricas_comerciais))

    st.html('<div class="spacer-16"></div>')
    evolution_col, exposure_col = st.columns(
        [1.65, 1],
        gap="large",
        vertical_alignment="top",
    )
    with evolution_col:
        financial_timeline = _build_financial_timeline(evolucao_financeira)
        if financial_timeline is None:
            st.html(
                '<div class="empty-state commercial-timeline-empty">'
                "Aguardando volume sinalizado para formar a evolução financeira."
                "</div>"
            )
        else:
            st.plotly_chart(
                financial_timeline,
                width="stretch",
                theme=None,
                config={"displayModeBar": False},
                key=f"financial_timeline_{run_id}",
            )
    with exposure_col:
        st.html(financial_categories_card(exposicao_por_categoria))
