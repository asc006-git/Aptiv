import json
import time
import io
import sys
import math
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(
    page_title="APTIV OS // TALENT INTELLIGENCE PLATFORM",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}
div[data-testid="stToolbar"] {display: none;}

.stApp {
    background-color: #000000 !important;
    color: #e0e0e0 !important;
}

/* === TYPOGRAPHY SYSTEM === */
body, p, label, li, div.stMarkdown, div[data-testid="stMarkdownContainer"],
.reading-text, .candidate-info, .narrative-text, .filter-label {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    font-size: 0.9375em !important;
    font-weight: 400 !important;
    color: #d4d4d4 !important;
    line-height: 1.6 !important;
}

/* Orbitron: major page titles, workflow stages, section headers, KPI labels only */
.orbitron-title, .workflow-step, .section-header, .kpi-label,
h1, h2, h3, h4, h5, h6 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}

h1 { font-size: 1.4em !important; letter-spacing: 2px !important; }
h2 { font-size: 1.2em !important; }
h3 { font-size: 1.05em !important; }
h4 { font-size: 0.9em !important; }
h5 { font-size: 0.8em !important; }
h6 { font-size: 0.75em !important; }

.section-header {
    font-size: 0.72em !important;
    letter-spacing: 1.8px !important;
    color: #777777 !important;
    margin-bottom: 14px !important;
    padding-bottom: 8px !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
}

/* JetBrains Mono: data, metrics, code, IDs */
code, pre, td, .mono-text, .metric-value, .candidate-id, .rank-num, .score-num,
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
}

[data-testid="stMetricValue"] {
    font-size: 1.4em !important;
    font-weight: 600 !important;
    color: #ffffff !important;
}

[data-testid="stMetricLabel"] {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.65em !important;
    letter-spacing: 1.5px !important;
    color: #777777 !important;
    text-transform: uppercase !important;
}

/* === CARDS & PANELS === */
.card, .insight-card, .glass-panel {
    background: rgba(14, 14, 14, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}

.card:hover, .insight-card:hover {
    border-color: rgba(255, 255, 255, 0.18) !important;
    background: rgba(18, 18, 18, 0.95) !important;
}

.card.selected {
    border-color: rgba(255, 255, 255, 0.4) !important;
    background: rgba(22, 22, 22, 0.95) !important;
    box-shadow: 0 0 0 1px rgba(255,255,255,0.15) !important;
}

/* === METRIC STYLING === */
div[data-testid="stMetric"] {
    background: rgba(14, 14, 14, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important;
    border-radius: 8px !important;
    padding: 16px 12px !important;
    text-align: center !important;
}

/* === INPUTS === */
div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"],
div[data-baseweb="multiselect"] {
    background-color: rgba(10, 10, 10, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 6px !important;
    transition: border-color 0.15s !important;
}
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
    border-color: rgba(255, 255, 255, 0.4) !important;
}

input, textarea {
    color: #ffffff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85em !important;
}

div[data-baseweb="tag"] {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    color: #d4d4d4 !important;
    border-radius: 4px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8em !important;
}

/* === BUTTONS === */
div.stButton button {
    background: rgba(18, 18, 18, 0.9) !important;
    color: #d4d4d4 !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8em !important;
    font-weight: 500 !important;
    letter-spacing: 0.3px !important;
    padding: 8px 14px !important;
    transition: all 0.15s ease !important;
}
div.stButton button:hover {
    color: #ffffff !important;
    background: rgba(30, 30, 30, 0.95) !important;
    border-color: rgba(255, 255, 255, 0.3) !important;
}

div.stButton button[kind="primary"],
div.stButton button[data-testid="stBaseButton-primary"] {
    background: rgba(255, 255, 255, 0.06) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    font-weight: 600 !important;
}
div.stButton button[kind="primary"]:hover,
div.stButton button[data-testid="stBaseButton-primary"]:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    border-color: #ffffff !important;
}

div.stButton button:disabled {
    opacity: 0.3 !important;
}

/* === EXPANDER === */
div[data-testid="stExpander"] {
    background: rgba(14, 14, 14, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
    overflow: hidden !important;
}
div[data-testid="stExpander"]:hover {
    border-color: rgba(255, 255, 255, 0.15) !important;
}
div[data-testid="stExpander"] summary {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85em !important;
    letter-spacing: 0.5px !important;
    color: #ffffff !important;
    padding: 8px 4px !important;
}
div[data-testid="stExpander"] summary p {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    margin: 0 !important;
}

/* === TABS === */
div[role="tablist"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
    gap: 0 !important;
    margin-bottom: 20px !important;
}
button[role="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.8em !important;
    letter-spacing: 0.5px !important;
    color: #666666 !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 8px 16px !important;
    transition: all 0.15s !important;
}
button[role="tab"][aria-selected="true"] {
    color: #ffffff !important;
    border-bottom: 2px solid #ffffff !important;
}
button[role="tab"]:hover {
    color: #cccccc !important;
}

/* === SCROLLBARS === */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }

/* === BADGES === */
.badge {
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 0.65em;
    letter-spacing: 0.3px;
    padding: 2px 8px;
    border-radius: 3px;
    border: 1px solid rgba(255,255,255,0.12);
    color: #bbbbbb;
    background: rgba(255,255,255,0.03);
    margin: 2px 4px 2px 0;
}
.badge.highlight {
    border-color: rgba(255,255,255,0.3);
    color: #ffffff;
    background: rgba(255,255,255,0.06);
}

/* === SKILL CHIPS === */
.skill-chip {
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-size: 0.7em;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid rgba(255,255,255,0.08);
    color: #aaaaaa;
    background: rgba(255,255,255,0.02);
    margin: 2px 4px 2px 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 140px;
}
.skill-chip.relevant {
    border-color: rgba(255,255,255,0.2);
    color: #dddddd;
    background: rgba(255,255,255,0.04);
}

/* === INSIGHT LABEL/VALUE === */
.insight-label {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.7em;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #777777;
}
.insight-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85em;
    color: #ffffff;
    margin-top: 1px;
}

/* === SCORE BAR === */
.score-track {
    background: rgba(255, 255, 255, 0.04);
    border-radius: 4px;
    width: 100%;
    height: 8px;
    margin-top: 4px;
    margin-bottom: 10px;
    overflow: hidden;
}
.score-fill {
    height: 8px;
    background: #ffffff;
    border-radius: 4px;
    transition: width 0.3s ease;
}
.score-fill.penalty {
    background: #555555;
}

/* === LEADERBOARD LIST === */
.leaderboard-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    cursor: pointer;
    transition: background 0.12s;
}
.leaderboard-item:hover {
    background: rgba(255,255,255,0.03);
}
.leaderboard-item.selected {
    background: rgba(255,255,255,0.05);
    border-left: 2px solid #ffffff;
}

/* === DATA TABLE === */
div[data-testid="stDataFrame"] {
    background: transparent !important;
}
div[data-testid="stDataFrame"] td {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75em !important;
    color: #cccccc !important;
    border-bottom: 1px solid rgba(255,255,255,0.04) !important;
}
div[data-testid="stDataFrame"] th {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.7em !important;
    letter-spacing: 0.5px !important;
    color: #888888 !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid rgba(255,255,255,0.08) !important;
}

/* === MISC === */
.avatar {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 6px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    font-family: 'Inter', sans-serif;
    font-size: 0.7em;
    font-weight: 600;
    color: #ffffff;
}

.mono-label {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.72em;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #777777;
}

.mono-value {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    color: #ffffff;
}

.divider-light {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.04);
    margin: 6px 0;
}
</style>
""", unsafe_allow_html=True)

def render_workflow_tracker(current_step):
    steps = [
        ("INGESTION", "01 INGESTION", "INGESTION", None),
        ("EXECUTING", "02 PIPELINE", "EXECUTING", None),
        ("LEADERBOARD", "03 WORKSPACE", "DASHBOARD", 0),
        ("INTELLIGENCE", "04 ANALYSIS", "DASHBOARD", 1),
        ("EXPLAINABILITY", "05 EXPLAINABILITY", "DASHBOARD", 2),
        ("HIDDEN_GEMS", "06 DISCOVERY", "DASHBOARD", 3),
        ("RAP", "07 RAP QUEUE", "DASHBOARD", 4),
        ("EXPORT", "08 EXPORTS", "DASHBOARD", 5)
    ]
    cols = st.columns(len(steps))
    is_done = st.session_state.get("pipeline_done", False)
    active_idx = 0
    for idx, (step_key, _, state_val, tab_val) in enumerate(steps):
        if current_step == step_key:
            active_idx = idx
            break
        elif state_val == "DASHBOARD" and st.session_state.get("app_state") == "DASHBOARD" and st.session_state.get("dashboard_tab") == tab_val:
            active_idx = idx
            break
    for idx, (step_key, label, state_val, tab_val) in enumerate(steps):
        with cols[idx]:
            is_active = (idx == active_idx)
            is_completed = is_done and (idx < active_idx)
            marker = "●" if is_active else "✓" if is_completed else "○"
            btn_label = f"{marker} {label}"
            btn_type = "primary" if is_active else "secondary"
            disabled = (state_val == "DASHBOARD" and not is_done) or (state_val == "EXECUTING" and not is_done and st.session_state.get("uploaded_bytes") is None)
            if st.button(btn_label, key=f"nav_btn_{step_key}_{idx}", use_container_width=True, type=btn_type, disabled=disabled):
                st.session_state.app_state = state_val
                if tab_val is not None:
                    st.session_state.dashboard_tab = tab_val
                st.rerun()

def render_score_bar(label, val, max_val=1.0, is_penalty=False, tooltip="", benchmark=None):
    pct = min(100.0, max(0.0, (val / max_val) * 100)) if max_val > 0 else 0
    pct_display = min(100.0, max(0.0, pct))
    fill_class = " penalty" if is_penalty else ""
    val_display = f"-{val:.3f}" if is_penalty else f"{val:.3f} / {max_val:.2f}"
    benchmark_html = ""
    if benchmark is not None:
        bench_pct = (benchmark / max_val) * 100
        benchmark_html = f'<div style="position:absolute; left:{bench_pct}%; top:-2px; width:2px; height:12px; background:#888; z-index:10;" title="Pool avg: {benchmark:.3f}"></div>'
    tooltip_html = f'<span style="color:#666; font-weight:400; font-size:0.85em;">{tooltip}</span>' if tooltip else ""
    st.markdown(f"""
    <div style="margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items:baseline; font-size: 0.8em; margin-bottom: 2px;">
            <span class="mono-label">{label} {tooltip_html}</span>
            <span class="mono-value" style="font-size:0.9em;">{val_display}</span>
        </div>
        <div class="score-track" style="position:relative;">
            {benchmark_html}
            <div class="score-fill{fill_class}" style="width:{pct_display}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_mono_row(label, val):
    return f"""
    <div style="display:flex; justify-content:space-between; align-items:center; padding:5px 0; border-bottom:1px solid rgba(255,255,255,0.03);">
        <span class="mono-label">{label}</span>
        <span class="mono-value" style="font-size:0.85em;">{val}</span>
    </div>
    """

def count_lines_jsonl(data):
    return len([l for l in data.decode("utf-8").splitlines() if l.strip()])

def render_recruiter_sidebar(df):
    st.sidebar.markdown("""
    <div style="text-align:center; margin-bottom:16px; padding-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.05);">
        <div style="font-family:'Orbitron',sans-serif; font-size:0.9em; font-weight:700; letter-spacing:3px; color:#ffffff;">APTIV OS</div>
        <div style="font-family:'Inter',sans-serif; font-size:0.6em; color:#888; letter-spacing:1.5px; margin-top:2px; text-transform:uppercase;">Operations Control</div>
    </div>
    """, unsafe_allow_html=True)
    active_id = st.session_state.get("selected_candidate_id", "")
    if active_id and active_id in df["candidate_id"].values:
        cand = df[df["candidate_id"] == active_id].iloc[0]
        rank = cand.get("rank", "?")
        score = cand.get("score", 0.0)
        arch = cand.get("archetype", "Standard")
        st.sidebar.markdown(f"""
        <div class="insight-card" style="padding:14px;">
            <div class="mono-label" style="margin-bottom:8px;">Active Selection</div>
            <div style="display:flex; align-items:center; gap:10px;">
                <div class="avatar">{active_id[:2]}</div>
                <div>
                    <div class="mono-value" style="font-size:0.85em;">{active_id}</div>
                    <div style="font-family:'Inter',sans-serif; font-size:0.75em; color:#999; margin-top:1px;">{cand.get('current_title', '')}</div>
                </div>
            </div>
            <hr class="divider-light">
            <div style="display:flex; justify-content:space-between; font-size:0.75em; font-family:'JetBrains Mono',monospace;">
                <span style="color:#888;">RANK #{rank}</span>
                <span style="color:#fff;">SCORE: {score:.4f}</span>
            </div>
            <div style="font-family:'Inter',sans-serif; font-size:0.7em; color:#999; margin-top:4px; text-transform:uppercase; letter-spacing:0.3px;">
                Archetype: <span style="color:#fff;">{arch}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        is_shortlisted = active_id in st.session_state.shortlist
        btn_label = "Remove from Shortlist" if is_shortlisted else "Add to Shortlist"
        if st.sidebar.button(btn_label, key="sidebar_shortlist_toggle", use_container_width=True):
            if is_shortlisted:
                st.session_state.shortlist.remove(active_id)
            else:
                st.session_state.shortlist.add(active_id)
            st.rerun()
    else:
        st.sidebar.markdown(f"""
        <div class="insight-card" style="padding:14px; text-align:center;">
            <div class="mono-label">No candidate selected</div>
        </div>
        """, unsafe_allow_html=True)

    st.sidebar.markdown(f'<div class="section-header" style="margin-top:16px;">Shortlist ({len(st.session_state.shortlist)})</div>', unsafe_allow_html=True)
    shortlist_ids = list(st.session_state.shortlist)
    if not shortlist_ids:
        st.sidebar.markdown('<div style="font-family:Inter,sans-serif; font-size:0.8em; color:#555; text-align:center; padding:10px;">No shortlisted candidates.</div>', unsafe_allow_html=True)
    else:
        for cid in shortlist_ids:
            if cid in df["candidate_id"].values:
                r_row = df[df["candidate_id"] == cid].iloc[0]
                c_rank = r_row.get("rank", "?")
                c_score = r_row.get("score", 0.0)
                st.sidebar.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:6px; padding:6px 10px; margin-bottom:4px;">
                    <div>
                        <span class="mono-value" style="font-size:0.8em;">#{c_rank} {cid}</span>
                        <div style="font-size:0.7em; color:#888; font-family:'JetBrains Mono',monospace;">{c_score:.4f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                col_sl1, col_sl2 = st.sidebar.columns(2)
                with col_sl1:
                    if st.button("View", key=f"sl_view_{cid}", use_container_width=True):
                        st.session_state.selected_candidate_id = cid
                        st.session_state.dashboard_tab = 1
                        st.rerun()
                with col_sl2:
                    if st.button("Remove", key=f"sl_rem_{cid}", use_container_width=True):
                        st.session_state.shortlist.remove(cid)
                        st.rerun()
        st.sidebar.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
        shortlist_df = df[df["candidate_id"].isin(shortlist_ids)][["candidate_id", "rank", "score", "current_title", "current_company", "location", "years_of_experience", "archetype", "narrative"]].copy()
        sl_csv = shortlist_df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("Export CSV", data=sl_csv, file_name="recruiter_shortlist.csv", mime="text/csv", use_container_width=True, key="dl_sl_csv")

    st.sidebar.markdown(f'<div class="section-header" style="margin-top:16px;">System</div>', unsafe_allow_html=True)
    if st.sidebar.button("Ingestion Portal", use_container_width=True, key="sidebar_goto_ingestion"):
        st.session_state.app_state = "INGESTION"
        st.rerun()
    if st.sidebar.button("Reset Pipeline", use_container_width=True, type="secondary", key="sidebar_reset_pipelines"):
        for key in ["app_state", "dataset_name", "candidate_count", "file_size_bytes",
                    "uploaded_bytes", "df", "pipeline_time", "pipeline_memory",
                    "selected_candidate_id", "schema_valid", "pipeline_done", "uploaded_filename", "shortlist", "compare_candidate_id"]:
            if key in st.session_state:
                try:
                    del st.session_state[key]
                except:
                    pass
        st.session_state.shortlist = set()
        st.session_state.app_state = "INGESTION"
        st.rerun()

def render_candidate_card(row, is_selected, is_shortlisted):
    cid = row["candidate_id"]
    rank = row.get("rank", "?")
    score = row.get("score", 0.0)
    title = row.get("current_title", "N/A")
    company = row.get("current_company", "N/A")
    location = row.get("location", "N/A")
    yoe = row.get("years_of_experience", 0.0)
    arch = row.get("archetype", "Standard")
    rap = row.get("rap_priority", "")
    is_hg = row.get("is_hidden_gem", False)
    tier = row.get("display_tier", "")

    badges = []
    if is_hg:
        badges.append(('<span class="badge highlight">Hidden Gem</span>'))
    if rap:
        badges.append(f'<span class="badge">{rap.replace(" ", "&nbsp;")}</span>')
    if tier:
        badges.append(f'<span class="badge">{tier}</span>')
    badges.append(f'<span class="badge">{arch}</span>')
    badges_str = "".join(badges)

    skills_list = row.get("skills_listed", "")
    if isinstance(skills_list, list):
        skills_items = skills_list
    else:
        skills_items = [s.strip() for s in str(skills_list).split(",") if s.strip()]
    highlight_kws = ["vector", "pinecone", "weaviate", "qdrant", "milvus", "faiss", "embeddings",
                     "dense", "ndcg", "mrr", "ranking", "python", "lora", "qlora", "peft", "fine-tune",
                     "nlp", "information retrieval", "search", "retrieval", "distributed", "kubernetes"]
    skill_chips = ""
    for s in skills_items[:8]:
        is_rel = any(k in s.lower() for k in highlight_kws)
        cls = "skill-chip relevant" if is_rel else "skill-chip"
        title_attr = s.replace('"', "'")
        skill_chips += f'<span class="{cls}" title="{title_attr}">{s}</span>'

    selected_class = " selected" if is_selected else ""
    star = "★" if is_shortlisted else "☆"
    star_color = "#ffaa00" if is_shortlisted else "#555"

    st.markdown(f"""
    <div class="card{selected_class}" style="padding:14px 16px; margin-bottom:8px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div style="display:flex; align-items:center; gap:10px; min-width:0; flex:1;">
                <div class="avatar">{cid[:2]}</div>
                <div style="min-width:0;">
                    <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
                        <span class="mono-value" style="font-size:0.85em;">#{rank}</span>
                        <span class="mono-value" style="font-size:0.9em;">{cid}</span>
                        <span style="color:{star_color}; font-size:1em;">{star}</span>
                    </div>
                    <div style="font-family:'Inter',sans-serif; font-size:0.85em; color:#e0e0e0; font-weight:500; margin-top:1px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                        {title} <span style="color:#777;">at</span> {company}
                    </div>
                </div>
            </div>
            <div style="text-align:right; flex-shrink:0;">
                <div class="mono-value" style="font-size:1em; font-weight:600;">{score:.4f}</div>
                <div style="font-family:'Inter',sans-serif; font-size:0.65em; color:#888; margin-top:1px;">FINAL SCORE</div>
            </div>
        </div>
        <hr class="divider-light">
        <div style="display:flex; justify-content:space-between; font-family:'Inter',sans-serif; font-size:0.78em; color:#999;">
            <span>{location}</span>
            <span>{yoe:.1f} yrs experience</span>
        </div>
        <div style="margin-top:8px; display:flex; flex-wrap:wrap; align-items:center;">
            {badges_str}
        </div>
        <div style="margin-top:8px; display:flex; flex-wrap:wrap; gap:2px;">
            {skill_chips}
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("Select & Analyze" if not is_selected else "Active Selection", key=f"card_sel_{cid}", use_container_width=True, type="primary" if is_selected else "secondary"):
            st.session_state.selected_candidate_id = cid
            st.session_state.dashboard_tab = 1
            st.rerun()
    with col_btn2:
        sl_label = "Remove Shortlist" if is_shortlisted else "Add to Shortlist"
        if st.button(sl_label, key=f"card_sl_{cid}", use_container_width=True):
            if is_shortlisted:
                st.session_state.shortlist.remove(cid)
            else:
                st.session_state.shortlist.add(cid)
            st.rerun()

if "app_state" not in st.session_state:
    st.session_state.app_state = "INGESTION"
if "dashboard_tab" not in st.session_state:
    st.session_state.dashboard_tab = 0
if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = "None"
if "candidate_count" not in st.session_state:
    st.session_state.candidate_count = 0
if "file_size_bytes" not in st.session_state:
    st.session_state.file_size_bytes = 0
if "uploaded_bytes" not in st.session_state:
    st.session_state.uploaded_bytes = None
if "df" not in st.session_state:
    st.session_state.df = None
if "pipeline_time" not in st.session_state:
    st.session_state.pipeline_time = 0.0
if "pipeline_memory" not in st.session_state:
    st.session_state.pipeline_memory = 0.0
if "selected_candidate_id" not in st.session_state:
    st.session_state.selected_candidate_id = ""
if "compare_candidate_id" not in st.session_state:
    st.session_state.compare_candidate_id = ""
if "shortlist" not in st.session_state:
    st.session_state.shortlist = set()
if "schema_valid" not in st.session_state:
    st.session_state.schema_valid = False
if "pipeline_done" not in st.session_state:
    st.session_state.pipeline_done = False
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = ""

# ==================== INGESTION PORTAL ====================
if st.session_state.app_state == "INGESTION":
    render_workflow_tracker("INGESTION")

    col_logo, col_main = st.columns([1, 3])
    with col_logo:
        st.markdown("""
        <div style="padding:12px 0;">
            <div style="font-family:'Orbitron',sans-serif; font-weight:900; font-size:2em; letter-spacing:4px; color:#fff;">APTIV</div>
            <div style="font-family:'Inter',sans-serif; font-weight:500; font-size:0.55em; letter-spacing:2px; color:#888; margin-top:1px; text-transform:uppercase;">Operating System</div>
        </div>
        """, unsafe_allow_html=True)
    with col_main:
        st.markdown("""
        <div style="padding:12px 0;">
            <div style="font-family:'Orbitron',sans-serif; font-weight:700; font-size:0.85em; letter-spacing:2px; color:#888;">Candidate Ingestion Portal</div>
            <div style="font-family:'Inter',sans-serif; font-weight:400; font-size:0.8em; color:#666; margin-top:2px;">Upload &rarr; Validate &rarr; Ingest &rarr; Analyze</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_upload, col_summary = st.columns([3, 2], gap="large")

    raw_df = None
    preview_df = pd.DataFrame()
    schema_status = "Awaiting upload"
    detected_fields = []

    with col_upload:
        st.markdown('<div class="section-header">Upload Dataset</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload Candidate Dataset",
            type=["json", "jsonl", "csv"],
            key="file_uploader",
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            st.session_state.uploaded_bytes = bytes_data
            st.session_state.uploaded_filename = uploaded_file.name
            st.session_state.dataset_name = uploaded_file.name
            st.session_state.file_size_bytes = len(bytes_data)
            try:
                if uploaded_file.name.endswith(".csv"):
                    raw_df = pd.read_csv(io.BytesIO(bytes_data))
                    st.session_state.candidate_count = len(raw_df)
                    preview_df = raw_df.head(5)
                elif uploaded_file.name.endswith(".jsonl"):
                    st.session_state.candidate_count = count_lines_jsonl(bytes_data)
                    preview_lines = bytes_data.decode("utf-8").splitlines()[:5]
                    records = [json.loads(l) for l in preview_lines if l.strip()]
                    preview_df = pd.DataFrame(records)
                    all_lines = bytes_data.decode("utf-8").splitlines()
                    all_records = [json.loads(l) for l in all_lines if l.strip()]
                    raw_df = pd.DataFrame(all_records)
                else:
                    raw = json.loads(bytes_data.decode("utf-8"))
                    if isinstance(raw, list):
                        st.session_state.candidate_count = len(raw)
                        preview_df = pd.DataFrame(raw[:5])
                        raw_df = pd.DataFrame(raw)
                    else:
                        st.session_state.candidate_count = 1
                        preview_df = pd.DataFrame([raw])
                        raw_df = pd.DataFrame([raw])
                st.session_state.schema_valid = True
                schema_status = "Validated"
                detected_fields = list(raw_df.columns) if raw_df is not None else []
            except Exception as e:
                st.session_state.candidate_count = 0
                st.session_state.schema_valid = False
                schema_status = f"Failed: {str(e)[:45]}"

        if st.session_state.uploaded_bytes is not None:
            file_size = st.session_state.file_size_bytes
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size/1024:.2f} KB"
            else:
                size_str = f"{file_size/(1024*1024):.2f} MB"
            val_color = "#ffffff" if st.session_state.schema_valid else "#ff4444"

            st.markdown(f"""
            <div style="display:grid; grid-template-columns:repeat(2,1fr); gap:10px; margin-top:14px;">
                <div class="insight-card" style="padding:12px;">
                    <div class="insight-label">File</div>
                    <div class="insight-value" style="font-size:0.8em;">{st.session_state.dataset_name}</div>
                </div>
                <div class="insight-card" style="padding:12px;">
                    <div class="insight-label">Size</div>
                    <div class="insight-value">{size_str}</div>
                </div>
                <div class="insight-card" style="padding:12px;">
                    <div class="insight-label">Candidates</div>
                    <div class="insight-value">{st.session_state.candidate_count:,}</div>
                </div>
                <div class="insight-card" style="padding:12px;">
                    <div class="insight-label">Schema</div>
                    <div class="insight-value" style="color:{val_color};">{schema_status}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if detected_fields:
                field_chips = "".join([f'<span class="skill-chip">{f}</span>' for f in detected_fields[:12]])
                st.markdown(f"""
                <div class="insight-card" style="padding:12px; margin-top:8px;">
                    <div class="insight-label" style="margin-bottom:4px;">Schema Fields ({len(detected_fields)})</div>
                    <div>{field_chips}</div>
                </div>
                """, unsafe_allow_html=True)

    with col_summary:
        st.markdown('<div class="section-header">Dataset Summary</div>', unsafe_allow_html=True)
        if raw_df is not None and not raw_df.empty:
            yoe_list = []
            if 'years_of_experience' in raw_df.columns:
                yoe_list = raw_df['years_of_experience'].dropna().tolist()
            elif 'profile' in raw_df.columns:
                for p in raw_df['profile']:
                    if isinstance(p, dict):
                        yoe_list.append(p.get('years_of_experience', 0))
                    elif isinstance(p, str):
                        try:
                            yoe_list.append(json.loads(p).get('years_of_experience', 0))
                        except:
                            pass
            avg_yoe = sum(yoe_list)/len(yoe_list) if yoe_list else 0.0
            senior_count = sum(1 for y in yoe_list if y >= 8)
            mid_count = sum(1 for y in yoe_list if 3 <= y < 8)
            junior_count = sum(1 for y in yoe_list if y < 3)
            tot_yoe = len(yoe_list) or 1
            senior_pct = (senior_count/tot_yoe)*100
            mid_pct = (mid_count/tot_yoe)*100
            junior_pct = (junior_count/tot_yoe)*100

            loc_list = []
            if 'location' in raw_df.columns:
                loc_list = raw_df['location'].dropna().tolist()
            elif 'profile' in raw_df.columns:
                for p in raw_df['profile']:
                    if isinstance(p, dict):
                        loc_list.append(p.get('location', ''))
                    elif isinstance(p, str):
                        try:
                            loc_list.append(json.loads(p).get('location', ''))
                        except:
                            pass
            loc_series = pd.Series([l for l in loc_list if l])
            top_locs = loc_series.value_counts().head(3)
            tot_locs = len(loc_series) or 1
            locs_html = ""
            for loc_name, count in top_locs.items():
                loc_pct = (count/tot_locs)*100
                locs_html += f'<div style="margin-bottom:4px;"><div style="display:flex; justify-content:space-between;"><span class="mono-value" style="font-size:0.75em;">{loc_name.upper()}</span><span class="mono-value" style="font-size:0.7em; color:#999;">{count} ({loc_pct:.0f}%)</span></div><div class="score-track" style="height:4px; margin-top:2px;"><div class="score-fill" style="width:{loc_pct}%; height:4px;"></div></div></div>'
            if not locs_html:
                locs_html = '<div style="font-family:Inter,sans-serif; font-size:0.8em; color:#666;">No location data.</div>'

            st.markdown(f"""<div class="glass-panel" style="padding:20px;">
            <div class="mono-label" style="margin-bottom:12px; letter-spacing:1px;">Pool Overview</div>
            <div style="margin-bottom:14px;">
                <div style="font-family:Inter,sans-serif; font-weight:600; font-size:0.8em; color:#aaa; margin-bottom:6px;">Experience (avg {avg_yoe:.1f} yrs)</div>
                <div style="display:flex; justify-content:space-between; font-size:0.72em; font-family:JetBrains Mono,monospace; color:#888;">
                    <span>Senior (8+)</span><span>{senior_count} ({senior_pct:.0f}%)</span>
                </div>
                <div class="score-track" style="height:4px; margin-top:2px;"><div class="score-fill" style="width:{senior_pct}%; height:4px;"></div></div>
                <div style="display:flex; justify-content:space-between; font-size:0.72em; font-family:JetBrains Mono,monospace; color:#888; margin-top:3px;">
                    <span>Mid (3-8)</span><span>{mid_count} ({mid_pct:.0f}%)</span>
                </div>
                <div class="score-track" style="height:4px; margin-top:2px;"><div class="score-fill" style="width:{mid_pct}%; height:4px;"></div></div>
                <div style="display:flex; justify-content:space-between; font-size:0.72em; font-family:JetBrains Mono,monospace; color:#888; margin-top:3px;">
                    <span>Junior (<3)</span><span>{junior_count} ({junior_pct:.0f}%)</span>
                </div>
                <div class="score-track" style="height:4px; margin-top:2px;"><div class="score-fill" style="width:{junior_pct}%; height:4px;"></div></div>
            </div>
            <div>
                <div style="font-family:Inter,sans-serif; font-weight:600; font-size:0.8em; color:#aaa; margin-bottom:6px;">Top Locations</div>
                {locs_html}
            </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="glass-panel" style="padding:24px; text-align:center;">
                <div class="mono-label" style="margin-bottom:6px;">Awaiting Data</div>
                <div style="font-family:Inter,sans-serif; font-size:0.8em; color:#666;">Upload a dataset above to view summary analytics.</div>
            </div>
            """, unsafe_allow_html=True)

    if st.session_state.uploaded_bytes is not None:
        if not preview_df.empty:
            st.markdown('<div class="section-header" style="margin-top:16px;">Preview (First 5 Records)</div>', unsafe_allow_html=True)
            display_preview = preview_df.copy()
            if 'profile' in display_preview.columns:
                for col in ["years_of_experience", "location", "current_title", "current_company"]:
                    display_preview[col] = display_preview['profile'].apply(lambda x: x.get(col, '') if isinstance(x, dict) else '')
            preview_cols = [c for c in ["candidate_id", "current_title", "current_company", "location", "years_of_experience"] if c in display_preview.columns]
            if preview_cols:
                st.dataframe(display_preview[preview_cols].head(5), use_container_width=True, hide_index=True)
        if st.session_state.candidate_count > 0 and st.session_state.schema_valid:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Run Aptiv Intelligence Engine", type="primary", use_container_width=True):
                st.session_state.app_state = "EXECUTING"
                st.rerun()

# ==================== EXECUTION CENTER ====================
elif st.session_state.app_state == "EXECUTING":
    render_workflow_tracker("EXECUTING")

    st.markdown("""
    <div style="text-align:center; padding:16px 0;">
        <div style="font-family:'Orbitron',sans-serif; font-weight:700; font-size:1em; letter-spacing:2px; color:#fff;">Intelligence Engine Execution</div>
        <div style="font-family:'Inter',sans-serif; font-weight:400; font-size:0.8em; color:#666; margin-top:3px;">Processing candidate datastream</div>
    </div>
    """, unsafe_allow_html=True)

    stages = [
        ("Candidate Parsing", "parse"),
        ("Feature Extraction", "features"),
        ("Skill Match Analysis", "skills"),
        ("Production Experience Analysis", "experience"),
        ("Retrieval Intelligence Analysis", "retrieval"),
        ("Behavioral Signal Analysis", "behavioral"),
        ("Startup Fit Analysis", "startup"),
        ("Risk Analysis", "risk"),
        ("Hidden Gem Detection", "gems"),
        ("Recruiter Action Prioritization", "rap"),
        ("Narrative Intelligence Generation", "narrative"),
        ("Ranking Finalization", "ranking")
    ]

    progress_bar = st.progress(0, text="Initializing engine...")
    col_pipeline, col_stats = st.columns([3, 2], gap="large")
    pipeline_container = col_pipeline.empty()
    stats_container = col_stats.empty()

    start_time = time.perf_counter()
    workspace_dir = Path(__file__).parent
    temp_jsonl_path = workspace_dir / "data" / "temp_sandbox_candidates.jsonl"

    if st.session_state.uploaded_bytes is not None:
        fname = st.session_state.uploaded_filename or ""
        if fname.endswith(".csv"):
            pass
        elif fname.endswith(".jsonl"):
            temp_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_jsonl_path, "wb") as f:
                f.write(st.session_state.uploaded_bytes)
        else:
            temp_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                raw = json.loads(st.session_state.uploaded_bytes.decode("utf-8"))
                candidates = raw if isinstance(raw, list) else [raw]
                with open(temp_jsonl_path, "w", encoding="utf-8") as f:
                    for c in candidates:
                        f.write(json.dumps(c) + "\n")
            except Exception as e:
                with open(temp_jsonl_path, "wb") as f:
                    f.write(st.session_state.uploaded_bytes)
    else:
        jsonl_path = workspace_dir / "data" / "candidates.jsonl"
        if not jsonl_path.exists():
            jsonl_path = workspace_dir / "data" / "sample_candidates.json"
        candidates = []
        if jsonl_path.suffix.lower() == ".jsonl":
            with open(jsonl_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i >= 100: break
                    ls = line.strip()
                    if ls: candidates.append(json.loads(ls))
        else:
            with open(jsonl_path, "r", encoding="utf-8") as f:
                fl = json.load(f)
                candidates = fl[:100]
        temp_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_jsonl_path, "w", encoding="utf-8") as f:
            for c in candidates:
                f.write(json.dumps(c) + "\n")

    from candidate_parser import parse_jsonl
    from scorer import CandidateScorer
    from hidden_gem_detector import detect_hidden_gems
    from rap_engine import compute_rap
    from narrative_generator import generate_candidate_narratives

    statuses = ["PENDING"] * len(stages)
    df = None

    for idx in range(len(stages)):
        statuses[idx] = "ACTIVE"
        stage_label, stage_key = stages[idx]

        with pipeline_container.container():
            st.markdown('<div class="section-header">Execution Pipeline</div>', unsafe_allow_html=True)
            for s_idx, (s_label, _) in enumerate(stages):
                cls = "pipeline-step"
                if statuses[s_idx] == "DONE":
                    cls += " done"
                    icon = "●"
                elif statuses[s_idx] == "ACTIVE":
                    cls += " active"
                    icon = "▸"
                else:
                    icon = "○"
                st.markdown(f'<div class="{cls}">{icon} {s_label}</div>', unsafe_allow_html=True)

        elapsed = time.perf_counter() - start_time
        mem_est = 0.0
        cand_processed = 0
        if df is not None:
            mem_est = df.memory_usage(deep=True).sum() / (1024*1024)
            cand_processed = len(df)

        with stats_container.container():
            st.markdown('<div class="section-header">Engine Telemetry</div>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="insight-card" style="padding:12px;"><div class="insight-label">Progress</div><div class="insight-value">{int((idx+1)/len(stages)*100)}%</div></div>
                <div class="insight-card" style="padding:12px;"><div class="insight-label">Runtime</div><div class="insight-value">{elapsed:.3f}s</div></div>
                <div class="insight-card" style="padding:12px;"><div class="insight-label">Memory</div><div class="insight-value">{mem_est:.2f} MB</div></div>
                <div class="insight-card" style="padding:12px;"><div class="insight-label">Candidates Processed</div><div class="insight-value">{cand_processed}</div></div>
            """, unsafe_allow_html=True)

        progress_bar.progress((idx + 1) / len(stages), text=f"{stage_label}...")
        s = time.perf_counter()

        if stage_key == "parse":
            if st.session_state.uploaded_bytes is not None and (st.session_state.uploaded_filename or "").endswith(".csv"):
                df = pd.read_csv(io.BytesIO(st.session_state.uploaded_bytes))
                df = df.head(100)
            else:
                df = parse_jsonl(str(temp_jsonl_path))
        elif stage_key == "features":
            time.sleep(0.03)
        elif stage_key == "skills":
            scorer = CandidateScorer()
            df['score_skill_match'] = scorer.compute_skill_match_score(df)
        elif stage_key == "experience":
            df['score_production_experience'] = scorer.compute_production_experience_score(df)
        elif stage_key == "retrieval":
            df['score_retrieval_ranking'] = scorer.compute_retrieval_ranking_experience_score(df)
        elif stage_key == "behavioral":
            df['score_behavioral'] = scorer.compute_behavioral_score(df)
        elif stage_key == "startup":
            df['score_startup_fit'] = scorer.compute_startup_fit_score(df)
        elif stage_key == "risk":
            df['penalty_risk'] = scorer.compute_risk_penalty(df)
            raw_rel = (
                scorer.weights['skill_match'] * df['score_skill_match'] +
                scorer.weights['production_experience'] * df['score_production_experience'] +
                scorer.weights['retrieval_ranking'] * df['score_retrieval_ranking'] +
                scorer.weights['behavioral'] * df['score_behavioral'] +
                scorer.weights['startup_fit'] * df['score_startup_fit']
            )
            df['final_score'] = (raw_rel - df['penalty_risk']).clip(0.0, 1.0)
            df["score"] = df["final_score"]
        elif stage_key == "gems":
            df = detect_hidden_gems(df)
        elif stage_key == "rap":
            df = compute_rap(df)
        elif stage_key == "narrative":
            df = df.sort_values(["final_score", "candidate_id"], ascending=[False, True]).reset_index(drop=True)
            df["rank"] = range(1, len(df) + 1)
            df = generate_candidate_narratives(df)
        elif stage_key == "ranking":
            df = df.sort_values(["final_score", "candidate_id"], ascending=[False, True]).reset_index(drop=True)
            df["rank"] = range(1, len(df) + 1)

        statuses[idx] = "DONE"

    total_time = time.perf_counter() - start_time
    mem_mb = df.memory_usage(deep=True).sum() / (1024*1024)
    st.session_state.df = df
    st.session_state.pipeline_time = total_time
    st.session_state.pipeline_memory = mem_mb
    st.session_state.pipeline_done = True

    if temp_jsonl_path.exists():
        temp_jsonl_path.unlink()

    with pipeline_container.container():
        st.markdown('<div class="section-header">Execution Pipeline</div>', unsafe_allow_html=True)
        for s_idx, (s_label, _) in enumerate(stages):
            st.markdown(f'<div class="pipeline-step done">● {s_label}</div>', unsafe_allow_html=True)

    with stats_container.container():
        st.markdown('<div class="section-header">Engine Telemetry</div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="insight-card" style="padding:12px;"><div class="insight-label">Progress</div><div class="insight-value">100%</div></div>
            <div class="insight-card" style="padding:12px;"><div class="insight-label">Runtime</div><div class="insight-value">{total_time:.3f}s</div></div>
            <div class="insight-card" style="padding:12px;"><div class="insight-label">Memory</div><div class="insight-value">{mem_mb:.2f} MB</div></div>
            <div class="insight-card" style="padding:12px;"><div class="insight-label">Candidates Processed</div><div class="insight-value">{len(df)}</div></div>
        """, unsafe_allow_html=True)

    progress_bar.progress(1.0, text="Pipeline complete")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; padding:8px 0; border-top:1px solid rgba(255,255,255,0.04);">
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.7em; color:#555; letter-spacing:0.5px;">
            Pipeline compliance secured. All stages completed.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Access Talent Dashboard", type="primary", use_container_width=True):
        st.session_state.app_state = "DASHBOARD"
        st.session_state.selected_candidate_id = df.iloc[0]["candidate_id"]
        st.session_state.dashboard_tab = 0
        st.rerun()

# ==================== DASHBOARD ====================
elif st.session_state.app_state == "DASHBOARD":
    df = st.session_state.df
    if df is None:
        st.warning("No data loaded.")
        if st.button("Go to Ingestion"):
            st.session_state.app_state = "INGESTION"
            st.rerun()
        st.stop()

    render_recruiter_sidebar(df)
    render_workflow_tracker("LEADERBOARD")

    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
    gems_found = int(df["is_hidden_gem"].sum()) if "is_hidden_gem" in df.columns else 0
    kpi_col1.metric("Candidates", f"{len(df)}")
    kpi_col2.metric("Runtime", f"{st.session_state.pipeline_time:.3f}s")
    kpi_col3.metric("Memory", f"{st.session_state.pipeline_memory:.2f} MB")
    kpi_col4.metric("Hidden Gems", f"{gems_found}")
    kpi_col5.metric("Shortlist", f"{len(st.session_state.shortlist)}")
    kpi_col6.metric("Status", "Operational")

    st.markdown("<br>", unsafe_allow_html=True)

    active_tab = st.session_state.dashboard_tab

    pool_stats = {
        'score_skill_match': df['score_skill_match'].mean() if 'score_skill_match' in df.columns else 0.0,
        'score_production_experience': df['score_production_experience'].mean() if 'score_production_experience' in df.columns else 0.0,
        'score_retrieval_ranking': df['score_retrieval_ranking'].mean() if 'score_retrieval_ranking' in df.columns else 0.0,
        'score_behavioral': df['score_behavioral'].mean() if 'score_behavioral' in df.columns else 0.0,
        'score_startup_fit': df['score_startup_fit'].mean() if 'score_startup_fit' in df.columns else 0.0,
    }

    if active_tab == 0:
        # ==================== LEADERBOARD ====================
        st.markdown('<div class="section-header">Talent Leaderboard</div>', unsafe_allow_html=True)

        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            search_q = st.text_input("", placeholder="Search by ID, title, company, or skills...", key="lead_search", label_visibility="collapsed")
        with col_s2:
            view_mode = st.selectbox("", ["All Candidates", "Hidden Gems Only", "RAP Priority"], key="lead_view", label_visibility="collapsed")

        filtered = df.copy()
        if search_q:
            q = search_q.lower()
            mask = (
                filtered["candidate_id"].str.lower().str.contains(q) |
                filtered["current_title"].str.lower().str.contains(q) |
                filtered["current_company"].str.lower().str.contains(q) |
                filtered["skills_listed"].str.lower().str.contains(q)
            )
            filtered = filtered[mask]
        if view_mode == "Hidden Gems Only" and "is_hidden_gem" in filtered.columns:
            filtered = filtered[filtered["is_hidden_gem"] == True]
        if view_mode == "RAP Priority" and "rap_priority" in filtered.columns:
            filtered = filtered[filtered["rap_priority"].isin(["Contact Immediately", "Priority Outreach", "Standard Outreach", "Long-Term Nurture", "Do Not Prioritize"])]

        st.markdown(f'<div style="font-family:Inter,sans-serif; font-size:0.8em; color:#888; margin-bottom:10px;">{len(filtered)} candidates</div>', unsafe_allow_html=True)

        if filtered.empty:
            st.info("No candidates match current filters.")
        else:
            card_cols = st.columns(2)
            for i, (_, row) in enumerate(filtered.iterrows()):
                with card_cols[i % 2]:
                    cid = row["candidate_id"]
                    selected = (cid == st.session_state.selected_candidate_id)
                    is_sl = cid in st.session_state.shortlist
                    render_candidate_card(row, selected, is_sl)

    elif active_tab == 1:
        # ==================== CANDIDATE INTELLIGENCE ====================
        st.markdown('<div class="section-header">Candidate Intelligence Panel</div>', unsafe_allow_html=True)

        active_id = st.session_state.selected_candidate_id
        if not active_id or active_id not in df["candidate_id"].values:
            active_id = df.iloc[0]["candidate_id"]
            st.session_state.selected_candidate_id = active_id
        cand = df[df["candidate_id"] == active_id].iloc[0]

        sel_id = st.selectbox(
            "Select Candidate",
            options=df["candidate_id"].tolist(),
            index=df["candidate_id"].tolist().index(active_id),
            key="intel_selector",
            label_visibility="collapsed"
        )
        if sel_id != active_id:
            st.session_state.selected_candidate_id = sel_id
            st.rerun()

        col_left, col_right = st.columns([1, 1], gap="large")

        with col_left:
            st.markdown('<div class="section-header">Identity</div>', unsafe_allow_html=True)
            with st.container():
                st.markdown(render_mono_row("Candidate ID", cand["candidate_id"]), unsafe_allow_html=True)
                st.markdown(render_mono_row("Rank", f"#{cand['rank']:03d}"), unsafe_allow_html=True)
                st.markdown(render_mono_row("Final Score", f"{cand['score']:.4f} / 1.0000"), unsafe_allow_html=True)
                st.markdown(render_mono_row("Tier", cand.get("display_tier", "N/A")), unsafe_allow_html=True)
                st.markdown(render_mono_row("Archetype", cand.get("archetype", "N/A")), unsafe_allow_html=True)
                st.markdown(render_mono_row("Location", f"{cand.get('location', 'N/A')}"), unsafe_allow_html=True)
                st.markdown(render_mono_row("Experience", f"{cand.get('years_of_experience', 0):.1f} yrs"), unsafe_allow_html=True)

            st.markdown('<div class="section-header" style="margin-top:16px;">Experience</div>', unsafe_allow_html=True)
            with st.container():
                st.markdown(render_mono_row("Current Title", cand.get("current_title", "N/A")), unsafe_allow_html=True)
                st.markdown(render_mono_row("Current Company", cand.get("current_company", "N/A")), unsafe_allow_html=True)

            if cand.get("is_hidden_gem", False):
                st.markdown('<div class="section-header" style="margin-top:16px;">Hidden Gem Analysis</div>', unsafe_allow_html=True)
                with st.container():
                    st.markdown(f'<span class="badge highlight">Hidden Gem</span>', unsafe_allow_html=True)
                    st.markdown(render_mono_row("Gem Score", f"{cand.get('hidden_gem_score', 0):.1f}"), unsafe_allow_html=True)
                    st.markdown(render_mono_row("Category", str(cand.get("hidden_gem_category", "")).upper()), unsafe_allow_html=True)
                    st.markdown(f'<div style="font-family:Inter,sans-serif; font-size:0.85em; color:#ccc; margin-top:6px; padding:10px; border-left:1px solid rgba(255,255,255,0.1);">{cand.get("hidden_gem_narrative", "")}</div>', unsafe_allow_html=True)

            if "rap_priority" in cand:
                st.markdown('<div class="section-header" style="margin-top:16px;">RAP Analysis</div>', unsafe_allow_html=True)
                with st.container():
                    prio = cand.get("rap_priority", "")
                    st.markdown(f'<span class="badge highlight">{prio}</span>', unsafe_allow_html=True)
                    st.markdown(render_mono_row("RAP Score", f"{cand.get('rap_score', 0):.1f} / 100"), unsafe_allow_html=True)
                    st.markdown(f'<div style="font-family:Inter,sans-serif; font-size:0.85em; color:#ccc; margin-top:6px;">{cand.get("rap_action", "")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-family:Inter,sans-serif; font-size:0.8em; color:#888; margin-top:2px;">{cand.get("rap_rationale", "")}</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="section-header">Skills</div>', unsafe_allow_html=True)
            with st.container():
                raw_skills = cand.get("skills_listed", "")
                if isinstance(raw_skills, list):
                    raw_skills = ", ".join(raw_skills)
                skill_items = [s.strip() for s in raw_skills.split(",") if s.strip()] if raw_skills else []
                if skill_items:
                    highlight_kws = ["vector", "pinecone", "weaviate", "qdrant", "milvus", "faiss", "embeddings",
                                     "dense", "ndcg", "mrr", "ranking", "python", "lora", "qlora", "peft", "fine-tune",
                                     "nlp", "information retrieval", "search", "retrieval", "distributed", "kubernetes"]
                    tags = ""
                    for s in skill_items[:15]:
                        is_rel = any(k in s.lower() for k in highlight_kws)
                        cls = "skill-chip relevant" if is_rel else "skill-chip"
                        tags += f'<span class="{cls}" title="{s}">{s}</span>'
                    st.markdown(f'<div>{tags}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="font-family:Inter,sans-serif; font-size:0.85em; color:#666;">No skills listed.</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-header" style="margin-top:16px;">Strengths</div>', unsafe_allow_html=True)
            pos = cand.get("positive_signals", [])
            if isinstance(pos, str):
                pos = [pos]
            if pos:
                html = '<div class="insight-card" style="padding:12px;">'
                for s in pos:
                    html += f'<div style="font-family:Inter,sans-serif; font-size:0.85em; color:#ddd; margin-bottom:4px;">&bull; {s}</div>'
                html += '</div>'
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.markdown('<div class="insight-card" style="padding:12px; color:#666;">No specific strengths recorded.</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-header" style="margin-top:16px;">Risks</div>', unsafe_allow_html=True)
            neg = cand.get("concerns", [])
            if isinstance(neg, str):
                neg = [neg]
            if neg:
                html = '<div class="insight-card" style="padding:12px;">'
                for c in neg:
                    html += f'<div style="font-family:Inter,sans-serif; font-size:0.85em; color:#bbb; margin-bottom:4px;">&bull; {c}</div>'
                html += '</div>'
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.markdown('<div class="insight-card" style="padding:12px; color:#666;">No risks detected.</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-header" style="margin-top:16px;">Score Breakdown</div>', unsafe_allow_html=True)
            with st.container():
                render_score_bar("Skill Match (40%)", cand.get("score_skill_match", 0) * 0.40, 0.40, benchmark=pool_stats['score_skill_match'] * 0.40)
                render_score_bar("Production Exp (25%)", cand.get("score_production_experience", 0) * 0.25, 0.25, benchmark=pool_stats['score_production_experience'] * 0.25)
                render_score_bar("Retrieval Depth (15%)", cand.get("score_retrieval_ranking", 0) * 0.15, 0.15, benchmark=pool_stats['score_retrieval_ranking'] * 0.15)
                render_score_bar("Behavioral (10%)", cand.get("score_behavioral", 0) * 0.10, 0.10, benchmark=pool_stats['score_behavioral'] * 0.10)
                render_score_bar("Startup Fit (10%)", cand.get("score_startup_fit", 0) * 0.10, 0.10, benchmark=pool_stats['score_startup_fit'] * 0.10)
                render_score_bar("Risk Penalty", cand.get("penalty_risk", 0), 1.0, is_penalty=True)

            st.markdown('<div class="section-header" style="margin-top:16px;">Recruiter Recommendation</div>', unsafe_allow_html=True)
            with st.container():
                narrative = cand.get("narrative", "No recommendation.")
                st.markdown(f'<div class="insight-card" style="padding:14px; font-family:Inter,sans-serif; font-size:0.9em; color:#ccc; line-height:1.6;">{narrative}</div>', unsafe_allow_html=True)

    elif active_tab == 2:
        # ==================== EXPLAINABILITY LAB ====================
        st.markdown('<div class="section-header">Explainability Lab &mdash; Compare Candidates</div>', unsafe_allow_html=True)

        cand_a_id = st.session_state.selected_candidate_id
        if not cand_a_id or cand_a_id not in df["candidate_id"].values:
            cand_a_id = df.iloc[0]["candidate_id"]
        cand_a = df[df["candidate_id"] == cand_a_id].iloc[0]

        st.markdown(f'<div style="font-family:Inter,sans-serif; font-size:0.95em; color:#ccc; margin-bottom:14px;">Comparing <strong style="color:#fff;">{cand_a_id}</strong> (Rank #{cand_a["rank"]}) against another candidate</div>', unsafe_allow_html=True)

        pool_b = df[df["candidate_id"] != cand_a_id]
        if pool_b.empty:
            st.warning("No other candidates to compare.")
        else:
            next_rank = cand_a["rank"] + 1
            default_b = pool_b[pool_b["rank"] == next_rank].iloc[0]["candidate_id"] if not pool_b[pool_b["rank"] == next_rank].empty else pool_b.iloc[0]["candidate_id"]
            if "compare_candidate_id" not in st.session_state or st.session_state.compare_candidate_id == cand_a_id or st.session_state.compare_candidate_id not in pool_b["candidate_id"].values:
                st.session_state.compare_candidate_id = default_b
            comp_id = st.selectbox(
                "Compare against:",
                options=pool_b["candidate_id"].tolist(),
                index=pool_b["candidate_id"].tolist().index(st.session_state.compare_candidate_id),
                key="comp_select",
                label_visibility="collapsed"
            )
            st.session_state.compare_candidate_id = comp_id
            cand_b = df[df["candidate_id"] == comp_id].iloc[0]

            components = [
                ("Skill Match (40%)", "score_skill_match", 0.40),
                ("Production Exp (25%)", "score_production_experience", 0.25),
                ("Retrieval Depth (15%)", "score_retrieval_ranking", 0.15),
                ("Behavioral (10%)", "score_behavioral", 0.10),
                ("Startup Fit (10%)", "score_startup_fit", 0.10),
            ]

            col_ex1, col_ex2 = st.columns([1, 1], gap="large")
            with col_ex1:
                st.markdown(f'<div class="section-header">Candidate A &mdash; {cand_a["candidate_id"]} (Score: {cand_a["score"]:.4f})</div>', unsafe_allow_html=True)
                for comp_name, col_name, weight in components:
                    val_a = cand_a.get(col_name, 0.0) * weight
                    render_score_bar(comp_name, val_a, weight, benchmark=pool_stats[col_name] * weight)
                render_score_bar("Risk Penalty", cand_a.get("penalty_risk", 0.0), 1.0, is_penalty=True)
            with col_ex2:
                st.markdown(f'<div class="section-header">Candidate B &mdash; {cand_b["candidate_id"]} (Score: {cand_b["score"]:.4f})</div>', unsafe_allow_html=True)
                for comp_name, col_name, weight in components:
                    val_b = cand_b.get(col_name, 0.0) * weight
                    render_score_bar(comp_name, val_b, weight, benchmark=pool_stats[col_name] * weight)
                render_score_bar("Risk Penalty", cand_b.get("penalty_risk", 0.0), 1.0, is_penalty=True)

            st.markdown('<div class="section-header" style="margin-top:16px;">Ranking Differential</div>', unsafe_allow_html=True)
            diffs = []
            for comp_name, col_name, weight in components:
                va = cand_a.get(col_name, 0.0) * weight
                vb = cand_b.get(col_name, 0.0) * weight
                d = va - vb
                if abs(d) > 0.001:
                    if d > 0:
                        diffs.append(f"A leads in <strong>{comp_name}</strong> by <strong>+{d:.4f}</strong>")
                    else:
                        diffs.append(f"B leads in <strong>{comp_name}</strong> by <strong>+{abs(d):.4f}</strong>")
            pen_diff = cand_b.get("penalty_risk", 0.0) - cand_a.get("penalty_risk", 0.0)
            if abs(pen_diff) > 0.001:
                if pen_diff > 0:
                    diffs.append(f"A has <strong>{pen_diff:.4f}</strong> less risk penalty")
                else:
                    diffs.append(f"B has <strong>{abs(pen_diff):.4f}</strong> less risk penalty")
            delta = cand_a["score"] - cand_b["score"]
            outcome = f"Candidate A outranks B by <strong>+{delta:.4f}</strong>." if delta > 0 else f"Candidate B outranks A by <strong>+{abs(delta):.4f}</strong>."

            html = f'<div class="insight-card" style="padding:14px;">'
            for d in diffs:
                html += f'<div style="font-family:Inter,sans-serif; font-size:0.85em; color:#ddd; margin-bottom:4px;">&bull; {d}</div>'
            html += f'<div style="font-family:Inter,sans-serif; font-size:0.95em; color:#fff; font-weight:600; margin-top:8px;">{outcome}</div></div>'
            st.markdown(html, unsafe_allow_html=True)

    elif active_tab == 3:
        # ==================== HIDDEN GEMS ====================
        st.markdown('<div class="section-header">Hidden Gem Discovery</div>', unsafe_allow_html=True)

        hg_df = df[df["is_hidden_gem"] == True] if "is_hidden_gem" in df.columns else pd.DataFrame()

        col_hg_search, col_hg_count = st.columns([3, 1])
        with col_hg_search:
            hg_search = st.text_input("", placeholder="Search hidden gems...", key="hg_search", label_visibility="collapsed")
        with col_hg_count:
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace; font-size:0.8em; color:#888; text-align:right; padding-top:8px;">{len(hg_df)} gems found</div>', unsafe_allow_html=True)

        hg_filtered = hg_df.copy()
        if hg_search:
            hg_filtered = hg_filtered[hg_filtered["candidate_id"].str.lower().str.contains(hg_search.lower())]

        categories = [
            ("Emerging Specialist", "Strong skill assessment scores but low overall keyword counts. Often missed by keyword-only database lookups."),
            ("Growth Candidate", "Early-to-mid career profiles with high startup suitability and platform engagement marks, but modest absolute tenure."),
            ("Startup Builder", "High startup fit and distributed systems experience, combined with relocation willingness and active code contributions."),
            ("High Intent Candidate", "Highly active and responsive coders ready to interview immediately, with quick notice periods."),
            ("Underexposed Expert", "Very high skill match but low profile views/saves visibility. Missed by recruiter search appearance counts."),
            ("Hidden Gem", "Candidates with high overall potential signals that represent strong off-keyword matches."),
        ]

        for cat_name, why_missed in categories:
            cat_df = hg_filtered[hg_filtered["hidden_gem_category"] == cat_name] if not hg_filtered.empty else pd.DataFrame()
            with st.expander(f"{cat_name} ({len(cat_df)} found)"):
                st.markdown(f'<div style="font-family:Inter,sans-serif; font-size:0.82em; color:#999; margin-bottom:10px; padding:8px; border-left:2px solid rgba(255,255,255,0.15);">{why_missed}</div>', unsafe_allow_html=True)
                if cat_df.empty:
                    st.markdown('<div style="font-family:Inter,sans-serif; font-size:0.85em; color:#666;">No candidates in this category.</div>', unsafe_allow_html=True)
                else:
                    for _, r in cat_df.iterrows():
                        r_cid = r['candidate_id']
                        r_is_sl = r_cid in st.session_state.shortlist
                        star = "★" if r_is_sl else "☆"
                        st.markdown(f"""
                        <div class="card" style="padding:14px; margin-bottom:6px;">
                            <div style="display:flex; justify-content:space-between;">
                                <span class="mono-value" style="font-size:0.85em;">{r_cid}</span>
                                <span class="mono-value" style="font-size:0.85em;">Rank #{r['rank']} | {r['score']:.4f}</span>
                            </div>
                            <div style="margin-top:4px; display:flex; justify-content:space-between; font-family:Inter,sans-serif; font-size:0.8em; color:#999;">
                                <span>Gem Score: <strong>{r.get('hidden_gem_score', 0):.1f}</strong></span>
                                <span style="color:#ffaa00;">{star}</span>
                            </div>
                            <div style="margin-top:6px; font-family:Inter,sans-serif; font-size:0.82em; color:#bbb; padding-left:8px; border-left:1px solid rgba(255,255,255,0.06);">
                                {r.get('hidden_gem_narrative', '')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        col_hg1, col_hg2 = st.columns(2)
                        with col_hg1:
                            if st.button("Select & View", key=f"hg_view_{r_cid}", use_container_width=True):
                                st.session_state.selected_candidate_id = r_cid
                                st.session_state.dashboard_tab = 1
                                st.rerun()
                        with col_hg2:
                            lbl = "Remove Shortlist" if r_is_sl else "Add to Shortlist"
                            if st.button(lbl, key=f"hg_sl_{r_cid}", use_container_width=True):
                                if r_is_sl: st.session_state.shortlist.remove(r_cid)
                                else: st.session_state.shortlist.add(r_cid)
                                st.rerun()

    elif active_tab == 4:
        # ==================== RAP OPERATIONS ====================
        st.markdown('<div class="section-header">RAP Operations Center</div>', unsafe_allow_html=True)

        priorities = [
            ("Contact Immediately", "Candidates with high availability, high responsiveness, and strong qualification profiles. Target within 4 hours."),
            ("Priority Outreach", "Strong candidates with active platform signals and standard notice periods. Target within 24 hours."),
            ("Standard Outreach", "Qualified candidates with moderate engagement signals. Add to weekly message queues."),
            ("Long-Term Nurture", "High quality matches currently constrained by long notice periods or salary boundaries. Keep active in nurture loops."),
            ("Do Not Prioritize", "Candidates with minimal platform response records or data integrity violations."),
        ]

        col_rap_search, col_rap_count = st.columns([3, 1])
        with col_rap_search:
            rap_search = st.text_input("", placeholder="Search by candidate ID...", key="rap_search", label_visibility="collapsed")
        with col_rap_count:
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace; font-size:0.8em; color:#888; text-align:right; padding-top:8px;">{len(df)} in queue</div>', unsafe_allow_html=True)

        for prio_name, directive in priorities:
            prio_df = df[df["rap_priority"] == prio_name] if "rap_priority" in df.columns else pd.DataFrame()
            if rap_search and not prio_df.empty:
                prio_df = prio_df[prio_df["candidate_id"].str.lower().str.contains(rap_search.lower())]

            with st.expander(f"{prio_name} ({len(prio_df)} in queue)"):
                st.markdown(f'<div style="font-family:Inter,sans-serif; font-size:0.82em; color:#999; margin-bottom:10px; padding:8px; border-left:2px solid rgba(255,255,255,0.12);">{directive}</div>', unsafe_allow_html=True)
                if prio_df.empty:
                    st.markdown('<div style="font-family:Inter,sans-serif; font-size:0.85em; color:#666;">No candidates in this queue.</div>', unsafe_allow_html=True)
                else:
                    for _, r in prio_df.iterrows():
                        r_cid = r['candidate_id']
                        r_is_sl = r_cid in st.session_state.shortlist
                        notice = r.get("notice_period_days", 0)
                        resp = r.get("recruiter_response_rate", 0.0)
                        signal = "High response" if resp >= 0.75 else "Medium" if resp >= 0.4 else "Low engagement"
                        star = "★" if r_is_sl else "☆"
                        st.markdown(f"""
                        <div class="card" style="padding:14px; margin-bottom:6px;">
                            <div style="display:flex; justify-content:space-between;">
                                <span class="mono-value" style="font-size:0.85em;">{r_cid}</span>
                                <span class="mono-value" style="font-size:0.85em;">RAP: {r.get('rap_score', 0):.1f} | Score: {r['score']:.4f}</span>
                            </div>
                            <div style="margin-top:4px; display:flex; justify-content:space-between; font-family:Inter,sans-serif; font-size:0.8em; color:#999;">
                                <span>{notice}-day notice</span>
                                <span>{signal}</span>
                                <span style="color:#ffaa00;">{star}</span>
                            </div>
                            <div style="margin-top:4px; font-family:Inter,sans-serif; font-size:0.82em; color:#ccc;">{r.get('rap_action', '')}</div>
                            <div style="font-family:Inter,sans-serif; font-size:0.78em; color:#888;">{r.get('rap_rationale', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        col_rap1, col_rap2 = st.columns(2)
                        with col_rap1:
                            if st.button("Select & View", key=f"rap_view_{r_cid}", use_container_width=True):
                                st.session_state.selected_candidate_id = r_cid
                                st.session_state.dashboard_tab = 1
                                st.rerun()
                        with col_rap2:
                            lbl = "Remove Shortlist" if r_is_sl else "Add to Shortlist"
                            if st.button(lbl, key=f"rap_sl_{r_cid}", use_container_width=True):
                                if r_is_sl: st.session_state.shortlist.remove(r_cid)
                                else: st.session_state.shortlist.add(r_cid)
                                st.rerun()

    elif active_tab == 5:
        # ==================== EXPORT CENTER ====================
        st.markdown('<div class="section-header">Export Center</div>', unsafe_allow_html=True)

        df_top100 = df.head(100).copy()
        is_monotonic = df_top100["score"].is_monotonic_decreasing
        monotonicity_status = "PASS" if is_monotonic else "FAIL"
        tie_break_status = "PASS"
        ties = df_top100[df_top100.duplicated(subset=["score"], keep=False)]
        if not ties.empty:
            for _, group in ties.groupby("score"):
                if not group["candidate_id"].is_monotonic_increasing:
                    tie_break_status = "FAIL"
                    break
        has_reasoning = df_top100["narrative"].notna().all() and (df_top100["narrative"].str.strip() != "").all()
        reasoning_status = "PASS" if has_reasoning else "FAIL"
        overall_valid = (monotonicity_status == "PASS") and (tie_break_status == "PASS") and (reasoning_status == "PASS")
        overall_status = "PASS" if overall_valid else "FAIL"

        col_val, col_export = st.columns([1, 1], gap="large")

        with col_val:
            st.markdown('<div class="section-header">Validation</div>', unsafe_allow_html=True)
            status_color = "#ffffff" if overall_status == "PASS" else "#ff4444"
            st.markdown(f"""
            <div class="insight-card" style="padding:16px; text-align:center;">
                <div class="mono-label" style="margin-bottom:6px;">Overall Compliance</div>
                <div style="font-family:'Orbitron',sans-serif; font-size:1.4em; font-weight:700; color:{status_color};">{overall_status}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(render_mono_row("Pool Size", f"{st.session_state.candidate_count} candidates"), unsafe_allow_html=True)
            st.markdown(render_mono_row("Top-100 Generated", f"{len(df_top100)} / 100"), unsafe_allow_html=True)
            st.markdown(render_mono_row("Monotonicity", monotonicity_status), unsafe_allow_html=True)
            st.markdown(render_mono_row("Tie-break", tie_break_status), unsafe_allow_html=True)
            st.markdown(render_mono_row("Reasoning", reasoning_status), unsafe_allow_html=True)

        with col_export:
            st.markdown('<div class="section-header">Downloads</div>', unsafe_allow_html=True)
            submission_df = df_top100[["candidate_id", "rank", "score", "narrative"]].copy()
            submission_df = submission_df.rename(columns={"score": "score", "narrative": "reasoning"})
            submission_csv = submission_df.to_csv(index=False).encode('utf-8')
            hg_export_df = df[df["is_hidden_gem"] == True].copy() if "is_hidden_gem" in df.columns else pd.DataFrame()
            if not hg_export_df.empty and "candidate_id" in hg_export_df.columns:
                hg_cols = ["candidate_id"] + [c for c in hg_export_df.columns if c != "candidate_id"]
                hg_export_df = hg_export_df[hg_cols]
            gems_csv = hg_export_df.to_csv(index=False).encode('utf-8') if not hg_export_df.empty else b""

            rap_export_df = df.copy() if "rap_priority" in df.columns else pd.DataFrame()
            if not rap_export_df.empty and "candidate_id" in rap_export_df.columns:
                rap_cols = ["candidate_id"] + [c for c in rap_export_df.columns if c != "candidate_id"]
                rap_export_df = rap_export_df[rap_cols]
            rap_csv = rap_export_df.to_csv(index=False).encode('utf-8') if not rap_export_df.empty else b""

            sl_ids = list(st.session_state.shortlist)
            sl_export_df = df[df["candidate_id"].isin(sl_ids)].copy()
            if not sl_export_df.empty and "candidate_id" in sl_export_df.columns:
                sl_cols = ["candidate_id"] + [c for c in sl_export_df.columns if c != "candidate_id"]
                sl_export_df = sl_export_df[sl_cols]
            sl_csv = sl_export_df.to_csv(index=False).encode('utf-8') if not sl_export_df.empty else b""

            st.download_button("Submission.csv (Top 100)", data=submission_csv, file_name="submission.csv", mime="text/csv", use_container_width=True, key="dl_main")
            st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
            st.download_button("Recruiter Shortlist.csv", data=sl_csv, file_name="recruiter_shortlist.csv", mime="text/csv", use_container_width=True, disabled=len(sl_ids)==0, key="dl_sl")
            st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
            st.download_button("Hidden Gems.csv", data=gems_csv, file_name="hidden_gems.csv", mime="text/csv", use_container_width=True, disabled=hg_export_df.empty, key="dl_hg")
            st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
            st.download_button("RAP Priorities.csv", data=rap_csv, file_name="rap_priorities.csv", mime="text/csv", use_container_width=True, disabled=rap_export_df.empty, key="dl_rap")

        with st.expander("Validator Logs", expanded=False):
            st.markdown(f"""
            <div style="font-family:JetBrains Mono,monospace; font-size:0.8em; color:#888; line-height:1.5;">
            [VALIDATOR] Pool: {st.session_state.candidate_count} candidates<br>
            [VALIDATOR] Top-100: {len(df_top100)} candidates<br>
            [VALIDATOR] Monotonicity: {monotonicity_status}<br>
            [VALIDATOR] Tie-break: {tie_break_status}<br>
            [VALIDATOR] Reasoning: {reasoning_status}<br>
            [VALIDATOR] Overall: {overall_status}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_r1, col_r2, col_r3 = st.columns([1, 1, 1])
        with col_r2:
            if st.button("Reset to Ingestion", type="secondary", use_container_width=True, key="reset_to_ingestion"):
                for key in ["app_state", "dataset_name", "candidate_count", "file_size_bytes",
                            "uploaded_bytes", "df", "pipeline_time", "pipeline_memory",
                            "selected_candidate_id", "schema_valid", "pipeline_done", "uploaded_filename", "shortlist", "compare_candidate_id"]:
                    if key in st.session_state:
                        try: del st.session_state[key]
                        except: pass
                st.session_state.shortlist = set()
                st.session_state.app_state = "INGESTION"
                st.rerun()
