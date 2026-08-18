from pathlib import Path
import sys
import html
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ==========================================================
# PROJETO
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dashboard_queries import (
    listar_runs,
    carregar_snapshot_dashboard,
)


# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Sentinela de Fraudes",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# ESTILO
# ==========================================================

st.html(
    """
    <style>
    :root {
        --bg: #080A0F;
        --surface: #11151D;
        --surface-2: #151A24;
        --surface-3: #181E2A;
        --border: rgba(255,255,255,.065);

        --text: #F5F7FB;
        --text-2: #9AA2B4;
        --text-3: #626B7E;

        --blue: #6882FF;
        --blue-2: #8EA3FF;
        --purple: #8B5CF6;

        --green: #4ADE80;
        --amber: #FBBF24;
        --red: #FB7185;
    }

    html, body, [class*="css"] {
        font-family:
            -apple-system,
            BlinkMacSystemFont,
            "SF Pro Display",
            "SF Pro Text",
            Inter,
            "Segoe UI",
            sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 72% -18%,
                rgba(104,130,255,.10),
                transparent 29%
            ),
            radial-gradient(
                circle at 18% -8%,
                rgba(139,92,246,.045),
                transparent 24%
            ),
            var(--bg);
        color: var(--text);
    }

    .block-container {
        max-width: 1540px;
        padding-top: 1.7rem;
        padding-bottom: 4rem;
        padding-left: 2.2rem;
        padding-right: 2.2rem;
    }

    #MainMenu,
    footer,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        visibility: hidden !important;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    section[data-testid="stSidebar"] {
        background: #0C0F15;
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.55rem;
    }

    section[data-testid="stSidebar"] hr {
        border-color: var(--border);
    }

    div[data-baseweb="select"] > div {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 11px !important;
    }

    /* =====================================================
       CABEÇALHO
       ===================================================== */

    .dashboard-eyebrow {
        color: var(--blue-2);
        text-transform: uppercase;
        letter-spacing: .13em;
        font-size: .68rem;
        font-weight: 750;
        margin-bottom: .45rem;
    }

    .dashboard-title {
        font-size: 2.05rem;
        line-height: 1.05;
        font-weight: 720;
        letter-spacing: -.045em;
        margin: 0;
        color: var(--text);
    }

    .dashboard-subtitle {
        margin-top: .62rem;
        color: var(--text-2);
        font-size: .91rem;
    }

    .header-meta {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 6px;
        padding-top: 9px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: .48rem;
        padding: .46rem .78rem;
        border-radius: 999px;
        font-size: .69rem;
        font-weight: 720;
        letter-spacing: .025em;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 999px;
    }

    .header-version,
    .last-update {
        color: var(--text-3);
        font-size: .58rem;
    }

    /* =====================================================
       KPIs
       ===================================================== */

    .kpi-card {
        min-height: 135px;
        padding: 1.22rem 1.28rem;
        border-radius: 18px;
        border: 1px solid var(--border);
        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,.026),
                rgba(255,255,255,.006)
            ),
            var(--surface);
        box-shadow: 0 16px 40px rgba(0,0,0,.12);
        transition: transform .18s ease, border-color .18s ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(104,130,255,.20);
    }

    .kpi-card-critical {
        border-color: rgba(251,113,133,.12);
    }

    .kpi-card-critical:hover {
        border-color: rgba(251,113,133,.28);
        box-shadow: 0 16px 42px rgba(251,113,133,.04);
    }

    .kpi-icon {
        width: 31px;
        height: 31px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 9px;
        background: rgba(104,130,255,.10);
        color: var(--blue-2);
        font-size: .89rem;
        margin-bottom: 1rem;
    }

    .kpi-icon-critical {
        background: rgba(251,113,133,.10);
        color: var(--red);
    }

    .kpi-label {
        color: var(--text-2);
        font-size: .70rem;
        font-weight: 650;
        letter-spacing: .02em;
        margin-bottom: .32rem;
    }

    .kpi-value {
        color: var(--text);
        font-size: 1.62rem;
        line-height: 1;
        font-weight: 720;
        letter-spacing: -.045em;
    }

    .kpi-value-critical {
        color: #FF8796;
    }

    .kpi-detail {
        color: var(--text-3);
        font-size: .66rem;
        margin-top: .55rem;
    }

    /* =====================================================
       SEÇÕES
       ===================================================== */

    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 13px;
    }

    .section-title {
        color: var(--text);
        font-size: .92rem;
        font-weight: 680;
        letter-spacing: -.018em;
    }

    .section-description {
        color: var(--text-3);
        font-size: .65rem;
        margin-top: 4px;
    }

    .section-link {
        color: var(--blue-2);
        font-size: .63rem;
        font-weight: 650;
    }

    /* =====================================================
       ÚLTIMA DETECÇÃO
       ===================================================== */

    .detection-shell {
        border-radius: 20px;
        padding: 16px;
        background:
            linear-gradient(
                135deg,
                rgba(251,113,133,.035),
                rgba(139,92,246,.017) 52%,
                rgba(104,130,255,.015)
            ),
            #0F131B;
        border: 1px solid rgba(251,113,133,.11);
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.025),
            0 18px 55px rgba(0,0,0,.14);
    }

    .detection-grid {
        display: grid;
        grid-template-columns: 1.85fr 1fr;
        gap: 12px;
    }

    .latest-detection {
        min-height: 205px;
        border-radius: 16px;
        padding: 17px 18px;
        border: 1px solid rgba(251,113,133,.16);
        background:
            radial-gradient(
                circle at 88% 10%,
                rgba(251,113,133,.085),
                transparent 28%
            ),
            #131821;
    }

    .latest-review {
        border-color: rgba(251,191,36,.18);
        background:
            radial-gradient(
                circle at 88% 10%,
                rgba(251,191,36,.075),
                transparent 28%
            ),
            #131821;
    }

    .latest-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
    }

    .latest-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 8px;
        border-radius: 999px;
        font-size: .48rem;
        font-weight: 820;
        letter-spacing: .055em;
    }

    .latest-tag-critical {
        background: rgba(251,113,133,.11);
        border: 1px solid rgba(251,113,133,.21);
        color: #FB7185;
    }

    .latest-tag-review {
        background: rgba(251,191,36,.10);
        border: 1px solid rgba(251,191,36,.20);
        color: #FBBF24;
    }

    .latest-score {
        font-size: 2.25rem;
        font-weight: 780;
        line-height: .95;
        letter-spacing: -.055em;
    }

    .latest-score-caption {
        margin-top: 5px;
        text-align: right;
        color: var(--text-3);
        font-size: .52rem;
    }

    .latest-name {
        color: var(--text);
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: -.025em;
        margin-top: 24px;
    }

    .latest-merchant {
        color: #C8CEDA;
        font-size: .66rem;
        margin-top: 5px;
    }

    .latest-details {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 18px;
    }

    .latest-detail-chip {
        display: inline-flex;
        padding: 6px 8px;
        border-radius: 9px;
        background: rgba(255,255,255,.028);
        border: 1px solid rgba(255,255,255,.045);
        color: #8E97AA;
        font-size: .55rem;
    }

    .latest-value {
        color: var(--text);
        font-weight: 690;
    }

    .recent-detections {
        display: flex;
        flex-direction: column;
        gap: 9px;
    }

    .recent-detection-card {
        flex: 1;
        min-height: 93px;
        border-radius: 14px;
        padding: 12px 13px;
        background: #131821;
        border: 1px solid rgba(255,255,255,.055);
    }

    .recent-detection-card-critical {
        border-color: rgba(251,113,133,.13);
    }

    .recent-detection-card-review {
        border-color: rgba(251,191,36,.13);
    }

    .recent-row {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        align-items: flex-start;
    }

    .recent-tag {
        font-size: .46rem;
        font-weight: 780;
        letter-spacing: .045em;
    }

    .recent-score {
        font-size: .93rem;
        font-weight: 760;
        letter-spacing: -.035em;
    }

    .recent-name {
        color: var(--text);
        font-size: .62rem;
        font-weight: 650;
        margin-top: 10px;
    }

    .recent-meta {
        color: var(--text-3);
        font-size: .51rem;
        margin-top: 3px;
    }

    .detections-empty {
        min-height: 200px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-radius: 16px;
        border: 1px dashed rgba(104,130,255,.15);
        color: var(--text-3);
        background: rgba(104,130,255,.015);
    }

    /* =====================================================
       FILTRO DO FEED
       ===================================================== */

    div[data-testid="stRadio"] > label {
        display: none !important;
    }

    div[data-testid="stRadio"] [role="radiogroup"] {
        display: inline-flex;
        gap: 4px;
        padding: 4px;
        border-radius: 11px;
        background: #11151D;
        border: 1px solid rgba(255,255,255,.06);
    }

    div[data-testid="stRadio"] [role="radio"] {
        background: transparent;
        border-radius: 8px;
        padding: 5px 9px;
    }

    div[data-testid="stRadio"] [role="radio"]:has(input:checked) {
        background: rgba(104,130,255,.12);
        box-shadow: inset 0 0 0 1px rgba(104,130,255,.15);
    }

    div[data-testid="stRadio"] [role="radio"] p {
        font-size: .60rem !important;
        font-weight: 650 !important;
        color: #8E96A8 !important;
    }

    div[data-testid="stRadio"] [role="radio"]:has(input:checked) p {
        color: #A7B5FF !important;
    }

    /* =====================================================
       TABELA
       ===================================================== */

    .transaction-table-wrapper {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        overflow: hidden;
    }

    .transaction-table-scroll {
        max-height: 445px;
        overflow-y: auto;
    }

    .transaction-table {
        width: 100%;
        border-collapse: collapse;
    }

    .transaction-table thead {
        position: sticky;
        top: 0;
        z-index: 3;
        background: #141923;
    }

    .transaction-table th {
        padding: 12px 13px;
        text-align: left;
        color: var(--text-3);
        font-size: .52rem;
        font-weight: 760;
        letter-spacing: .09em;
        border-bottom: 1px solid rgba(255,255,255,.055);
    }

    .transaction-table td {
        padding: 12px 13px;
        vertical-align: middle;
        color: #DDE2EC;
        font-size: .64rem;
        border-bottom: 1px solid rgba(255,255,255,.042);
    }

    .transaction-table tbody tr:last-child td {
        border-bottom: none;
    }

    .transaction-table tbody tr {
        transition: background .14s ease;
    }

    .transaction-table tbody tr:hover {
        background: rgba(104,130,255,.035);
    }

    .transaction-table-scroll::-webkit-scrollbar {
        width: 5px;
    }

    .transaction-table-scroll::-webkit-scrollbar-track {
        background: transparent;
    }

    .transaction-table-scroll::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,.10);
        border-radius: 999px;
    }

    .customer-cell {
        display: flex;
        align-items: center;
        gap: 9px;
    }

    .avatar {
        width: 31px;
        height: 31px;
        min-width: 31px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        background:
            linear-gradient(
                145deg,
                rgba(104,130,255,.20),
                rgba(139,92,246,.15)
            );
        color: #AFBCFF;
        font-size: .56rem;
        font-weight: 760;
    }

    .customer-name {
        color: var(--text);
        font-size: .64rem;
        font-weight: 630;
    }

    .customer-card {
        color: var(--text-3);
        font-size: .52rem;
        margin-top: 2px;
    }

    .merchant-name {
        color: #DDE2EC;
        font-size: .63rem;
        font-weight: 570;
    }

    .merchant-category {
        color: var(--text-3);
        font-size: .52rem;
        margin-top: 2px;
    }

    .location-text {
        color: var(--text-2);
        font-size: .58rem;
    }

    .amount-text {
        color: var(--text);
        font-size: .64rem;
        font-weight: 660;
    }

    .risk-wrapper {
        min-width: 88px;
    }

    .risk-value {
        font-size: .59rem;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .risk-track {
        width: 72px;
        height: 4px;
        border-radius: 999px;
        background: rgba(255,255,255,.065);
        overflow: hidden;
    }

    .risk-fill {
        height: 100%;
        border-radius: 999px;
    }

    .decision-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 5px 9px;
        border-radius: 999px;
        font-size: .49rem;
        font-weight: 780;
        letter-spacing: .045em;
        white-space: nowrap;
    }

    .decision-approved {
        background: rgba(34,197,94,.15);
        color: #4ADE80;
        border: 1px solid rgba(74,222,128,.31);
        box-shadow: 0 0 15px rgba(74,222,128,.07);
    }

    .decision-review {
        background: rgba(245,158,11,.15);
        color: #FBBF24;
        border: 1px solid rgba(251,191,36,.33);
        box-shadow: 0 0 15px rgba(251,191,36,.07);
    }

    .decision-critical {
        background: rgba(244,63,94,.16);
        color: #FB7185;
        border: 1px solid rgba(251,113,133,.35);
        box-shadow: 0 0 17px rgba(244,63,94,.10);
    }

    /* =====================================================
       VISÃO DE RISCO
       ===================================================== */

    .risk-metrics-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 2px;
    }

    .risk-mini-card {
        background: rgba(255,255,255,.018);
        border: 1px solid rgba(255,255,255,.050);
        border-radius: 12px;
        padding: 11px 12px;
    }

    .risk-mini-label {
        color: var(--text-3);
        font-size: .47rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .075em;
    }

    .risk-mini-value {
        color: var(--text);
        font-size: .91rem;
        font-weight: 720;
        letter-spacing: -.03em;
        margin-top: 4px;
    }

    /* =====================================================
       AVALIAÇÃO DA SIMULAÇÃO
       ===================================================== */

    .evaluation-shell {
        background:
            linear-gradient(
                145deg,
                rgba(104,130,255,.026),
                rgba(139,92,246,.012)
            ),
            var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 18px;
        min-height: 245px;
    }

    .evaluation-kicker {
        color: var(--blue-2);
        font-size: .49rem;
        font-weight: 760;
        letter-spacing: .09em;
        text-transform: uppercase;
    }

    .evaluation-note {
        color: var(--text-3);
        font-size: .53rem;
        margin-top: 4px;
        line-height: 1.4;
    }

    .evaluation-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 9px;
        margin-top: 16px;
    }

    .evaluation-card {
        border-radius: 13px;
        padding: 12px;
        background: rgba(255,255,255,.018);
        border: 1px solid rgba(255,255,255,.045);
    }

    .evaluation-card-detected {
        border-color: rgba(74,222,128,.12);
    }

    .evaluation-card-missed {
        border-color: rgba(251,113,133,.10);
    }

    .evaluation-value {
        font-size: 1.28rem;
        font-weight: 760;
        letter-spacing: -.04em;
        color: var(--text);
    }

    .evaluation-label {
        color: var(--text-3);
        font-size: .51rem;
        font-weight: 650;
        margin-top: 3px;
    }

    .evaluation-bar {
        margin-top: 15px;
        height: 8px;
        border-radius: 999px;
        overflow: hidden;
        background: rgba(255,255,255,.05);
        display: flex;
    }

    .evaluation-bar-detected {
        background: linear-gradient(
            90deg,
            #6882FF,
            #8B5CF6
        );
        height: 100%;
    }

    .evaluation-bar-missed {
        background: rgba(251,113,133,.65);
        height: 100%;
    }

    /* =====================================================
       COMPOSIÇÃO DAS SINALIZADAS
       ===================================================== */

    .flagged-shell {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 18px;
        min-height: 245px;
    }

    .flagged-summary {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 9px;
        margin-top: 10px;
    }

    .flagged-card {
        border-radius: 13px;
        padding: 13px;
        background: rgba(255,255,255,.018);
        border: 1px solid rgba(255,255,255,.045);
    }

    .flagged-card-review {
        border-color: rgba(251,191,36,.12);
    }

    .flagged-card-critical {
        border-color: rgba(251,113,133,.13);
    }

    .flagged-value {
        font-size: 1.35rem;
        font-weight: 760;
        letter-spacing: -.045em;
    }

    .flagged-label {
        color: var(--text-3);
        font-size: .51rem;
        margin-top: 3px;
    }

    .flagged-track {
        margin-top: 16px;
        height: 8px;
        border-radius: 999px;
        background: rgba(255,255,255,.05);
        overflow: hidden;
        display: flex;
    }

    .flagged-review-bar {
        background: #FBBF24;
        height: 100%;
    }

    .flagged-critical-bar {
        background: #FB7185;
        height: 100%;
    }

    .flagged-total {
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
        color: var(--text-3);
        font-size: .52rem;
    }

    /* =====================================================
       RANKING DE CATEGORIAS
       ===================================================== */

    .category-ranking {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .category-row {
        border-radius: 13px;
        padding: 11px 12px;
        background: var(--surface);
        border: 1px solid rgba(255,255,255,.05);
    }

    .category-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
    }

    .category-rank {
        width: 24px;
        height: 24px;
        min-width: 24px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #AAB7FF;
        background: rgba(104,130,255,.09);
        border: 1px solid rgba(104,130,255,.12);
        font-size: .52rem;
        font-weight: 750;
    }

    .category-name-wrap {
        flex: 1;
    }

    .category-name {
        color: var(--text);
        font-size: .62rem;
        font-weight: 650;
    }

    .category-meta {
        color: var(--text-3);
        font-size: .50rem;
        margin-top: 2px;
    }

    .category-count {
        color: var(--text);
        font-size: .72rem;
        font-weight: 730;
        text-align: right;
    }

    .category-count-label {
        color: var(--text-3);
        font-size: .45rem;
        margin-top: 1px;
    }

    .category-track {
        height: 5px;
        margin-top: 9px;
        background: rgba(255,255,255,.05);
        border-radius: 999px;
        overflow: hidden;
    }

    .category-fill {
        height: 100%;
        border-radius: 999px;
        background:
            linear-gradient(
                90deg,
                #6882FF,
                #8B5CF6
            );
    }
    </style>
    """
)


# ==========================================================
# HELPERS
# ==========================================================

def valor_ausente(valor):
    try:
        return pd.isna(valor)
    except Exception:
        return valor is None


def texto_seguro(valor, padrao="—"):
    if valor is None or valor_ausente(valor):
        return padrao
    return str(valor)


def formatar_numero(valor):
    if valor is None:
        return "—"
    return f"{int(valor):,}".replace(",", ".")


def formatar_percentual(valor, casas=2):
    if valor is None:
        return "—"
    return f"{float(valor) * 100:.{casas}f}%".replace(".", ",")


def formatar_moeda(valor):
    if valor is None or valor_ausente(valor):
        return "—"

    return (
        "US$ "
        + f"{float(valor):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


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


def formatar_categoria(valor):
    texto = texto_seguro(valor)

    if texto == "—":
        return texto

    return CATEGORIAS_PT.get(
        texto,
        texto.replace("_", " ").title(),
    )


def limpar_merchant(valor):
    texto = texto_seguro(valor)

    if texto == "—":
        return texto

    if texto.startswith("fraud_"):
        texto = texto[6:]

    return texto


def formatar_horario(valor):
    if valor is None or valor_ausente(valor):
        return "—"

    try:
        return pd.to_datetime(valor).strftime("%H:%M:%S")
    except Exception:
        return str(valor)


def iniciais(first, last):
    f = texto_seguro(first, "")
    l = texto_seguro(last, "")

    resultado = (
        (f[0] if f else "")
        + (l[0] if l else "")
    ).upper()

    return resultado or "?"


def traduzir_status(status):
    mapa = {
        "RUNNING": "AO VIVO",
        "COMPLETED": "CONCLUÍDO",
        "FAILED": "FALHOU",
    }
    return mapa.get(status, status)


def classe_decisao(decisao):
    mapa = {
        "APROVAR": (
            "decision-approved",
            "APROVADA",
            "#4ADE80",
        ),
        "REVISAR": (
            "decision-review",
            "REVISAR",
            "#FBBF24",
        ),
        "ALERTA_CRITICO": (
            "decision-critical",
            "ALERTA CRÍTICO",
            "#FB7185",
        ),
    }

    return mapa.get(
        decisao,
        (
            "decision-approved",
            texto_seguro(decisao, "—"),
            "#8EA3FF",
        ),
    )


def card_kpi(
    label,
    valor,
    detalhe,
    icone,
    critico=False,
):
    extra_card = (
        "kpi-card-critical"
        if critico
        else ""
    )

    extra_icon = (
        "kpi-icon-critical"
        if critico
        else ""
    )

    extra_value = (
        "kpi-value-critical"
        if critico
        else ""
    )

    return f"""
    <div class="kpi-card {extra_card}">
        <div class="kpi-icon {extra_icon}">
            {icone}
        </div>

        <div class="kpi-label">
            {html.escape(str(label))}
        </div>

        <div class="kpi-value {extra_value}">
            {html.escape(str(valor))}
        </div>

        <div class="kpi-detail">
            {html.escape(str(detalhe))}
        </div>
    </div>
    """


# ==========================================================
# TABELA
# ==========================================================

def render_tabela_transacoes(
    dataframe: pd.DataFrame
):
    if dataframe.empty:
        return """
        <div class="transaction-table-wrapper">
            <div style="
                padding:34px;
                text-align:center;
                color:#626B7E;
                font-size:11px;
            ">
                Nenhuma transação disponível.
            </div>
        </div>
        """

    linhas = []

    for _, row in dataframe.iterrows():
        first = texto_seguro(
            row.get("first"),
            ""
        )

        last = texto_seguro(
            row.get("last"),
            ""
        )

        nome = (
            f"{first} {last}".strip()
            or "Cliente não identificado"
        )

        merchant = limpar_merchant(
            row.get("merchant")
        )

        category = formatar_categoria(
            row.get("category")
        )

        city = texto_seguro(
            row.get("city"),
            ""
        )

        state = texto_seguro(
            row.get("state"),
            ""
        )

        location = (
            f"{city} · {state}"
            if city and state
            else city or state or "—"
        )

        cc = texto_seguro(
            row.get("cc_last4"),
            "----"
        )

        score = float(
            row.get("score_fraude")
            or 0
        )

        score_pct = (
            score * 100
        )

        (
            classe,
            label,
            cor,
        ) = classe_decisao(
            row.get("decisao")
        )

        largura_barra = max(
            min(score_pct, 100),
            2.0
        )

        horario = formatar_horario(
            row.get(
                "trans_date_trans_time"
            )
        )

        valor = formatar_moeda(
            row.get("amt")
        )

        linhas.append(
            f"""
            <tr>
                <td>
                    <span style="
                        color:#626B7E;
                        font-size:10px;
                    ">
                        {html.escape(horario)}
                    </span>
                </td>

                <td>
                    <div class="customer-cell">
                        <div class="avatar">
                            {html.escape(
                                iniciais(
                                    first,
                                    last
                                )
                            )}
                        </div>

                        <div>
                            <div class="customer-name">
                                {html.escape(nome)}
                            </div>

                            <div class="customer-card">
                                •••• {html.escape(cc)}
                            </div>
                        </div>
                    </div>
                </td>

                <td>
                    <div class="merchant-name">
                        {html.escape(merchant)}
                    </div>

                    <div class="merchant-category">
                        {html.escape(category)}
                    </div>
                </td>

                <td>
                    <span class="location-text">
                        {html.escape(location)}
                    </span>
                </td>

                <td>
                    <span class="amount-text">
                        {html.escape(valor)}
                    </span>
                </td>

                <td>
                    <div class="risk-wrapper">
                        <div
                            class="risk-value"
                            style="color:{cor};"
                        >
                            {score_pct:.2f}%
                        </div>

                        <div class="risk-track">
                            <div
                                class="risk-fill"
                                style="
                                    width:{largura_barra:.2f}%;
                                    background:{cor};
                                "
                            ></div>
                        </div>
                    </div>
                </td>

                <td>
                    <span class="
                        decision-badge
                        {classe}
                    ">
                        {html.escape(label)}
                    </span>
                </td>
            </tr>
            """
        )

    return f"""
    <div class="transaction-table-wrapper">
        <div class="transaction-table-scroll">
            <table class="transaction-table">
                <thead>
                    <tr>
                        <th>HORÁRIO</th>
                        <th>CLIENTE</th>
                        <th>ESTABELECIMENTO</th>
                        <th>LOCAL</th>
                        <th>VALOR</th>
                        <th>RISCO</th>
                        <th>DECISÃO</th>
                    </tr>
                </thead>

                <tbody>
                    {''.join(linhas)}
                </tbody>
            </table>
        </div>
    </div>
    """


# ==========================================================
# ÚLTIMA DETECÇÃO + ALERTAS RECENTES
# ==========================================================

def render_detection_area(
    dataframe: pd.DataFrame
):
    if dataframe.empty:
        return """
        <div class="detection-shell">
            <div class="detections-empty">
                <div style="
                    color:#8EA3FF;
                    font-size:22px;
                    margin-bottom:9px;
                ">
                    ◇
                </div>

                <div style="
                    color:#D6DBE5;
                    font-size:12px;
                    font-weight:650;
                ">
                    Nenhuma transação sinalizada até o momento
                </div>

                <div style="
                    margin-top:5px;
                    font-size:10px;
                ">
                    A próxima operação em revisão ou alerta crítico
                    aparecerá aqui automaticamente.
                </div>
            </div>
        </div>
        """

    principal = dataframe.iloc[0]

    decisao = principal.get(
        "decisao"
    )

    is_critical = (
        decisao == "ALERTA_CRITICO"
    )

    latest_class = (
        ""
        if is_critical
        else "latest-review"
    )

    tag_class = (
        "latest-tag-critical"
        if is_critical
        else "latest-tag-review"
    )

    tag_label = (
        "ALERTA CRÍTICO"
        if is_critical
        else "REVISAR"
    )

    cor = (
        "#FB7185"
        if is_critical
        else "#FBBF24"
    )

    first = texto_seguro(
        principal.get("first"),
        ""
    )

    last = texto_seguro(
        principal.get("last"),
        ""
    )

    nome = (
        f"{first} {last}".strip()
        or "Cliente não identificado"
    )

    merchant = limpar_merchant(
        principal.get("merchant")
    )

    category = formatar_categoria(
        principal.get("category")
    )

    city = texto_seguro(
        principal.get("city"),
        ""
    )

    state = texto_seguro(
        principal.get("state"),
        ""
    )

    location = (
        f"{city} · {state}"
        if city and state
        else city or state or "—"
    )

    score_pct = (
        float(
            principal.get(
                "score_fraude"
            )
            or 0
        )
        * 100
    )

    valor = formatar_moeda(
        principal.get("amt")
    )

    horario = formatar_horario(
        principal.get(
            "trans_date_trans_time"
        )
    )

    principal_html = f"""
    <div class="
        latest-detection
        {latest_class}
    ">
        <div class="latest-top">
            <span class="
                latest-tag
                {tag_class}
            ">
                ● {tag_label}
            </span>

            <div>
                <div
                    class="latest-score"
                    style="color:{cor};"
                >
                    {score_pct:.2f}%
                </div>

                <div class="latest-score-caption">
                    score de risco
                </div>
            </div>
        </div>

        <div class="latest-name">
            {html.escape(nome)}
        </div>

        <div class="latest-merchant">
            {html.escape(merchant)}
            ·
            {html.escape(category)}
        </div>

        <div class="latest-details">
            <span class="latest-detail-chip">
                <span class="latest-value">
                    {html.escape(valor)}
                </span>
            </span>

            <span class="latest-detail-chip">
                {html.escape(location)}
            </span>

            <span class="latest-detail-chip">
                {html.escape(horario)}
            </span>
        </div>
    </div>
    """

    recentes = []

    for _, row in dataframe.iloc[
        1:3
    ].iterrows():

        decisao_item = row.get(
            "decisao"
        )

        critico = (
            decisao_item
            == "ALERTA_CRITICO"
        )

        card_class = (
            "recent-detection-card-critical"
            if critico
            else "recent-detection-card-review"
        )

        item_cor = (
            "#FB7185"
            if critico
            else "#FBBF24"
        )

        item_label = (
            "CRÍTICO"
            if critico
            else "REVISAR"
        )

        f = texto_seguro(
            row.get("first"),
            ""
        )

        l = texto_seguro(
            row.get("last"),
            ""
        )

        nome_item = (
            f"{f} {l}".strip()
            or "Cliente não identificado"
        )

        score_item = (
            float(
                row.get(
                    "score_fraude"
                )
                or 0
            )
            * 100
        )

        categoria_item = (
            formatar_categoria(
                row.get("category")
            )
        )

        valor_item = (
            formatar_moeda(
                row.get("amt")
            )
        )

        recentes.append(
            f"""
            <div class="
                recent-detection-card
                {card_class}
            ">
                <div class="recent-row">
                    <span
                        class="recent-tag"
                        style="color:{item_cor};"
                    >
                        ● {item_label}
                    </span>

                    <span
                        class="recent-score"
                        style="color:{item_cor};"
                    >
                        {score_item:.2f}%
                    </span>
                </div>

                <div class="recent-name">
                    {html.escape(nome_item)}
                </div>

                <div class="recent-meta">
                    {html.escape(
                        categoria_item
                    )}
                    ·
                    {html.escape(
                        valor_item
                    )}
                </div>
            </div>
            """
        )

    while len(recentes) < 2:
        recentes.append(
            """
            <div class="recent-detection-card">
                <div style="
                    color:#626B7E;
                    font-size:9px;
                    padding:26px 4px;
                    text-align:center;
                ">
                    Aguardando nova sinalização
                </div>
            </div>
            """
        )

    return f"""
    <div class="detection-shell">
        <div class="section-header">
            <div>
                <div class="section-title">
                    Última Detecção
                </div>

                <div class="section-description">
                    Operação sinalizada mais recente pelo sistema
                </div>
            </div>

            <div class="section-link">
                Atualização automática · 1 s
            </div>
        </div>

        <div class="detection-grid">
            {principal_html}

            <div class="recent-detections">
                {''.join(recentes)}
            </div>
        </div>
    </div>
    """


# ==========================================================
# AVALIAÇÃO DA SIMULAÇÃO
# ==========================================================

def render_evaluation(
    fraudes: dict
):
    detectadas = (
        fraudes.get(
            "fraudes_detectadas",
            0
        )
        or 0
    )

    perdidas = (
        fraudes.get(
            "fraudes_perdidas",
            0
        )
        or 0
    )

    recall = (
        fraudes.get(
            "recall_politica"
        )
    )

    precision = (
        fraudes.get(
            "precision_encaminhamento"
        )
    )

    recall_pct = (
        float(recall)
        if recall is not None
        else 0
    )

    missed_pct = max(
        1 - recall_pct,
        0
    )

    return f"""
    <div class="evaluation-shell">
        <div class="evaluation-kicker">
            Avaliação da Simulação
        </div>

        <div class="evaluation-note">
            Métricas calculadas com o rótulo histórico
            após a decisão do modelo.
        </div>

        <div class="evaluation-grid">
            <div class="
                evaluation-card
                evaluation-card-detected
            ">
                <div class="evaluation-value">
                    {formatar_numero(detectadas)}
                </div>

                <div class="evaluation-label">
                    FRAUDES DETECTADAS
                </div>
            </div>

            <div class="
                evaluation-card
                evaluation-card-missed
            ">
                <div class="evaluation-value">
                    {formatar_numero(perdidas)}
                </div>

                <div class="evaluation-label">
                    FRAUDES NÃO DETECTADAS
                </div>
            </div>

            <div class="evaluation-card">
                <div class="evaluation-value">
                    {formatar_percentual(
                        recall,
                        1
                    )}
                </div>

                <div class="evaluation-label">
                    COBERTURA
                </div>
            </div>

            <div class="evaluation-card">
                <div class="evaluation-value">
                    {formatar_percentual(
                        precision,
                        1
                    )}
                </div>

                <div class="evaluation-label">
                    PRECISÃO
                </div>
            </div>
        </div>

        <div class="evaluation-bar">
            <div
                class="evaluation-bar-detected"
                style="
                    width:{recall_pct * 100:.2f}%;
                "
            ></div>

            <div
                class="evaluation-bar-missed"
                style="
                    width:{missed_pct * 100:.2f}%;
                "
            ></div>
        </div>
    </div>
    """


# ==========================================================
# COMPOSIÇÃO DAS SINALIZADAS
# ==========================================================

def render_flagged_composition(
    sinalizacoes: dict
):
    total = (
        sinalizacoes.get(
            "total_sinalizadas",
            0
        )
        or 0
    )

    revisao = (
        sinalizacoes.get(
            "total_revisao",
            0
        )
        or 0
    )

    criticas = (
        sinalizacoes.get(
            "total_criticas",
            0
        )
        or 0
    )

    if total > 0:
        pct_revisao = (
            revisao
            / total
        )

        pct_criticas = (
            criticas
            / total
        )
    else:
        pct_revisao = 0
        pct_criticas = 0

    return f"""
    <div class="flagged-shell">
        <div class="section-title">
            Composição das Sinalizadas
        </div>

        <div class="section-description">
            Distribuição entre revisão e alerta crítico
        </div>

        <div class="flagged-summary">
            <div class="
                flagged-card
                flagged-card-review
            ">
                <div
                    class="flagged-value"
                    style="color:#FBBF24;"
                >
                    {formatar_numero(revisao)}
                </div>

                <div class="flagged-label">
                    EM REVISÃO
                    ·
                    {
                        f"{pct_revisao * 100:.1f}%"
                        .replace(".", ",")
                    }
                </div>
            </div>

            <div class="
                flagged-card
                flagged-card-critical
            ">
                <div
                    class="flagged-value"
                    style="color:#FB7185;"
                >
                    {formatar_numero(criticas)}
                </div>

                <div class="flagged-label">
                    ALERTAS CRÍTICOS
                    ·
                    {
                        f"{pct_criticas * 100:.1f}%"
                        .replace(".", ",")
                    }
                </div>
            </div>
        </div>

        <div class="flagged-track">
            <div
                class="flagged-review-bar"
                style="
                    width:{pct_revisao * 100:.2f}%;
                "
            ></div>

            <div
                class="flagged-critical-bar"
                style="
                    width:{pct_criticas * 100:.2f}%;
                "
            ></div>
        </div>

        <div class="flagged-total">
            <span>
                Total sinalizado
            </span>

            <span style="
                color:#F5F7FB;
                font-weight:650;
            ">
                {formatar_numero(total)}
            </span>
        </div>
    </div>
    """


# ==========================================================
# RANKING DE CATEGORIAS
# ==========================================================

def render_category_ranking(
    dataframe: pd.DataFrame
):
    if dataframe.empty:
        return """
        <div style="
            color:#626B7E;
            padding:30px 0;
            font-size:11px;
        ">
            Ainda não há volume sinalizado suficiente
            para montar o ranking.
        </div>
        """

    df = (
        dataframe
        .copy()
        .sort_values(
            "total_encaminhadas",
            ascending=False,
        )
        .head(6)
    )

    max_value = max(
        int(
            df[
                "total_encaminhadas"
            ].max()
        ),
        1,
    )

    rows = []

    for index, (_, row) in enumerate(
        df.iterrows(),
        start=1,
    ):
        category = (
            formatar_categoria(
                row.get("category")
            )
        )

        total = int(
            row.get(
                "total_encaminhadas",
                0
            )
            or 0
        )

        revisao = int(
            row.get(
                "revisar",
                0
            )
            or 0
        )

        criticas = int(
            row.get(
                "criticas",
                0
            )
            or 0
        )

        score_medio = float(
            row.get(
                "score_medio",
                0
            )
            or 0
        )

        largura = (
            total
            / max_value
            * 100
        )

        rows.append(
            f"""
            <div class="category-row">
                <div class="category-top">
                    <div class="category-rank">
                        {index}
                    </div>

                    <div class="category-name-wrap">
                        <div class="category-name">
                            {html.escape(category)}
                        </div>

                        <div class="category-meta">
                            {formatar_numero(revisao)}
                            em revisão
                            ·
                            {formatar_numero(criticas)}
                            críticas
                            ·
                            score médio
                            {
                                f"{score_medio * 100:.1f}%"
                                .replace(".", ",")
                            }
                        </div>
                    </div>

                    <div>
                        <div class="category-count">
                            {formatar_numero(total)}
                        </div>

                        <div class="category-count-label">
                            sinalizadas
                        </div>
                    </div>
                </div>

                <div class="category-track">
                    <div
                        class="category-fill"
                        style="
                            width:{largura:.2f}%;
                        "
                    ></div>
                </div>
            </div>
            """
        )

    return f"""
    <div class="category-ranking">
        {''.join(rows)}
    </div>
    """


# ==========================================================
# EXECUÇÕES
# ==========================================================

runs = listar_runs()

if not runs:
    st.error(
        "Nenhuma execução de replay encontrada."
    )
    st.stop()

run_ids = [
    run["run_id"]
    for run in runs
]


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:
    st.html(
        """
        <div style="margin-bottom:30px;">
            <div style="
                color:#8EA3FF;
                font-size:20px;
                font-weight:760;
                letter-spacing:-.045em;
            ">
                ◈ Sentinela de Fraudes
            </div>

            <div style="
                color:#626B7E;
                font-size:10px;
                margin-top:5px;
            ">
                Inteligência e monitoramento transacional
            </div>
        </div>
        """
    )

    st.html(
        """
        <div style="
            color:#626B7E;
            font-size:9px;
            font-weight:720;
            letter-spacing:.12em;
            margin-bottom:8px;
        ">
            EXECUÇÃO
        </div>
        """
    )

    run_id = st.selectbox(
        "Execução",
        run_ids,
        label_visibility="collapsed",
    )

    st.divider()

    st.html(
        """
        <div style="
            color:#626B7E;
            font-size:9px;
            font-weight:720;
            letter-spacing:.12em;
            margin-bottom:14px;
        ">
            PRINCIPAL
        </div>

        <div style="
            color:#9AAEFF;
            font-size:13px;
            font-weight:620;
            margin:18px 0;
        ">
            ▣ &nbsp; Visão geral
        </div>

        <div style="
            color:#8C93A3;
            font-size:13px;
            margin:20px 0;
        ">
            ◌ &nbsp; Transações
        </div>

        <div style="
            color:#8C93A3;
            font-size:13px;
            margin:20px 0;
        ">
            ⚠ &nbsp; Alertas críticos
        </div>

        <div style="
            color:#8C93A3;
            font-size:13px;
            margin:20px 0;
        ">
            ◇ &nbsp; Fila de revisão
        </div>
        """
    )


# ==========================================================
# DASHBOARD AO VIVO
# ==========================================================

@st.fragment(run_every="1s")
def render_dashboard_live(
    run_id: str
):
    snapshot = (
        carregar_snapshot_dashboard(
            run_id
        )
    )

    replay = (
        snapshot.get("replay")
        or {}
    )

    resumo = (
        snapshot.get("resumo")
        or {}
    )

    fraudes = (
        snapshot.get("fraudes")
        or {}
    )

    valores = (
        snapshot.get("valores")
        or {}
    )

    sinalizacoes = (
        snapshot.get("sinalizacoes")
        or {}
    )

    transacoes = pd.DataFrame(
        snapshot.get(
            "transacoes_recentes",
            []
        )
    )

    transacoes_sinalizadas = pd.DataFrame(
        snapshot.get(
            "transacoes_sinalizadas",
            []
        )
    )

    alertas_criticos = pd.DataFrame(
        snapshot.get(
            "alertas_criticos",
            []
        )
    )

    categorias = pd.DataFrame(
        snapshot.get(
            "top_categorias_risco",
            []
        )
    )

    total = (
        resumo.get(
            "total_processadas",
            0
        )
        or 0
    )

    aprovadas = (
        resumo.get(
            "aprovadas",
            0
        )
        or 0
    )

    revisar = (
        resumo.get(
            "revisar",
            0
        )
        or 0
    )

    criticos = (
        resumo.get(
            "alertas_criticos",
            0
        )
        or 0
    )

    percentual_aprovadas = (
        resumo.get(
            "percentual_aprovadas",
            0
        )
        or 0
    )

    percentual_revisar = (
        resumo.get(
            "percentual_revisar",
            0
        )
        or 0
    )

    percentual_criticos = (
        resumo.get(
            "percentual_criticos",
            0
        )
        or 0
    )

    percentual_encaminhado = (
        resumo.get(
            "percentual_encaminhado",
            0
        )
        or 0
    )

    recall = (
        fraudes.get(
            "recall_politica"
        )
    )

    precision_encaminhamento = (
        fraudes.get(
            "precision_encaminhamento"
        )
    )

    taxa_fraude_critica = (
        fraudes.get(
            "taxa_fraude_critica"
        )
    )

    status_original = (
        replay.get(
            "status",
            "UNKNOWN",
        )
    )

    status_pt = traduzir_status(
        status_original
    )

    model_version = texto_seguro(
        replay.get(
            "model_version"
        )
    )

    policy_version = texto_seguro(
        replay.get(
            "policy_version"
        )
    )

    agora = (
        datetime.now()
        .strftime("%H:%M:%S")
    )

    # ------------------------------------------------------
    # CABEÇALHO
    # ------------------------------------------------------

    header_left, header_right = (
        st.columns(
            [5, 1.45]
        )
    )

    with header_left:
        st.html(
            """
            <div class="dashboard-eyebrow">
                Monitoramento de Fraudes
            </div>

            <h1 class="dashboard-title">
                Inteligência de Transações
            </h1>

            <div class="dashboard-subtitle">
                Monitoramento de risco, decisões operacionais
                e transações suspeitas.
            </div>
            """
        )

    with header_right:
        if status_original == "RUNNING":
            cor_status = "#4ADE80"
            fundo_status = "rgba(74,222,128,.09)"
            borda_status = "rgba(74,222,128,.20)"
        elif status_original == "COMPLETED":
            cor_status = "#8EA3FF"
            fundo_status = "rgba(104,130,255,.09)"
            borda_status = "rgba(104,130,255,.20)"
        else:
            cor_status = "#FB7185"
            fundo_status = "rgba(251,113,133,.09)"
            borda_status = "rgba(251,113,133,.20)"

        st.html(
            f"""
            <div class="header-meta">
                <div
                    class="status-pill"
                    style="
                        color:{cor_status};
                        background:{fundo_status};
                        border:
                            1px solid
                            {borda_status};
                    "
                >
                    <span
                        class="status-dot"
                        style="
                            background:{cor_status};
                            box-shadow:
                                0 0 12px
                                {cor_status};
                        "
                    ></span>

                    {html.escape(
                        status_pt
                    )}
                </div>

                <div class="header-version">
                    {html.escape(
                        model_version
                    )}
                    ·
                    {html.escape(
                        policy_version
                    )}
                </div>

                <div class="last-update">
                    Atualizado às {agora}
                </div>
            </div>
            """
        )

    st.html(
        "<div style='height:24px'></div>"
    )

    # ------------------------------------------------------
    # KPIs
    # ------------------------------------------------------

    k1, k2, k3, k4 = (
        st.columns(
            4,
            gap="medium",
        )
    )

    with k1:
        st.html(
            card_kpi(
                "TRANSAÇÕES PROCESSADAS",
                formatar_numero(
                    total
                ),
                "Volume total analisado",
                "◫",
            )
        )

    with k2:
        st.html(
            card_kpi(
                "APROVADAS",
                formatar_numero(
                    aprovadas
                ),
                (
                    f"{percentual_aprovadas * 100:.2f}% "
                    "do total"
                ),
                "✓",
            )
        )

    with k3:
        st.html(
            card_kpi(
                "EM REVISÃO",
                formatar_numero(
                    revisar
                ),
                (
                    f"{percentual_revisar * 100:.3f}% "
                    "das transações"
                ),
                "◇",
            )
        )

    with k4:
        st.html(
            card_kpi(
                "ALERTAS CRÍTICOS",
                formatar_numero(
                    criticos
                ),
                (
                    f"{percentual_criticos * 100:.3f}% "
                    "do volume"
                ),
                "!",
                critico=True,
            )
        )

    st.html(
        "<div style='height:27px'></div>"
    )

    # ------------------------------------------------------
    # ÚLTIMA DETECÇÃO
    # ------------------------------------------------------

    st.html(
        render_detection_area(
            transacoes_sinalizadas
        )
    )

    st.html(
        "<div style='height:28px'></div>"
    )

    # ------------------------------------------------------
    # FEED + VISÃO DE RISCO
    # ------------------------------------------------------

    feed_col, overview_col = (
        st.columns(
            [2.15, .85],
            gap="large",
        )
    )

    with feed_col:
        title_col, filter_col = (
            st.columns(
                [1.3, 1],
                gap="small",
            )
        )

        with title_col:
            st.html(
                """
                <div class="section-header">
                    <div>
                        <div class="section-title">
                            Fluxo de Transações
                        </div>

                        <div class="section-description">
                            Fluxo completo ou apenas
                            operações que exigiram atenção
                        </div>
                    </div>
                </div>
                """
            )

        with filter_col:
            filtro_feed = st.radio(
                "Filtro do fluxo",
                [
                    "Todas",
                    "Sinalizadas",
                    "Críticas",
                ],
                horizontal=True,
                label_visibility="collapsed",
                key=(
                    f"filtro_feed_"
                    f"{run_id}"
                ),
            )

        if (
            filtro_feed
            == "Sinalizadas"
        ):
            dataframe_feed = (
                transacoes_sinalizadas
            )

        elif (
            filtro_feed
            == "Críticas"
        ):
            dataframe_feed = (
                alertas_criticos
            )

        else:
            dataframe_feed = (
                transacoes
            )

        st.html(
            render_tabela_transacoes(
                dataframe_feed.head(14)
            )
        )

    with overview_col:
        st.html(
            """
            <div class="section-header">
                <div>
                    <div class="section-title">
                        Visão de Risco
                    </div>

                    <div class="section-description">
                        Qualidade da política operacional
                    </div>
                </div>
            </div>
            """
        )

        recall_pct = (
            float(recall) * 100
            if recall is not None
            else 0
        )

        fig_recall = go.Figure(
            data=[
                go.Pie(
                    values=[
                        recall_pct,
                        max(
                            100
                            - recall_pct,
                            0
                        ),
                    ],
                    hole=.78,
                    sort=False,
                    direction="clockwise",
                    rotation=270,
                    marker=dict(
                        colors=[
                            "#6F82FF",
                            "#1A1E28",
                        ],
                        line=dict(
                            width=0
                        ),
                    ),
                    textinfo="none",
                    hoverinfo="skip",
                )
            ]
        )

        fig_recall.update_layout(
            height=230,
            margin=dict(
                l=15,
                r=15,
                t=5,
                b=5,
            ),
            paper_bgcolor=(
                "rgba(0,0,0,0)"
            ),
            showlegend=False,
            annotations=[
                dict(
                    text=(
                        f"{recall_pct:.1f}%"
                        .replace(
                            ".",
                            ","
                        )
                    ),
                    x=.5,
                    y=.54,
                    showarrow=False,
                    font=dict(
                        size=28,
                        color="#F5F7FB",
                    ),
                ),
                dict(
                    text=(
                        "Cobertura de fraudes"
                    ),
                    x=.5,
                    y=.42,
                    showarrow=False,
                    font=dict(
                        size=9,
                        color="#626B7E",
                    ),
                ),
            ],
        )

        st.plotly_chart(
            fig_recall,
            use_container_width=True,
            theme=None,
            config={
                "displayModeBar": False,
            },
        )

        st.html(
            f"""
            <div class="risk-metrics-grid">
                <div class="risk-mini-card">
                    <div class="risk-mini-label">
                        Precisão
                    </div>

                    <div class="risk-mini-value">
                        {formatar_percentual(
                            precision_encaminhamento,
                            1
                        )}
                    </div>
                </div>

                <div class="risk-mini-card">
                    <div class="risk-mini-label">
                        Taxa sinalizada
                    </div>

                    <div class="risk-mini-value">
                        {formatar_percentual(
                            percentual_encaminhado,
                            2
                        )}
                    </div>
                </div>

                <div class="risk-mini-card">
                    <div class="risk-mini-label">
                        Fraudes nos críticos
                    </div>

                    <div class="risk-mini-value">
                        {formatar_percentual(
                            taxa_fraude_critica,
                            1
                        )}
                    </div>
                </div>

                <div class="risk-mini-card">
                    <div class="risk-mini-label">
                        Ticket médio
                    </div>

                    <div class="risk-mini-value">
                        {html.escape(
                            formatar_moeda(
                                valores.get(
                                    "ticket_medio"
                                )
                            )
                        )}
                    </div>
                </div>
            </div>
            """
        )

    st.html(
        "<div style='height:30px'></div>"
    )

    # ------------------------------------------------------
    # EVOLUÇÃO DAS SINALIZAÇÕES
    # ------------------------------------------------------

    evolucao_col, avaliacao_col = (
        st.columns(
            [1.7, 1],
            gap="large",
        )
    )

    with evolucao_col:
        st.html(
            """
            <div class="section-header">
                <div>
                    <div class="section-title">
                        Evolução Recente das Sinalizações
                    </div>

                    <div class="section-description">
                        Sequência acumulada das últimas operações
                        enviadas para revisão ou alerta crítico
                    </div>
                </div>
            </div>
            """
        )

        if not transacoes_sinalizadas.empty:
            evolucao = (
                transacoes_sinalizadas
                .copy()
            )

            evolucao[
                "trans_date_trans_time"
            ] = pd.to_datetime(
                evolucao[
                    "trans_date_trans_time"
                ]
            )

            evolucao = (
                evolucao
                .sort_values(
                    "trans_date_trans_time"
                )
                .reset_index(
                    drop=True
                )
            )

            evolucao[
                "revisao_evento"
            ] = (
                evolucao[
                    "decisao"
                ]
                .eq(
                    "REVISAR"
                )
                .astype(int)
            )

            evolucao[
                "critico_evento"
            ] = (
                evolucao[
                    "decisao"
                ]
                .eq(
                    "ALERTA_CRITICO"
                )
                .astype(int)
            )

            evolucao[
                "revisao_acumulada"
            ] = (
                evolucao[
                    "revisao_evento"
                ]
                .cumsum()
            )

            evolucao[
                "criticos_acumulados"
            ] = (
                evolucao[
                    "critico_evento"
                ]
                .cumsum()
            )

            fig_evolucao = (
                go.Figure()
            )

            fig_evolucao.add_trace(
                go.Scatter(
                    x=evolucao[
                        "trans_date_trans_time"
                    ],
                    y=evolucao[
                        "revisao_acumulada"
                    ],
                    mode="lines+markers",
                    name="Revisão",
                    line=dict(
                        color="#FBBF24",
                        width=2.5,
                        shape="hv",
                    ),
                    marker=dict(
                        size=5,
                        color="#FBBF24",
                    ),
                    hovertemplate=(
                        "<b>Revisão</b><br>"
                        "%{y} acumuladas"
                        "<extra></extra>"
                    ),
                )
            )

            fig_evolucao.add_trace(
                go.Scatter(
                    x=evolucao[
                        "trans_date_trans_time"
                    ],
                    y=evolucao[
                        "criticos_acumulados"
                    ],
                    mode="lines+markers",
                    name="Alertas críticos",
                    line=dict(
                        color="#FB7185",
                        width=2.8,
                        shape="hv",
                    ),
                    marker=dict(
                        size=6,
                        color="#FB7185",
                    ),
                    hovertemplate=(
                        "<b>Críticos</b><br>"
                        "%{y} acumulados"
                        "<extra></extra>"
                    ),
                )
            )

            fig_evolucao.update_layout(
                height=255,
                margin=dict(
                    l=5,
                    r=10,
                    t=5,
                    b=5,
                ),
                paper_bgcolor=(
                    "rgba(0,0,0,0)"
                ),
                plot_bgcolor=(
                    "rgba(0,0,0,0)"
                ),
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(
                        color="#8E97AA",
                        size=9,
                    ),
                ),
                xaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    tickfont=dict(
                        color="#626B7E",
                        size=9,
                    ),
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor=(
                        "rgba(255,255,255,.04)"
                    ),
                    zeroline=False,
                    rangemode="tozero",
                    tickfont=dict(
                        color="#626B7E",
                        size=9,
                    ),
                ),
                hoverlabel=dict(
                    bgcolor="#151A24",
                    bordercolor=(
                        "rgba(255,255,255,.08)"
                    ),
                    font_color="#F5F7FB",
                ),
            )

            st.plotly_chart(
                fig_evolucao,
                use_container_width=True,
                theme=None,
                config={
                    "displayModeBar": False,
                },
            )

        else:
            st.html(
                """
                <div style="
                    color:#626B7E;
                    font-size:11px;
                    padding:70px 0;
                    text-align:center;
                ">
                    Aguardando primeiras sinalizações.
                </div>
                """
            )

    with avaliacao_col:
        st.html(
            render_evaluation(
                fraudes
            )
        )

    st.html(
        "<div style='height:30px'></div>"
    )

    # ------------------------------------------------------
    # COMPOSIÇÃO + CATEGORIAS
    # ------------------------------------------------------

    composicao_col, categorias_col = (
        st.columns(
            [1, 1.55],
            gap="large",
        )
    )

    with composicao_col:
        st.html(
            render_flagged_composition(
                sinalizacoes
            )
        )

    with categorias_col:
        st.html(
            """
            <div class="section-header">
                <div>
                    <div class="section-title">
                        Categorias de Maior Risco
                    </div>

                    <div class="section-description">
                        Ranking das categorias com maior
                        volume de transações sinalizadas
                    </div>
                </div>
            </div>
            """
        )

        st.html(
            render_category_ranking(
                categorias
            )
        )


# ==========================================================
# EXECUÇÃO
# ==========================================================

render_dashboard_live(
    run_id
)
