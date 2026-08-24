"""Sistema visual compartilhado do dashboard."""

APP_CSS = r"""
<style>
:root {
    --bg: #07090d;
    --sidebar: #0a0d12;
    --surface: #10141c;
    --surface-raised: #141924;
    --surface-soft: #0d1118;
    --border: rgba(255, 255, 255, .075);
    --border-strong: rgba(255, 255, 255, .115);
    --text: #f4f6fb;
    --text-soft: #c8ceda;
    --muted: #8b94a7;
    --faint: #596274;
    --blue: #7187ff;
    --blue-soft: #9aabff;
    --purple: #9567f5;
    --green: #4ade80;
    --amber: #f4bd50;
    --red: #fb7185;
}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
        "SF Pro Text", Inter, "Segoe UI", sans-serif;
}

.stApp {
    color: var(--text);
    background:
        radial-gradient(circle at 74% -16%, rgba(113, 135, 255, .10), transparent 29%),
        radial-gradient(circle at 20% -8%, rgba(149, 103, 245, .045), transparent 24%),
        var(--bg);
}

.block-container {
    max-width: 1500px;
    padding: 1.65rem 2rem 4rem;
}

#MainMenu, footer, [data-testid="stDecoration"] {
    visibility: hidden !important;
}

header[data-testid="stHeader"] { background: transparent; }

section[data-testid="stSidebar"] {
    background: var(--sidebar);
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] > div { padding-top: 1.55rem; }
section[data-testid="stSidebar"] hr { border-color: var(--border); }

.brand-lockup { padding: .15rem .15rem 1.7rem; }
.brand-mark {
    display: flex;
    align-items: center;
    gap: .65rem;
    color: var(--text);
    font-size: 1.05rem;
    font-weight: 735;
    letter-spacing: -.035em;
}
.brand-symbol {
    display: inline-grid;
    place-items: center;
    width: 28px;
    height: 28px;
    border: 1px solid rgba(113, 135, 255, .34);
    border-radius: 9px;
    color: var(--blue-soft);
    background: rgba(113, 135, 255, .09);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .05);
}
.brand-subtitle {
    margin: .5rem 0 0 2.42rem;
    color: var(--faint);
    font-size: .66rem;
}
.sidebar-label {
    margin: .15rem 0 .55rem;
    color: var(--faint);
    font-size: .57rem;
    font-weight: 760;
    letter-spacing: .12em;
    text-transform: uppercase;
}
.sidebar-foot {
    margin-top: 1.4rem;
    padding: .78rem .85rem;
    border: 1px solid var(--border);
    border-radius: 12px;
    color: var(--muted);
    background: rgba(255, 255, 255, .018);
    font-size: .63rem;
    line-height: 1.55;
}
.sidebar-live {
    display: inline-block;
    width: 6px;
    height: 6px;
    margin-right: 6px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 9px rgba(74, 222, 128, .55);
}

[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
    display: none;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] [role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 5px;
}
[data-testid="stSidebar"] [data-testid="stRadioOption"] {
    min-height: 42px;
    padding: 0 11px;
    border: 1px solid transparent;
    border-radius: 10px;
    transition: background .15s ease, border-color .15s ease;
}
[data-testid="stSidebar"] [data-testid="stRadioOption"]:hover {
    background: rgba(255, 255, 255, .025);
}
[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] {
    background: rgba(113, 135, 255, .10);
    border-color: rgba(113, 135, 255, .16);
}
[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div > div:first-child {
    display: none;
}
[data-testid="stSidebar"] [data-testid="stRadioOption"] p {
    color: var(--muted);
    font-size: .78rem;
    font-weight: 610;
}
[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] p {
    color: var(--blue-soft);
    font-weight: 680;
}

div[data-baseweb="select"] > div,
div[data-testid="stSelectbox"] [role="group"],
div[data-testid="stSelectbox"] input,
div[data-testid="stSelectbox"] button,
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    min-height: 42px;
    color: var(--text-soft) !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}
div[data-baseweb="select"] > div:focus-within,
div[data-testid="stSelectbox"] [role="group"]:focus-within,
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(113, 135, 255, .42) !important;
    box-shadow: 0 0 0 3px rgba(113, 135, 255, .07) !important;
}
div[data-testid="stWidgetLabel"] p {
    color: var(--muted);
    font-size: .66rem;
    font-weight: 620;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 24px;
    margin-bottom: 1.5rem;
}
.page-eyebrow {
    margin-bottom: .45rem;
    color: var(--blue-soft);
    font-size: .63rem;
    font-weight: 770;
    letter-spacing: .14em;
    text-transform: uppercase;
}
.page-title {
    margin: 0;
    color: var(--text);
    font-size: clamp(1.72rem, 2.5vw, 2.15rem);
    font-weight: 735;
    letter-spacing: -.048em;
    line-height: 1.06;
}
.page-subtitle {
    max-width: 660px;
    margin-top: .58rem;
    color: var(--muted);
    font-size: .83rem;
    line-height: 1.5;
}
.header-meta { text-align: right; padding-top: .15rem; }
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: .46rem;
    padding: .42rem .7rem;
    border: 1px solid rgba(113, 135, 255, .22);
    border-radius: 999px;
    color: var(--blue-soft);
    background: rgba(113, 135, 255, .08);
    font-size: .61rem;
    font-weight: 730;
    letter-spacing: .04em;
}
.status-pill.live { color: var(--green); border-color: rgba(74,222,128,.2); background: rgba(74,222,128,.07); }
.status-pill.failed { color: var(--red); border-color: rgba(251,113,133,.2); background: rgba(251,113,133,.07); }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; box-shadow: 0 0 9px currentColor; }
.header-version { margin-top: .5rem; color: var(--faint); font-size: .57rem; }

.section-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 16px;
    margin: 0 0 .72rem;
}
.section-title { color: var(--text); font-size: .86rem; font-weight: 680; letter-spacing: -.018em; }
.section-description { margin-top: .23rem; color: var(--faint); font-size: .62rem; line-height: 1.4; }
.section-meta { color: var(--blue-soft); font-size: .58rem; font-weight: 650; white-space: nowrap; }
.spacer-16 { height: 16px; }
.spacer-22 { height: 22px; }
.spacer-28 { height: 28px; }

.kpi-card {
    min-height: 124px;
    padding: 1.08rem 1.14rem;
    border: 1px solid var(--border);
    border-radius: 16px;
    background: linear-gradient(145deg, rgba(255,255,255,.025), rgba(255,255,255,.004)), var(--surface);
    box-shadow: 0 14px 40px rgba(0,0,0,.12), inset 0 1px 0 rgba(255,255,255,.018);
}
.kpi-top { display: flex; align-items: center; justify-content: space-between; }
.kpi-icon {
    display: grid;
    place-items: center;
    width: 28px;
    height: 28px;
    border-radius: 8px;
    color: var(--blue-soft);
    background: rgba(113,135,255,.09);
    font-size: .75rem;
}
.kpi-accent { width: 5px; height: 5px; border-radius: 50%; background: var(--blue); opacity: .65; }
.kpi-label { margin-top: .9rem; color: var(--muted); font-size: .62rem; font-weight: 660; letter-spacing: .035em; }
.kpi-value { margin-top: .28rem; color: var(--text); font-size: 1.54rem; font-weight: 735; letter-spacing: -.045em; line-height: 1; }
.kpi-detail { margin-top: .46rem; color: var(--faint); font-size: .59rem; }
.kpi-card.review .kpi-icon, .kpi-card.review .kpi-accent { color: var(--amber); background-color: rgba(244,189,80,.1); }
.kpi-card.released .kpi-icon, .kpi-card.released .kpi-accent { color: var(--green); background-color: rgba(74,222,128,.1); }
.kpi-card.released { border-color: rgba(74,222,128,.11); }
.kpi-card.critical { border-color: rgba(251,113,133,.12); }
.kpi-card.critical .kpi-icon, .kpi-card.critical .kpi-accent { color: var(--red); background-color: rgba(251,113,133,.1); }
.kpi-card.critical .kpi-value { color: #ff8b9b; }
.kpi-card.commercial-kpi { box-sizing: border-box; height: 171px; }

.detection-shell {
    padding: .95rem;
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(251,113,133,.025), rgba(113,135,255,.015)), var(--surface-soft);
    box-shadow: 0 18px 52px rgba(0,0,0,.14);
}
.detection-grid { display: grid; grid-template-columns: minmax(0, 1.8fr) minmax(230px, .95fr); gap: 10px; }
.latest-detection {
    min-height: 184px;
    padding: 1.08rem 1.15rem;
    border: 1px solid rgba(244,189,80,.17);
    border-radius: 14px;
    background: radial-gradient(circle at 92% 8%, rgba(244,189,80,.07), transparent 28%), var(--surface-raised);
}
.latest-detection.critical { border-color: rgba(251,113,133,.18); background: radial-gradient(circle at 92% 8%, rgba(251,113,133,.075), transparent 28%), var(--surface-raised); }
.latest-top, .recent-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.decision-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 7px;
    border: 1px solid currentColor;
    border-radius: 999px;
    font-size: .48rem;
    font-weight: 790;
    letter-spacing: .06em;
    text-transform: uppercase;
}
.decision-badge::before { content: ""; width: 5px; height: 5px; border-radius: 50%; background: currentColor; }
.approved { color: var(--green); background: rgba(74,222,128,.07); border-color: rgba(74,222,128,.19); }
.review { color: var(--amber); background: rgba(244,189,80,.07); border-color: rgba(244,189,80,.2); }
.critical { color: var(--red); background: rgba(251,113,133,.07); border-color: rgba(251,113,133,.2); }
.latest-score { color: var(--amber); font-size: 2rem; font-weight: 760; letter-spacing: -.055em; line-height: .92; text-align: right; }
.latest-detection.critical .latest-score { color: var(--red); }
.score-caption { margin-top: 5px; color: var(--faint); font-size: .52rem; text-align: right; }
.latest-name { margin-top: 1.55rem; color: var(--text); font-size: 1rem; font-weight: 700; letter-spacing: -.025em; }
.latest-merchant { margin-top: .3rem; color: var(--text-soft); font-size: .64rem; }
.detail-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 1rem; }
.detail-chip { padding: 5px 7px; border: 1px solid rgba(255,255,255,.055); border-radius: 8px; color: var(--muted); background: rgba(255,255,255,.022); font-size: .54rem; }
.detail-chip strong { color: var(--text-soft); font-weight: 670; }
.recent-stack { display: grid; grid-template-rows: 1fr 1fr; gap: 9px; }
.recent-card { min-height: 86px; padding: .78rem .85rem; border: 1px solid var(--border); border-radius: 13px; background: var(--surface-raised); }
.recent-score { color: var(--text); font-size: .93rem; font-weight: 740; letter-spacing: -.035em; }
.recent-name { margin-top: .65rem; color: var(--text-soft); font-size: .62rem; font-weight: 660; }
.recent-meta { margin-top: .2rem; color: var(--faint); font-size: .51rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.empty-state { padding: 3rem 1rem; border: 1px dashed rgba(113,135,255,.17); border-radius: 14px; color: var(--muted); background: rgba(113,135,255,.018); text-align: center; font-size: .72rem; }

.feed-shell { overflow: hidden; border: 1px solid var(--border); border-radius: 16px; background: var(--surface); }
.feed-scroll { max-height: 462px; overflow-y: auto; }
.feed-table { width: 100%; border-collapse: collapse; table-layout: fixed; }
.feed-table thead { position: sticky; top: 0; z-index: 2; background: #131823; }
.feed-table th { padding: 10px 12px; color: var(--faint); font-size: .49rem; font-weight: 760; letter-spacing: .08em; text-align: left; }
.feed-table td { padding: 11px 12px; border-top: 1px solid rgba(255,255,255,.042); color: var(--text-soft); font-size: .6rem; vertical-align: middle; }
.feed-table tbody tr:hover { background: rgba(113,135,255,.025); }
.feed-time { color: var(--faint); font-variant-numeric: tabular-nums; }
.feed-primary { color: var(--text-soft); font-weight: 640; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.feed-secondary { margin-top: 3px; color: var(--faint); font-size: .51rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.feed-amount { color: var(--text); font-weight: 680; white-space: nowrap; }
.risk-line { display: flex; align-items: center; gap: 8px; }
.risk-number { min-width: 42px; font-weight: 700; font-variant-numeric: tabular-nums; }
.risk-number.tone-approved { color: var(--green); }
.risk-number.tone-review { color: var(--amber); }
.risk-number.tone-critical { color: var(--red); }
.risk-track { flex: 1; height: 3px; overflow: hidden; border-radius: 99px; background: rgba(255,255,255,.07); }
.risk-fill { height: 100%; min-width: 2px; border-radius: inherit; }
.risk-fill.tone-approved { background: var(--green); }
.risk-fill.tone-review { background: var(--amber); }
.risk-fill.tone-critical { background: var(--red); }
.risk-explainer { position: relative; outline: none; cursor: help; }
.risk-decision { margin-top: 5px; }
.decision-explanation {
    position: fixed;
    z-index: 10000;
    top: 50%;
    right: max(18px, env(safe-area-inset-right));
    box-sizing: border-box;
    width: min(350px, calc(100vw - 36px));
    padding: 15px;
    border: 1px solid rgba(154,171,255,.18);
    border-radius: 14px;
    color: var(--text-soft);
    background:
        radial-gradient(circle at 92% 4%, rgba(113,135,255,.10), transparent 30%),
        #111620;
    box-shadow: 0 20px 50px rgba(0,0,0,.48), inset 0 1px 0 rgba(255,255,255,.035);
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    transform: translateY(-50%) translateY(5px);
    transition: opacity .14s ease, visibility .14s ease, transform .14s ease;
}
.feed-table tbody tr:hover .decision-explanation,
.risk-explainer:focus-within .decision-explanation {
    opacity: 1;
    visibility: visible;
    transform: translateY(-50%);
}
.explanation-eyebrow {
    color: var(--blue-soft);
    font-size: .52rem;
    font-weight: 790;
    letter-spacing: .1em;
    text-transform: uppercase;
}
.explanation-score-row {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 16px;
    margin-top: 12px;
    color: var(--muted);
    font-size: .59rem;
}
.explanation-score-row strong {
    color: var(--text);
    font-size: 1.35rem;
    font-weight: 760;
    letter-spacing: -.045em;
    line-height: 1;
}
.explanation-policy {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-top: 11px;
    padding: 8px 9px;
    border: 1px solid currentColor;
    border-radius: 9px;
    font-size: .54rem;
}
.explanation-policy-label { font-weight: 790; letter-spacing: .045em; text-transform: uppercase; }
.explanation-divider { height: 1px; margin: 13px 0 11px; background: rgba(255,255,255,.065); }
.explanation-subtitle {
    color: var(--muted);
    font-size: .5rem;
    font-weight: 740;
    letter-spacing: .065em;
    text-transform: uppercase;
}
.explanation-factors { display: flex; flex-direction: column; gap: 9px; margin-top: 10px; }
.explanation-factor {
    display: grid;
    grid-template-columns: 12px minmax(112px, 1fr) 92px;
    align-items: center;
    gap: 7px;
}
.explanation-arrow { font-size: .7rem; font-weight: 800; }
.explanation-feature { color: var(--text-soft); font-size: .57rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.explanation-factor.aumenta .explanation-arrow { color: var(--red); }
.explanation-factor.reduz .explanation-arrow { color: var(--green); }
.explanation-factor.neutro .explanation-arrow { color: var(--muted); }
.explanation-track { height: 4px; overflow: hidden; border-radius: 999px; background: rgba(255,255,255,.07); }
.explanation-fill { display: block; height: 100%; min-width: 2px; border-radius: inherit; }
.explanation-factor.aumenta .explanation-fill { background: linear-gradient(90deg, #9567f5, var(--red)); }
.explanation-factor.reduz .explanation-fill { background: linear-gradient(90deg, var(--blue), var(--green)); }
.explanation-factor.neutro .explanation-fill { background: var(--muted); }
.explanation-legend { display: flex; gap: 14px; margin-top: 12px; color: var(--faint); font-size: .49rem; }
.explanation-legend .aumenta { color: #d97486; }
.explanation-legend .reduz { color: #61bd7f; }
.explanation-empty {
    padding: 11px;
    border: 1px dashed rgba(154,171,255,.14);
    border-radius: 9px;
    color: var(--muted);
    background: rgba(113,135,255,.025);
    font-size: .55rem;
    line-height: 1.45;
}

@supports (anchor-name: --risk-anchor) {
    .decision-explanation {
        top: auto;
        right: auto;
        margin: 0 0 10px;
        position-area: block-start span-inline-start;
        position-try-fallbacks: flip-block, flip-inline;
        transform: translateY(5px);
    }
    .feed-table tbody tr:hover .decision-explanation,
    .risk-explainer:focus-within .decision-explanation {
        transform: translateY(0);
    }
}

.insight-card { box-sizing: border-box; min-height: 245px; padding: 1rem 1.05rem; border: 1px solid var(--border); border-radius: 16px; background: var(--surface); }
.quality-card, .category-card { height: 380px; }
.insight-card-title { color: var(--text); font-size: .78rem; font-weight: 670; }
.insight-card-subtitle { margin-top: .22rem; color: var(--faint); font-size: .58rem; }
.quality-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-top: .9rem; }
.quality-item { padding: .75rem; border: 1px solid rgba(255,255,255,.055); border-radius: 11px; background: rgba(255,255,255,.018); }
.quality-value { color: var(--text); font-size: 1.05rem; font-weight: 720; letter-spacing: -.035em; }
.quality-label { margin-top: .25rem; color: var(--faint); font-size: .5rem; font-weight: 680; letter-spacing: .045em; text-transform: uppercase; }
.quality-note { margin-top: .85rem; color: var(--faint); font-size: .53rem; line-height: 1.45; }
.category-list { display: flex; flex-direction: column; gap: 9px; margin-top: .9rem; }
.category-row { padding-bottom: 9px; border-bottom: 1px solid rgba(255,255,255,.04); }
.category-row:last-child { padding-bottom: 0; border-bottom: 0; }
.category-top { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.category-name { color: var(--text-soft); font-size: .61rem; font-weight: 640; }
.category-meta { margin-top: 2px; color: var(--faint); font-size: .49rem; }
.category-count { color: var(--text); font-size: .66rem; font-weight: 700; }
.category-track { height: 3px; margin-top: 6px; overflow: hidden; border-radius: 99px; background: rgba(255,255,255,.055); }
.category-fill { height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--blue), var(--purple)); }

.commercial-card {
    box-sizing: border-box;
    padding: 1.05rem 1.1rem;
    border: 1px solid var(--border);
    border-radius: 16px;
    background:
        linear-gradient(145deg, rgba(255,255,255,.018), rgba(255,255,255,.002)),
        var(--surface);
}
.commercial-flow-card, .efficiency-card { height: 295px; }
.commercial-card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.commercial-total { display: flex; flex-direction: column; align-items: flex-end; white-space: nowrap; }
.commercial-total strong { color: var(--text); font-size: 1rem; font-weight: 730; letter-spacing: -.03em; }
.commercial-total span { margin-top: 3px; color: var(--faint); font-size: .48rem; text-transform: uppercase; letter-spacing: .055em; }
.money-segment {
    display: flex;
    width: 100%;
    height: 9px;
    margin-top: 1.2rem;
    overflow: hidden;
    border-radius: 999px;
    background: rgba(255,255,255,.05);
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.025);
}
.money-segment > span { min-width: 2px; }
.money-segment-approved { background: var(--green); }
.money-segment-review { background: var(--amber); }
.money-segment-critical { background: var(--red); }
.money-ledger { display: flex; flex-direction: column; margin-top: .9rem; }
.money-row {
    display: grid;
    grid-template-columns: 7px minmax(120px, 1fr) auto 54px;
    align-items: center;
    gap: 8px;
    min-height: 46px;
    border-top: 1px solid rgba(255,255,255,.042);
}
.money-row:first-child { border-top: 0; }
.money-row .money-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.money-row.approved-row { color: var(--green); }
.money-row.review-row { color: var(--amber); }
.money-row.critical-row { color: var(--red); }
.money-label { color: var(--text-soft); font-size: .61rem; font-weight: 620; }
.money-row strong { color: var(--text); font-size: .64rem; font-weight: 680; white-space: nowrap; }
.money-share { color: var(--muted); font-size: .57rem; text-align: right; font-variant-numeric: tabular-nums; }

.efficiency-card {
    background:
        radial-gradient(circle at 92% 4%, rgba(113,135,255,.075), transparent 32%),
        var(--surface);
}
.efficiency-kicker { color: var(--blue-soft); font-size: .52rem; font-weight: 760; letter-spacing: .09em; text-transform: uppercase; }
.efficiency-value { margin-top: .55rem; color: var(--text); font-size: 1.62rem; font-weight: 750; letter-spacing: -.045em; line-height: 1; }
.efficiency-caption { margin-top: .38rem; color: var(--faint); font-size: .55rem; }
.tradeoff-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 1rem; }
.tradeoff-item { padding: .72rem; border: 1px solid rgba(255,255,255,.052); border-radius: 11px; background: rgba(255,255,255,.016); }
.tradeoff-item strong { display: block; color: var(--text); font-size: 1.12rem; font-weight: 730; letter-spacing: -.035em; }
.tradeoff-item.coverage strong { color: var(--green); }
.tradeoff-item.friction strong { color: var(--amber); }
.tradeoff-item span { display: block; margin-top: .28rem; color: var(--faint); font-size: .48rem; font-weight: 670; letter-spacing: .035em; text-transform: uppercase; }
.efficiency-foot { display: flex; justify-content: space-between; gap: 12px; margin-top: .85rem; color: var(--faint); font-size: .49rem; }
.efficiency-foot strong { color: var(--text-soft); font-weight: 650; white-space: nowrap; }

.financial-category-card { height: 360px; }
.financial-category-list { display: flex; flex-direction: column; gap: 8px; margin-top: .9rem; }
.financial-category-row { padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,.04); }
.financial-category-row:last-child { padding-bottom: 0; border-bottom: 0; }
.financial-category-value { color: var(--text); font-size: .62rem; font-weight: 700; white-space: nowrap; }
.financial-category-fill { height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--purple), var(--red)); }
.commercial-timeline-empty { min-height: 360px; display: grid; place-items: center; }

div[data-testid="stPlotlyChart"] {
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: 16px;
    background: var(--surface);
}
.timeline-empty {
    min-height: 380px;
    display: grid;
    place-items: center;
}

[data-testid="stButtonGroup"] [role="radiogroup"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    width: 100%;
}
[data-testid="stButtonGroup"] button[data-variant="segmented_control"] {
    flex: 1 1 0 !important;
    min-width: 0 !important;
    min-height: 34px;
    border-color: var(--border) !important;
    color: var(--muted) !important;
    background: var(--surface) !important;
    font-size: .65rem;
    font-weight: 630;
}
[data-testid="stButtonGroup"] button[data-variant="segmented_control"][data-selected="true"] {
    color: var(--blue-soft) !important;
    border-color: rgba(113,135,255,.22) !important;
    background: rgba(113,135,255,.105) !important;
}

@media (max-width: 1100px) {
    .block-container { padding-left: 1.25rem; padding-right: 1.25rem; }
    .detection-grid { grid-template-columns: 1fr; }
    .recent-stack { grid-template-columns: 1fr 1fr; grid-template-rows: auto; }
    .feed-table th:nth-child(3), .feed-table td:nth-child(3) { display: none; }
}

@media (max-width: 720px) {
    .page-header { flex-direction: column; }
    .header-meta { text-align: left; }
    .detection-grid, .recent-stack, .quality-grid { grid-template-columns: 1fr; }
    .quality-card, .category-card { height: auto; }
    .commercial-flow-card, .efficiency-card, .financial-category-card { height: auto; }
    .kpi-card.commercial-kpi { height: auto; }
    .money-row { grid-template-columns: 7px 1fr auto; }
    .money-share { display: none; }
    .tradeoff-grid { grid-template-columns: 1fr; }
    .efficiency-foot { flex-direction: column; }
    .feed-table th:nth-child(2), .feed-table td:nth-child(2) { width: 40%; }
}
</style>
"""
