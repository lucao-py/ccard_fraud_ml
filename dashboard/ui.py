"""Formatação e componentes HTML compartilhados pelas páginas."""

from __future__ import annotations

from datetime import datetime
import html
import json
import math

import pandas as pd

from src.decision_policy import DecisionPolicy


POLITICA_DECISAO = DecisionPolicy()


CATEGORIAS_PT = {
    "gas_transport": "Combustível e transporte",
    "grocery_pos": "Mercado presencial",
    "grocery_net": "Mercado online",
    "shopping_net": "Compras online",
    "shopping_pos": "Compras presenciais",
    "misc_net": "Outros online",
    "misc_pos": "Outros presenciais",
    "food_dining": "Alimentação",
    "entertainment": "Entretenimento",
    "health_fitness": "Saúde e fitness",
    "home": "Casa",
    "kids_pets": "Crianças e pets",
    "personal_care": "Cuidados pessoais",
    "travel": "Viagens",
}


def valor_ausente(valor) -> bool:
    try:
        return bool(pd.isna(valor))
    except Exception:
        return valor is None


def texto_seguro(valor, padrao: str = "—") -> str:
    if valor is None or valor_ausente(valor):
        return padrao
    return str(valor)


def formatar_numero(valor) -> str:
    if valor is None or valor_ausente(valor):
        return "—"
    return f"{int(valor):,}".replace(",", ".")


def formatar_percentual(valor, casas: int = 1) -> str:
    if valor is None or valor_ausente(valor):
        return "—"
    return f"{float(valor) * 100:.{casas}f}%".replace(".", ",")


def formatar_score(valor, casas: int = 2) -> str:
    if valor is None or valor_ausente(valor):
        return "—"
    return f"{float(valor) * 100:.{casas}f}%".replace(".", ",")


def formatar_moeda(valor) -> str:
    if valor is None or valor_ausente(valor):
        return "—"
    numero = f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"US$ {numero}"


def formatar_moeda_compacta(valor) -> str:
    if valor is None or valor_ausente(valor):
        return "—"
    numero = float(valor)
    absoluto = abs(numero)
    if absoluto >= 1_000_000:
        return f"US$ {numero / 1_000_000:.2f} mi".replace(".", ",")
    if absoluto >= 1_000:
        return f"US$ {numero / 1_000:.1f} mil".replace(".", ",")
    return formatar_moeda(numero)


def formatar_categoria(valor) -> str:
    texto = texto_seguro(valor)
    if texto == "—":
        return texto
    return CATEGORIAS_PT.get(texto, texto.replace("_", " ").title())


def limpar_merchant(valor) -> str:
    texto = texto_seguro(valor)
    return texto[6:] if texto.startswith("fraud_") else texto


def formatar_data_hora(valor, incluir_data: bool = False) -> str:
    if valor is None or valor_ausente(valor):
        return "—"
    try:
        data = pd.to_datetime(valor)
        formato = "%d/%m/%Y · %H:%M:%S" if incluir_data else "%H:%M:%S"
        return data.strftime(formato)
    except Exception:
        return str(valor)


def formatar_run(run: dict) -> str:
    inicio = run.get("started_at")
    try:
        data = pd.to_datetime(inicio).tz_convert("America/Sao_Paulo")
        return f"Janela de {data.strftime('%d/%m · %H:%M')}"
    except Exception:
        return "Janela monitorada"


def status_info(status: str | None) -> tuple[str, str]:
    mapa = {
        "RUNNING": ("AO VIVO", "live"),
        "COMPLETED": ("ATUALIZADO", ""),
        "FAILED": ("INDISPONÍVEL", "failed"),
    }
    return mapa.get(status or "", ("STATUS INDEFINIDO", "failed"))


def decision_info(decisao: str | None) -> tuple[str, str, str]:
    mapa = {
        "APROVAR": ("APROVADA", "approved", "#4ade80"),
        "REVISAR": ("REVISAR", "review", "#f4bd50"),
        "ALERTA_CRITICO": ("ALERTA CRÍTICO", "critical", "#fb7185"),
    }
    return mapa.get(decisao or "", (texto_seguro(decisao), "approved", "#9aabff"))


def nome_cliente(row: dict | pd.Series) -> str:
    first = texto_seguro(row.get("first"), "").strip()
    last = texto_seguro(row.get("last"), "").strip()
    return f"{first} {last}".strip() or "Cliente não identificado"


def localizacao(row: dict | pd.Series) -> str:
    city = texto_seguro(row.get("city"), "").strip()
    state = texto_seguro(row.get("state"), "").strip()
    if city and state:
        return f"{city} · {state}"
    return city or state or "—"


def page_header(
    *,
    eyebrow: str,
    title: str,
    subtitle: str,
    status: str | None,
    model_version: str | None,
    policy_version: str | None,
) -> str:
    status_label, status_class = status_info(status)
    agora = datetime.now().strftime("%H:%M:%S")
    return f"""
    <div class="page-header">
        <div>
            <div class="page-eyebrow">{html.escape(eyebrow)}</div>
            <h1 class="page-title">{html.escape(title)}</h1>
            <div class="page-subtitle">{html.escape(subtitle)}</div>
        </div>
        <div class="header-meta">
            <div class="status-pill {status_class}">
                <span class="status-dot"></span>{html.escape(status_label)}
            </div>
            <div class="header-version">
                {html.escape(texto_seguro(model_version))} · {html.escape(texto_seguro(policy_version))}<br>
                Atualizado às {agora}
            </div>
        </div>
    </div>
    """


def section_head(title: str, description: str, meta: str | None = None) -> str:
    meta_html = f'<div class="section-meta">{html.escape(meta)}</div>' if meta else ""
    return f"""
    <div class="section-head">
        <div>
            <div class="section-title">{html.escape(title)}</div>
            <div class="section-description">{html.escape(description)}</div>
        </div>
        {meta_html}
    </div>
    """


def kpi_card(label: str, value: str, detail: str, icon: str, tone: str = "") -> str:
    return f"""
    <div class="kpi-card {tone}">
        <div class="kpi-top">
            <div class="kpi-icon">{html.escape(icon)}</div>
            <span class="kpi-accent"></span>
        </div>
        <div class="kpi-label">{html.escape(label)}</div>
        <div class="kpi-value">{html.escape(value)}</div>
        <div class="kpi-detail">{html.escape(detail)}</div>
    </div>
    """


def _detection_card(row: dict | pd.Series, principal: bool) -> str:
    decision_label, decision_class, _ = decision_info(row.get("decisao"))
    score = float(row.get("score_fraude") or 0)
    merchant = limpar_merchant(row.get("merchant"))
    category = formatar_categoria(row.get("category"))
    if principal:
        return f"""
        <div class="latest-detection {'critical' if decision_class == 'critical' else ''}">
            <div class="latest-top">
                <span class="decision-badge {decision_class}">{html.escape(decision_label)}</span>
                <div>
                    <div class="latest-score">{html.escape(formatar_score(score))}</div>
                    <div class="score-caption">score de risco</div>
                </div>
            </div>
            <div class="latest-name">{html.escape(nome_cliente(row))}</div>
            <div class="latest-merchant">{html.escape(merchant)} · {html.escape(category)}</div>
            <div class="detail-chips">
                <span class="detail-chip"><strong>{html.escape(formatar_moeda(row.get('amt')))}</strong></span>
                <span class="detail-chip">{html.escape(localizacao(row))}</span>
                <span class="detail-chip">{html.escape(formatar_data_hora(row.get('trans_date_trans_time')))}</span>
            </div>
        </div>
        """
    return f"""
    <div class="recent-card">
        <div class="recent-top">
            <span class="decision-badge {decision_class}">{html.escape(decision_label)}</span>
            <span class="recent-score">{html.escape(formatar_score(score))}</span>
        </div>
        <div class="recent-name">{html.escape(nome_cliente(row))}</div>
        <div class="recent-meta">{html.escape(category)} · {html.escape(formatar_moeda(row.get('amt')))}</div>
    </div>
    """


def detection_area(dataframe: pd.DataFrame) -> str:
    if dataframe.empty:
        return """
        <div class="detection-shell">
            <div class="empty-state">
                Nenhuma operação sinalizada até o momento.<br>
                Novas operações em revisão ou alerta crítico aparecerão aqui automaticamente.
            </div>
        </div>
        """
    principal = _detection_card(dataframe.iloc[0], principal=True)
    anteriores = [_detection_card(dataframe.iloc[i], principal=False) for i in range(1, min(3, len(dataframe)))]
    while len(anteriores) < 2:
        anteriores.append('<div class="recent-card" style="display:grid;place-items:center;color:#596274;font-size:.58rem">Aguardando nova sinalização</div>')
    return f"""
    <div class="detection-shell">
        <div class="detection-grid">
            {principal}
            <div class="recent-stack">{''.join(anteriores)}</div>
        </div>
    </div>
    """


def _normalizar_explicacao_local(valor) -> dict | None:
    if valor is None:
        return None

    if isinstance(valor, dict):
        return valor

    if isinstance(valor, str):
        try:
            explicacao = json.loads(valor)
            return explicacao if isinstance(explicacao, dict) else None
        except (ValueError, json.JSONDecodeError):
            return None

    return None


def _tooltip_explicacao(
    row: dict | pd.Series,
    *,
    indice: int,
    score: float,
    decision_label: str,
    decision_class: str
) -> str:
    explicacao = _normalizar_explicacao_local(
        row.get("explicacao_local")
    )
    fatores_brutos = (
        explicacao.get("fatores", [])
        if explicacao
        else []
    )
    fatores = []

    for fator in fatores_brutos[:5]:
        try:
            impacto = float(fator.get("impacto"))
        except (TypeError, ValueError, AttributeError):
            continue

        if not math.isfinite(impacto):
            continue

        if impacto > 0:
            direcao = "aumenta"
            seta = "↑"
        elif impacto < 0:
            direcao = "reduz"
            seta = "↓"
        else:
            direcao = "neutro"
            seta = "•"

        fatores.append({
            "feature": texto_seguro(fator.get("feature")),
            "impacto": impacto,
            "direcao": direcao,
            "seta": seta,
        })

    max_impacto = max(
        (
            abs(fator["impacto"])
            for fator in fatores
        ),
        default=0.0
    )
    linhas_fatores = []

    for fator in fatores:
        largura = (
            abs(fator["impacto"])
            / max_impacto
            * 100
            if max_impacto > 0
            else 0
        )
        linhas_fatores.append(f"""
        <div class="explanation-factor {fator['direcao']}">
            <span class="explanation-arrow">{fator['seta']}</span>
            <span class="explanation-feature">{html.escape(fator['feature'])}</span>
            <span class="explanation-track">
                <span class="explanation-fill" style="width:{largura:.2f}%"></span>
            </span>
        </div>
        """)

    if linhas_fatores:
        fatores_html = "".join(linhas_fatores)
    else:
        fatores_html = """
        <div class="explanation-empty">
            Explicação local ainda não disponível para esta operação.
        </div>
        """

    decisao = texto_seguro(
        row.get("decisao"),
        ""
    )
    regra = POLITICA_DECISAO.descrever_regra(
        decisao
    )
    tooltip_id = f"decision-explanation-{indice}"
    anchor_name = f"--risk-anchor-{indice}"

    return f"""
    <div class="risk-explainer" tabindex="0"
         aria-describedby="{tooltip_id}"
         style="anchor-name:{anchor_name}">
        <div class="risk-line">
            <span class="risk-number tone-{decision_class}">{html.escape(formatar_score(score, 1))}</span>
            <span class="risk-track"><span class="risk-fill tone-{decision_class}" style="display:block;width:{max(2, score * 100):.2f}%"></span></span>
        </div>
        <div class="risk-decision"><span class="decision-badge {decision_class}">{html.escape(decision_label)}</span></div>
        <div id="{tooltip_id}" class="decision-explanation" role="tooltip"
             style="position-anchor:{anchor_name}">
            <div class="explanation-eyebrow">Por que essa decisão?</div>
            <div class="explanation-score-row">
                <span>Score de risco</span>
                <strong>{html.escape(formatar_score(score, 1))}</strong>
            </div>
            <div class="explanation-policy {decision_class}">
                <span class="explanation-policy-label">{html.escape(decision_label)}</span>
                <span>{html.escape(regra)}</span>
            </div>
            <div class="explanation-divider"></div>
            <div class="explanation-subtitle">Fatores que mais influenciaram o score</div>
            <div class="explanation-factors">{fatores_html}</div>
            <div class="explanation-legend">
                <span class="aumenta">↑ aumenta o score</span>
                <span class="reduz">↓ reduz o score</span>
            </div>
        </div>
    </div>
    """


def transaction_feed(dataframe: pd.DataFrame) -> str:
    if dataframe.empty:
        return '<div class="empty-state">Nenhuma transação encontrada para este recorte.</div>'
    rows: list[str] = []
    for indice, (_, row) in enumerate(dataframe.iterrows()):
        decision_label, decision_class, _ = decision_info(row.get("decisao"))
        score = float(row.get("score_fraude") or 0)
        explicacao = _tooltip_explicacao(
            row,
            indice=indice,
            score=score,
            decision_label=decision_label,
            decision_class=decision_class
        )
        rows.append(f"""
        <tr>
            <td class="feed-time">{html.escape(formatar_data_hora(row.get('trans_date_trans_time')))}</td>
            <td>
                <div class="feed-primary">{html.escape(nome_cliente(row))}</div>
                <div class="feed-secondary">•••• {html.escape(texto_seguro(row.get('cc_last4'), '----'))} · {html.escape(localizacao(row))}</div>
            </td>
            <td>
                <div class="feed-primary">{html.escape(limpar_merchant(row.get('merchant')))}</div>
                <div class="feed-secondary">{html.escape(formatar_categoria(row.get('category')))}</div>
            </td>
            <td class="feed-amount">{html.escape(formatar_moeda(row.get('amt')))}</td>
            <td>{explicacao}</td>
        </tr>
        """)
    return f"""
    <div class="feed-shell">
        <div class="feed-scroll">
            <table class="feed-table">
                <thead><tr>
                    <th style="width:12%">HORÁRIO</th>
                    <th style="width:27%">CLIENTE</th>
                    <th style="width:28%">ESTABELECIMENTO</th>
                    <th style="width:14%">VALOR</th>
                    <th style="width:19%">RISCO / DECISÃO</th>
                </tr></thead>
                <tbody>{''.join(rows)}</tbody>
            </table>
        </div>
    </div>
    """


def quality_card(fraudes: dict, resumo: dict, valores: dict) -> str:
    return f"""
    <div class="insight-card quality-card">
        <div class="insight-card-title">Qualidade da triagem</div>
        <div class="insight-card-subtitle">Indicadores observados após conciliação histórica</div>
        <div class="quality-grid">
            <div class="quality-item"><div class="quality-value">{html.escape(formatar_percentual(fraudes.get('recall_politica'), 1))}</div><div class="quality-label">Cobertura observada</div></div>
            <div class="quality-item"><div class="quality-value">{html.escape(formatar_percentual(fraudes.get('precision_encaminhamento'), 1))}</div><div class="quality-label">Precisão observada</div></div>
            <div class="quality-item"><div class="quality-value">{html.escape(formatar_percentual(resumo.get('percentual_encaminhado'), 2))}</div><div class="quality-label">Taxa sinalizada</div></div>
            <div class="quality-item"><div class="quality-value">{html.escape(formatar_moeda(valores.get('ticket_medio')))}</div><div class="quality-label">Ticket médio</div></div>
        </div>
        <div class="quality-note">Esses indicadores avaliam a política em retrospecto e não revelam o rótulo histórico no fluxo operacional.</div>
    </div>
    """


def categories_card(dataframe: pd.DataFrame) -> str:
    if dataframe.empty:
        content = '<div class="empty-state" style="margin-top:.9rem;padding:2rem">Sem sinalizações suficientes para formar um ranking.</div>'
    else:
        max_total = max(float(dataframe["total_encaminhadas"].max()), 1)
        rows = []
        for _, row in dataframe.head(5).iterrows():
            total = int(row.get("total_encaminhadas") or 0)
            review = int(row.get("revisar") or 0)
            critical = int(row.get("criticas") or 0)
            width = total / max_total * 100
            rows.append(f"""
            <div class="category-row">
                <div class="category-top">
                    <div><div class="category-name">{html.escape(formatar_categoria(row.get('category')))}</div><div class="category-meta">{review} em revisão · {critical} críticas</div></div>
                    <div class="category-count">{total}</div>
                </div>
                <div class="category-track"><div class="category-fill" style="width:{width:.2f}%"></div></div>
            </div>
            """)
        content = f'<div class="category-list">{"".join(rows)}</div>'
    return f"""
    <div class="insight-card category-card">
        <div class="insight-card-title">Concentração das sinalizações</div>
        <div class="insight-card-subtitle">Categorias que mais exigiram atenção operacional</div>
        {content}
    </div>
    """


def commercial_flow_card(metricas: dict) -> str:
    volume = float(metricas.get("volume_processado") or 0)
    liberado = float(metricas.get("volume_liberado") or 0)
    revisao = float(metricas.get("valor_revisao") or 0)
    critico = float(metricas.get("valor_critico") or 0)

    def participacao(valor: float) -> float:
        return valor / volume if volume > 0 else 0.0

    liberado_pct = participacao(liberado)
    revisao_pct = participacao(revisao)
    critico_pct = participacao(critico)

    return f"""
    <div class="commercial-card commercial-flow-card">
        <div class="commercial-card-head">
            <div>
                <div class="insight-card-title">Fluxo financeiro</div>
                <div class="insight-card-subtitle">Destino do volume analisado pela política</div>
            </div>
            <div class="commercial-total">
                <strong>{html.escape(formatar_moeda_compacta(volume))}</strong>
                <span>processados</span>
            </div>
        </div>
        <div class="money-segment" aria-label="Composição do volume processado">
            <span class="money-segment-approved" style="width:{liberado_pct * 100:.4f}%"></span>
            <span class="money-segment-review" style="width:{revisao_pct * 100:.4f}%"></span>
            <span class="money-segment-critical" style="width:{critico_pct * 100:.4f}%"></span>
        </div>
        <div class="money-ledger">
            <div class="money-row approved-row">
                <span class="money-dot"></span><span class="money-label">Volume liberado</span>
                <strong>{html.escape(formatar_moeda(liberado))}</strong>
                <span class="money-share">{html.escape(formatar_percentual(liberado_pct, 1))}</span>
            </div>
            <div class="money-row review-row">
                <span class="money-dot"></span><span class="money-label">Valor sob revisão</span>
                <strong>{html.escape(formatar_moeda(revisao))}</strong>
                <span class="money-share">{html.escape(formatar_percentual(revisao_pct, 2))}</span>
            </div>
            <div class="money-row critical-row">
                <span class="money-dot"></span><span class="money-label">Exposição crítica</span>
                <strong>{html.escape(formatar_moeda(critico))}</strong>
                <span class="money-share">{html.escape(formatar_percentual(critico_pct, 2))}</span>
            </div>
        </div>
    </div>
    """


def financial_efficiency_card(metricas: dict) -> str:
    return f"""
    <div class="commercial-card efficiency-card">
        <div class="efficiency-kicker">Valor identificado</div>
        <div class="efficiency-value">
            {html.escape(formatar_moeda(metricas.get('valor_fraudulento_identificado')))}
        </div>
        <div class="efficiency-caption">exposição fraudulenta identificada pela política</div>
        <div class="tradeoff-grid">
            <div class="tradeoff-item coverage">
                <strong>{html.escape(formatar_percentual(metricas.get('cobertura_financeira'), 1))}</strong>
                <span>Cobertura financeira</span>
            </div>
            <div class="tradeoff-item friction">
                <strong>{html.escape(formatar_percentual(metricas.get('friccao_financeira'), 2))}</strong>
                <span>Fricção financeira</span>
            </div>
        </div>
        <div class="efficiency-foot">
            <span>Não interceptada <strong>{html.escape(formatar_moeda_compacta(metricas.get('valor_fraudulento_nao_interceptado')))}</strong></span>
            <span>Retenção financeira <strong>{html.escape(formatar_percentual(metricas.get('taxa_retencao_financeira'), 2))}</strong></span>
        </div>
    </div>
    """


def financial_categories_card(dataframe: pd.DataFrame) -> str:
    if dataframe.empty:
        content = (
            '<div class="empty-state" style="margin-top:.9rem;padding:2rem">'
            "Sem exposição sinalizada suficiente para formar o ranking."
            "</div>"
        )
    else:
        max_value = max(float(dataframe["exposicao_sinalizada"].max()), 1)
        rows = []
        for _, row in dataframe.head(5).iterrows():
            exposicao = float(row.get("exposicao_sinalizada") or 0)
            revisao = float(row.get("valor_revisao") or 0)
            critico = float(row.get("valor_critico") or 0)
            width = exposicao / max_value * 100
            rows.append(f"""
            <div class="financial-category-row">
                <div class="category-top">
                    <div>
                        <div class="category-name">{html.escape(formatar_categoria(row.get('category')))}</div>
                        <div class="category-meta">Revisão {html.escape(formatar_moeda_compacta(revisao))} · Crítico {html.escape(formatar_moeda_compacta(critico))}</div>
                    </div>
                    <div class="financial-category-value">{html.escape(formatar_moeda_compacta(exposicao))}</div>
                </div>
                <div class="category-track"><div class="financial-category-fill" style="width:{width:.2f}%"></div></div>
            </div>
            """)
        content = f'<div class="financial-category-list">{"".join(rows)}</div>'

    return f"""
    <div class="commercial-card financial-category-card">
        <div class="insight-card-title">Exposição por categoria</div>
        <div class="insight-card-subtitle">Concentração financeira das operações sinalizadas</div>
        {content}
    </div>
    """
