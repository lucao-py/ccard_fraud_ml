"""Ponto de entrada da central de monitoramento antifraude."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.views.overview import render_overview_page
from dashboard.styles import APP_CSS
from src.dashboard_queries import buscar_execucao_ativa


st.set_page_config(
    page_title="Sentinela de Fraudes",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.html(APP_CSS)


def _render_brand() -> None:
    st.html("""
    <div class="brand-lockup">
        <div class="brand-mark"><span class="brand-symbol">◇</span>Sentinela de Fraudes</div>
        <div class="brand-subtitle">Inteligência e monitoramento transacional</div>
    </div>
    """)


def _render_waiting_state() -> None:
    st.html("""
    <div class="page-header">
        <div>
            <div class="page-eyebrow">Sistema inicializando</div>
            <h1 class="page-title">Preparando o monitoramento</h1>
            <div class="page-subtitle">
                A central será atualizada automaticamente assim que as primeiras transações chegarem.
            </div>
        </div>
    </div>
    <div class="empty-state" style="min-height:360px;display:grid;place-items:center">
        <div><span style="color:#9aabff;font-size:1.35rem">◇</span><br><br>
        Aguardando as primeiras transações...</div>
    </div>
    """)


execucao = buscar_execucao_ativa()

if execucao is None:
    with st.sidebar:
        _render_brand()
        st.html("""
        <div class="sidebar-foot">
            <span class="sidebar-live"></span>Inicializando processamento<br>
            Preparando o fluxo transacional
        </div>
        """)

    @st.fragment(run_every="1s")
    def _wait_for_processing() -> None:
        if buscar_execucao_ativa() is not None:
            st.rerun(scope="app")
        _render_waiting_state()

    _wait_for_processing()
    st.stop()

run_id = execucao["run_id"]


@st.fragment(run_every="2s")
def _render_monitoring_status() -> None:
    estado_atual = buscar_execucao_ativa() or execucao
    status = estado_atual.get("status")
    processadas = int(estado_atual.get("processadas") or 0)

    if status == "FAILED":
        status_label = "Sistema temporariamente indisponível"
        dot_style = "background:#fb7185;box-shadow:0 0 9px rgba(251,113,133,.55)"
    elif status == "RUNNING":
        status_label = "Monitoramento ativo"
        dot_style = ""
    else:
        status_label = "Sistema ativo"
        dot_style = ""

    st.html(f"""
    <div class="sidebar-foot">
        <span class="sidebar-live" style="{dot_style}"></span>{status_label}<br>
        {processadas:,} transações processadas
    </div>
    """.replace(",", "."))

with st.sidebar:
    _render_brand()
    _render_monitoring_status()

render_overview_page(run_id)
