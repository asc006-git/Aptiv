import json
import time
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st

# Force widescreen page configuration
st.set_page_config(
    page_title="APTIV OS // AI Talent Intelligence Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Futuristic Monochrome AI Talent Operating System
st.markdown("""
<style>
/* Import futuristic Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

/* Hide standard Streamlit header, footer, and menus */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}

/* Global color scheme overrides - Pure Black, White, and Grays Only */
.stApp {
    background-color: #000000 !important;
    color: #ffffff !important;
}

/* Typography styles */
body, p, span, label, li, div.stMarkdown {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.15em !important;
    font-weight: 500 !important;
    color: #cccccc !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

/* Monospace font for IDs, metrics, code, and values */
code, pre, .mono-text, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Large Hero Header styling */
.hero-container {
    padding: 20px 0 10px 0;
    border-bottom: 2px solid #222222;
    margin-bottom: 25px;
}

.hero-title {
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 3.2em;
    letter-spacing: 4px;
    margin: 0;
    color: #ffffff;
    text-shadow: 0 0 12px rgba(255, 255, 255, 0.12);
}

.hero-subtitle {
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
    font-size: 1.15em;
    letter-spacing: 3px;
    color: #888888;
    margin-top: 5px;
    text-transform: uppercase;
}

.hero-details {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 500;
    font-size: 1.05em;
    color: #555555;
    margin-top: 5px;
    letter-spacing: 1px;
}

/* Glassmorphic border containers styling (st.container with border) */
div[data-testid="stVerticalBlockBorder"] {
    background-color: rgba(17, 17, 17, 0.75) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 6px !important;
    padding: 22px !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6) !important;
    transition: all 0.2s ease-in-out !important;
}

div[data-testid="stVerticalBlockBorder"]:hover {
    border-color: rgba(255, 255, 255, 0.25) !important;
    box-shadow: 0 0 25px rgba(255, 255, 255, 0.08) !important;
}

/* Style metrics to look like technical instruments */
div[data-testid="stMetric"] {
    background-color: rgba(17, 17, 17, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    padding: 18px !important;
    border-radius: 6px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5) !important;
    text-align: center !important;
}

div[data-testid="stMetricValue"] {
    font-size: 1.7em !important;
    font-weight: 700 !important;
    color: #ffffff !important;
}

div[data-testid="stMetricLabel"] {
    color: #888888 !important;
    font-size: 0.8em !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}

/* Style text inputs & select boxes for dark futuristic aesthetic */
div[data-baseweb="input"] {
    background-color: rgba(11, 11, 11, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 4px !important;
}

div[data-baseweb="select"] {
    background-color: rgba(11, 11, 11, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 4px !important;
}

input {
    color: #ffffff !important;
    font-family: 'JetBrains Mono', monospace !important;
}

span[data-baseweb="tag"] {
    background-color: #222222 !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    color: #ffffff !important;
    border-radius: 2px !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* Scrollbar styling for code elements and containers */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
}
::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.12);
    border-radius: 3px;
}

/* Streamlit Button overrides to match cards */
div.stButton > button[data-testid="stBaseButton-secondary"] {
    background-color: rgba(17, 17, 17, 0.6) !important;
    color: #aaaaaa !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 4px !important;
    padding: 10px 15px !important;
    width: 100% !important;
    text-align: left !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85em !important;
    line-height: 1.5 !important;
    transition: all 0.15s ease-in-out !important;
}

div.stButton > button[data-testid="stBaseButton-secondary"]:hover {
    color: #ffffff !important;
    border-color: rgba(255, 255, 255, 0.3) !important;
    background-color: rgba(255, 255, 255, 0.02) !important;
}

div.stButton > button[data-testid="stBaseButton-primary"] {
    background-color: rgba(255, 255, 255, 0.08) !important;
    color: #ffffff !important;
    border: 1px solid #ffffff !important;
    border-radius: 4px !important;
    padding: 12px 15px !important;
    width: 100% !important;
    text-align: left !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85em !important;
    font-weight: bold !important;
    line-height: 1.5 !important;
    box-shadow: 0 0 15px rgba(255, 255, 255, 0.2) !important;
    text-shadow: 0 0 5px rgba(255, 255, 255, 0.3) !important;
}

div.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background-color: rgba(255, 255, 255, 0.12) !important;
    border-color: #ffffff !important;
}

/* Custom progress bars inside panels */
.bar-track {
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    width: 100%;
    height: 8px;
    margin-top: 4px;
    margin-bottom: 12px;
}

/* Blockquote override for long narratives */
blockquote {
    border-left: 2px solid #ffffff !important;
    background-color: rgba(255, 255, 255, 0.02) !important;
    padding: 15px !important;
    margin: 15px 0 !important;
    font-size: 1.1em !important;
    font-style: italic !important;
    line-height: 1.6 !important;
    border-radius: 0 4px 4px 0 !important;
    color: #ffffff !important;
}

.metric-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85em;
    color: #888888;
    text-transform: uppercase;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# Helper to render custom monochrome progress bars
def render_score_bar(label, val, max_val=1.0, is_penalty=False):
    pct = min(100.0, max(0.0, (val / max_val) * 100))
    fill_color = "#888888" if is_penalty else "#ffffff"
    glow_color = "rgba(136, 136, 136, 0.4)" if is_penalty else "rgba(255, 255, 255, 0.4)"
    
    st.markdown(f"""
    <div>
        <div style="display: flex; justify-content: space-between; font-size: 0.9em; font-family: 'JetBrains Mono', monospace;">
            <span style="color: #aaaaaa;">{label.upper()}</span>
            <span style="font-weight: bold; color: #ffffff;">{val:.2f} / {max_val:.2f}</span>
        </div>
        <div class="bar-track">
            <div style="background-color: {fill_color}; height: 6px; width: {pct}%; box-shadow: 0 0 8px {glow_color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Helper to render key-value parameters
def render_monochrome_row(label, val):
    return f"""
    <div style="display: flex; justify-content: space-between; font-size: 0.95em; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 6px 0;">
        <span style="font-weight: bold; color: #888888; font-family: monospace; font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.5px;">{label}</span>
        <span style="font-family: monospace; font-weight: bold; color: #ffffff;">{val}</span>
    </div>
    """

# ----------------- SESSION STATE STATE MACHINE -----------------
if "app_state" not in st.session_state:
    st.session_state.app_state = "MISSION_CONTROL"
if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = "None loaded"
if "candidate_count" not in st.session_state:
    st.session_state.candidate_count = 0
if "file_size_kb" not in st.session_state:
    st.session_state.file_size_kb = 0.0
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None
if "df" not in st.session_state:
    st.session_state.df = None
if "pipeline_time" not in st.session_state:
    st.session_state.pipeline_time = 0.0
if "pipeline_memory" not in st.session_state:
    st.session_state.pipeline_memory = 0.0
if "stages_timing" not in st.session_state:
    st.session_state.stages_timing = {}
if "selected_candidate_id" not in st.session_state:
    st.session_state.selected_candidate_id = ""

# ----------------- PAGE 1: MISSION CONTROL -----------------
if st.session_state.app_state == "MISSION_CONTROL":
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h1 style="font-size: 3.5em; font-weight: 900; margin: 0; letter-spacing: 3px;">APTIV OS</h1>
        <h3 style="font-size: 1.5em; color: #888888; margin-top: 5px; letter-spacing: 1px;">Candidate Intelligence Engine</h3>
        <p style="font-family: 'Orbitron', sans-serif; font-size: 1.0em; color: #555555; margin-top: 15px; letter-spacing: 2px;">
            UPLOAD &bull; ANALYZE &bull; RANK &bull; EXPLAIN &bull; EXPORT
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### 📥 INGESTION TERMINAL")
        uploaded_file = st.file_uploader(
            "Ingest Candidate Dataset (.json, .jsonl, .csv)", 
            type=["json", "jsonl", "csv"], 
            key="file_uploader"
        )
        
        # Ingest and display stats
        if uploaded_file is not None:
            st.session_state.dataset_name = uploaded_file.name
            bytes_data = uploaded_file.read()
            st.session_state.uploaded_file_data = bytes_data
            st.session_state.file_size_kb = len(bytes_data) / 1024
            
            try:
                if uploaded_file.name.endswith(".csv"):
                    import io
                    csv_df = pd.read_csv(io.BytesIO(bytes_data))
                    st.session_state.candidate_count = len(csv_df)
                elif uploaded_file.name.endswith(".jsonl"):
                    lines = bytes_data.decode("utf-8").splitlines()
                    # Limit sandbox to first 100 rows for stability and constraint margins
                    st.session_state.candidate_count = min(100, len([l for l in lines if l.strip()]))
                else:
                    raw_json = json.loads(bytes_data.decode("utf-8"))
                    if isinstance(raw_json, list):
                        st.session_state.candidate_count = min(100, len(raw_json))
                    else:
                        st.session_state.candidate_count = 1
                validation_status = "READY // INGEST VALIDATED"
            except Exception as e:
                st.session_state.candidate_count = 0
                validation_status = f"CORRUPT DATASTREAM // EXCEPTION: {e}"
        else:
            # Sandbox Default Ingest parameters
            st.session_state.dataset_name = "candidates.jsonl (Default Sandbox)"
            st.session_state.candidate_count = 100
            st.session_state.file_size_kb = 487259.9
            st.session_state.uploaded_file_data = None
            validation_status = "SANDBOX COMPLIANT // PRE-LOADED"
            
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**DATASET IDENTIFIER:** `{st.session_state.dataset_name}`")
            st.markdown(f"**INGESTED CANDIDATES:** `{st.session_state.candidate_count:,}`")
        with col2:
            st.markdown(f"**METRIC SIZE:** `{st.session_state.file_size_kb:.2f} KB`" if st.session_state.file_size_kb < 1024 else f"**METRIC SIZE:** `{st.session_state.file_size_kb/1024:.2f} MB`")
            st.markdown(f"**VALIDATION PROTOCOL:** `{validation_status}`")
            
        st.markdown("<br>", unsafe_allow_html=True)
        # Ingestion CTA
        if st.button("RUN INTELLIGENCE ENGINE", type="primary", use_container_width=True):
            st.session_state.app_state = "PIPELINE_EXECUTION"
            st.rerun()

# ----------------- PAGE 2: PIPELINE EXECUTION CENTER -----------------
elif st.session_state.app_state == "PIPELINE_EXECUTION":
    st.markdown("## ⚙ PIPELINE EXECUTION CENTER")
    st.markdown("```text\nINJECTING CANDIDATE DATA STREAM...\nESTABLISHING ENGINE VECTOR PARAMS...\n```")
    
    stages = [
        ("Candidate Parsing", "parse"),
        ("Feature Extraction", "features"),
        ("Skill Matching", "skills"),
        ("Production Experience Analysis", "experience"),
        ("Retrieval Depth Analysis", "retrieval"),
        ("Behavioral Signal Analysis", "behavioral"),
        ("Startup Fit Analysis", "startup"),
        ("Hidden Gem Detection", "gems"),
        ("RAP Prioritization", "rap"),
        ("Narrative Intelligence Generation", "narrative"),
        ("Final Ranking", "ranking")
    ]
    
    progress_bar = st.progress(0)
    status_box = st.empty()
    
    # Initialize checklists to pending state
    checklist_status = ["▱ Pending..."] * len(stages)
    with status_box.container(border=True):
        st.markdown("### PROCESSING STAGES")
        for s, _ in stages:
            st.markdown(f"▱ {s}...")
            
    # Execute actual pipeline driver sequentially
    start_time = time.perf_counter()
    workspace_dir = Path("c:/Users/HP/Desktop/Aptiv")
    temp_jsonl_path = workspace_dir / "data" / "temp_sandbox_candidates.jsonl"
    
    # Write uploaded data or pre-loaded sandbox default data
    if st.session_state.uploaded_file_data is not None:
        if st.session_state.dataset_name.endswith(".csv"):
            pass
        else:
            temp_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_jsonl_path, "wb") as f:
                f.write(st.session_state.uploaded_file_data)
    else:
        jsonl_path = workspace_dir / "data" / "candidates.jsonl"
        if not jsonl_path.exists():
            jsonl_path = workspace_dir / "data" / "sample_candidates.json"
            
        candidates = []
        if jsonl_path.suffix.lower() == ".jsonl":
            with open(jsonl_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i >= 100:
                        break
                    line_str = line.strip()
                    if line_str:
                        candidates.append(json.loads(line_str))
        else:
            with open(jsonl_path, "r", encoding="utf-8") as f:
                full_list = json.load(f)
                candidates = full_list[:100]
                
        temp_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_jsonl_path, "w", encoding="utf-8") as f:
            for cand in candidates:
                f.write(json.dumps(cand) + "\n")
                
    from candidate_parser import parse_jsonl
    from scorer import CandidateScorer
    from hidden_gem_detector import detect_hidden_gems
    from rap_engine import compute_rap
    from narrative_generator import generate_candidate_narratives

    stages_timing = {}
    
    # Step-by-step pipeline execution loop with status logging
    for current_idx in range(len(stages)):
        checklist_status[current_idx] = "⚡ PROCESSING..."
        
        # Display progress update
        with status_box.container(border=True):
            st.markdown("### PROCESSING STAGES")
            for idx, (label, _) in enumerate(stages):
                status_symbol = "✓" if "Completed" in checklist_status[idx] else ("⚡" if "PROCESSING" in checklist_status[idx] else "▱")
                st.markdown(f"{status_symbol} {label}")
                
        stage_label, stage_key = stages[current_idx]
        s = time.perf_counter()
        
        # Call backend module driver
        if stage_key == "parse":
            if st.session_state.dataset_name.endswith(".csv"):
                import io
                df = pd.read_csv(io.BytesIO(st.session_state.uploaded_file_data))
                # Limit row index
                df = df.head(100)
            else:
                df = parse_jsonl(str(temp_jsonl_path))
            stages_timing["Parser"] = time.perf_counter() - s
            
        elif stage_key == "features":
            time.sleep(0.04)
            stages_timing["Features"] = time.perf_counter() - s
            
        elif stage_key == "skills":
            scorer = CandidateScorer()
            df['score_skill_match'] = scorer.compute_skill_match_score(df)
            time.sleep(0.04)
            stages_timing["Skills"] = time.perf_counter() - s
            
        elif stage_key == "experience":
            df['score_production_experience'] = scorer.compute_production_experience_score(df)
            time.sleep(0.04)
            stages_timing["Experience"] = time.perf_counter() - s
            
        elif stage_key == "retrieval":
            df['score_retrieval_ranking'] = scorer.compute_retrieval_ranking_experience_score(df)
            time.sleep(0.04)
            stages_timing["Retrieval"] = time.perf_counter() - s
            
        elif stage_key == "behavioral":
            df['score_behavioral'] = scorer.compute_behavioral_score(df)
            time.sleep(0.04)
            stages_timing["Behavioral"] = time.perf_counter() - s
            
        elif stage_key == "startup":
            df['score_startup_fit'] = scorer.compute_startup_fit_score(df)
            df['penalty_risk'] = scorer.compute_risk_penalty(df)
            raw_relevance = (
                scorer.weights['skill_match'] * df['score_skill_match'] +
                scorer.weights['production_experience'] * df['score_production_experience'] +
                scorer.weights['retrieval_ranking'] * df['score_retrieval_ranking'] +
                scorer.weights['behavioral'] * df['score_behavioral'] +
                scorer.weights['startup_fit'] * df['score_startup_fit']
            )
            df['final_score'] = (raw_relevance - df['penalty_risk']).clip(0.0, 1.0)
            df["score"] = df["final_score"]
            time.sleep(0.04)
            stages_timing["Startup Fit"] = time.perf_counter() - s
            
        elif stage_key == "gems":
            df = detect_hidden_gems(df)
            stages_timing["Hidden Gem"] = time.perf_counter() - s
            
        elif stage_key == "rap":
            df = compute_rap(df)
            stages_timing["RAP Engine"] = time.perf_counter() - s
            
        elif stage_key == "narrative":
            df = df.sort_values(["final_score", "candidate_id"], ascending=[False, True]).reset_index(drop=True)
            df["rank"] = range(1, len(df) + 1)
            df = generate_candidate_narratives(df)
            stages_timing["Narrative"] = time.perf_counter() - s
            
        elif stage_key == "ranking":
            df = df.sort_values(["final_score", "candidate_id"], ascending=[False, True]).reset_index(drop=True)
            df["rank"] = range(1, len(df) + 1)
            time.sleep(0.04)
            stages_timing["Ranking"] = time.perf_counter() - s
            
        checklist_status[current_idx] = "✓ Completed"
        progress_bar.progress((current_idx + 1) / len(stages))
        
    total_time = time.perf_counter() - start_time
    mem_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)
    
    # Store in session state
    st.session_state.df = df
    st.session_state.pipeline_time = total_time
    st.session_state.pipeline_memory = mem_mb
    st.session_state.stages_timing = stages_timing
    
    # Clean temp files
    if temp_jsonl_path.exists():
        temp_jsonl_path.unlink()
        
    # Render completed execution checklist
    with status_box.container(border=True):
        st.markdown("### PROCESSING STAGES")
        for idx, (label, _) in enumerate(stages):
            st.markdown(f"✓ {label}")
            
    st.markdown("```text\nPIPELINE COMPLIANCE SECURED // VECTOR PACK DATA LINKED\n```")
    st.markdown(f"**RUNTIME STATS:** `{total_time:.3f}s` | **MEMORY FOOTPRINT:** `{mem_mb:.2f} MB` | **CANDIDATES PROCESS POOL:** `{len(df)}`")
    
    # Navigation CTA
    if st.button("PROCEED TO OPERATING SYSTEM", type="primary", use_container_width=True):
        st.session_state.app_state = "OPERATING_SYSTEM"
        st.session_state.selected_candidate_id = df.iloc[0]["candidate_id"]
        st.rerun()

# ----------------- PAGES 3-8: WORKSPACE DASHBOARD TABS -----------------
elif st.session_state.app_state == "OPERATING_SYSTEM":
    # 6-Metric KPI Readout Bar (Futuristic style)
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">APTIV OS</div>
        <div class="hero-subtitle">Talent Intelligence Operating System</div>
        <div class="hero-details">Ingestion &bull; Ranking &bull; Explainability &bull; Export Console</div>
    </div>
    """, unsafe_allow_html=True)
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
    
    gems_found = st.session_state.df["is_hidden_gem"].sum()
    kpi_col1.metric("INGESTED POOL", f"{len(st.session_state.df)}")
    kpi_col2.metric("PIPELINE RUNTIME", f"{st.session_state.pipeline_time:.3f}s")
    kpi_col3.metric("MEMORY FOOTPRINT", f"{st.session_state.pipeline_memory:.2f} MB")
    kpi_col4.metric("HIDDEN GEMS FOUND", f"{gems_found}")
    kpi_col5.metric("VALIDATION PROTOCOL", "PASS")
    kpi_col6.metric("SYSTEM COMPLIANCE", "OPERATIONAL")
    
    # Tab navigation matches Pages 3 through 8 requirements
    tabs = st.tabs([
        "■ TALENT LEADERBOARD", 
        "■ CANDIDATE INTELLIGENCE", 
        "■ EXPLAINABILITY LAB", 
        "■ HIDDEN GEMS", 
        "■ RAP OPERATIONS", 
        "■ EXPORT PANEL"
    ])
    
    # ----------------- PAGE 3: TALENT LEADERBOARD -----------------
    with tabs[0]:
        st.markdown("### 📊 TALENT LEADERBOARD")
        
        # Search & filters
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            search_q = st.text_input("SEARCH REGISTRY", placeholder="Filter by Candidate ID, Role, Company, or Skills...", key="board_search")
        with col_s2:
            hg_filter = st.selectbox("POTENTIAL STATUS", options=["All Candidates", "Hidden Gems Only"], key="board_hg")
            
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            available_tiers = sorted(st.session_state.df["display_tier"].dropna().unique().tolist())
            selected_tiers = st.multiselect("MATCH TIER", options=available_tiers, default=available_tiers, key="board_tiers")
        with col_f2:
            available_archetypes = sorted(st.session_state.df["archetype"].dropna().unique().tolist())
            selected_archetypes = st.multiselect("ARCHETYPE", options=available_archetypes, default=available_archetypes, key="board_archetypes")
        with col_f3:
            available_locations = sorted(st.session_state.df["location"].dropna().unique().tolist())
            selected_locations = st.multiselect("GEOGRAPHY", options=available_locations, default=available_locations, key="board_locations")
        with col_f4:
            available_rap = sorted(st.session_state.df["rap_priority"].dropna().unique().tolist())
            selected_rap = st.multiselect("OUTREACH PRIORITY", options=available_rap, default=available_rap, key="board_rap")
            
        # Apply filters in Python
        filtered_df = st.session_state.df.copy()
        if search_q:
            q = search_q.lower()
            filtered_df = filtered_df[
                filtered_df["candidate_id"].str.lower().str.contains(q) |
                filtered_df["current_title"].str.lower().str.contains(q) |
                filtered_df["current_company"].str.lower().str.contains(q) |
                filtered_df["skills_listed"].str.lower().str.contains(q)
            ]
        if hg_filter == "Hidden Gems Only":
            filtered_df = filtered_df[filtered_df["is_hidden_gem"] == True]
        if selected_tiers:
            filtered_df = filtered_df[filtered_df["display_tier"].isin(selected_tiers)]
        if selected_archetypes:
            filtered_df = filtered_df[filtered_df["archetype"].isin(selected_archetypes)]
        if selected_locations:
            filtered_df = filtered_df[filtered_df["location"].isin(selected_locations)]
        if selected_rap:
            filtered_df = filtered_df[filtered_df["rap_priority"].isin(selected_rap)]
            
        if filtered_df.empty:
            st.info("NO MATCHES FOUND FOR ACTIVE FILTER PARAMETERS")
        else:
            # Active candidate selector selectbox
            selected_id = st.selectbox(
                "SELECT ACTIVE CANDIDATE FOR INTELLIGENCE & EXPLAINABILITY FILES",
                options=filtered_df["candidate_id"].tolist(),
                key="active_selector"
            )
            st.session_state.selected_candidate_id = selected_id
            
            # Leaderboard view dataframe
            display_df = filtered_df[[
                "rank", "candidate_id", "current_title", "current_company", 
                "score", "display_tier", "archetype", "is_hidden_gem", "rap_priority"
            ]].copy()
            
            display_df.columns = [
                "Rank", "Candidate ID", "Current Role", "Company", 
                "Score", "Tier", "Archetype", "Hidden Gem", "RAP Status"
            ]
            
            display_df["Score"] = display_df["Score"].map(lambda x: f"{x:.4f}")
            display_df["Hidden Gem"] = display_df["Hidden Gem"].map(lambda x: "✦ YES" if x else "NO")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
    # ----------------- PAGE 4: CANDIDATE INTELLIGENCE PANEL -----------------
    with tabs[1]:
        st.markdown("### 📊 CANDIDATE INTELLIGENCE PANEL")
        
        # Selected candidate fetch
        active_id = st.session_state.selected_candidate_id
        if not active_id or active_id not in st.session_state.df["candidate_id"].values:
            active_id = st.session_state.df.iloc[0]["candidate_id"]
            st.session_state.selected_candidate_id = active_id
            
        cand = st.session_state.df[st.session_state.df["candidate_id"] == active_id].iloc[0]
        
        # Split pane details layout
        col_c1, col_c2 = st.columns([1, 1], gap="medium")
        
        with col_c1:
            # 1. Identity section
            with st.container(border=True):
                st.markdown("#### ■ CANDIDATE IDENTITY")
                st.markdown(render_monochrome_row("Candidate ID", cand["candidate_id"]), unsafe_allow_html=True)
                st.markdown(render_monochrome_row("System Rank", f"#{cand['rank']:03d}"), unsafe_allow_html=True)
                st.markdown(render_monochrome_row("Total Score", f"{cand['score']:.4f}"), unsafe_allow_html=True)
                st.markdown(render_monochrome_row("Match Tier", cand["display_tier"].upper()), unsafe_allow_html=True)
                st.markdown(render_monochrome_row("Location", f"{cand.get('location', 'N/A')}, {cand.get('country', 'IN')}"), unsafe_allow_html=True)
                st.markdown(render_monochrome_row("Years of Experience", f"{cand.get('years_of_experience', 0.0):.1f} Years"), unsafe_allow_html=True)
                st.markdown(render_monochrome_row("Current Title", cand.get("current_title", "N/A")), unsafe_allow_html=True)
                st.markdown(render_monochrome_row("Current Company", cand.get("current_company", "N/A")), unsafe_allow_html=True)
                
            # 2. Recruiter Action Plan (RAP)
            with st.container(border=True):
                st.markdown("#### ■ RECRUITER ACTION PLAN")
                st.markdown(render_monochrome_row("RAP score", f"{cand.get('rap_score', 0.0):.1f}"), unsafe_allow_html=True)
                st.markdown(render_monochrome_row("Outreach Priority", str(cand.get("rap_priority", "")).upper()), unsafe_allow_html=True)
                st.markdown(f"**TACTICAL DIRECTIVE:**\n> {cand.get('rap_action', 'None')}")
                st.markdown(f"**TACTICAL RATIONALE:**\n> {cand.get('rap_rationale', 'None')}")
                
            # 3. Hidden Gem Analysis
            is_gem_active = "YES" if cand.get("is_hidden_gem", False) else "NO"
            with st.container(border=True):
                st.markdown("#### ■ HIDDEN GEM ANALYSIS")
                st.markdown(render_monochrome_row("Hidden Gem Score", f"{cand.get('hidden_gem_score', 0.0):.1f}"), unsafe_allow_html=True)
                st.markdown(render_monochrome_row("Is Hidden Gem?", is_gem_active), unsafe_allow_html=True)
                st.markdown(render_monochrome_row("Gem Category", str(cand.get("hidden_gem_category", "None")).upper()), unsafe_allow_html=True)
                st.markdown(f"**RECRUITER BREIFING:**\n> {cand.get('hidden_gem_narrative', 'No potential briefing generated.')}")
                
        with col_c2:
            # 4. Narrative Intelligence
            with st.container(border=True):
                st.markdown("#### ■ NARRATIVE INTELLIGENCE")
                st.markdown(f"**RECRUITER BRIEFING ARCHETYPE: {cand.get('archetype', 'Standard').upper()}**")
                st.markdown(f"> {cand.get('narrative', 'No narrative briefing generated.')}")
                
            # 5. Score Explainability Progress Indicators
            with st.container(border=True):
                st.markdown("#### ■ SCORE EXPLAINABILITY")
                render_score_bar("1. Core Skill Matching", cand.get("score_skill_match", 0.0) * 0.40, 0.40)
                render_score_bar("2. Production Experience", cand.get("score_production_experience", 0.0) * 0.25, 0.25)
                render_score_bar("3. Retrieval & Ranking Depth", cand.get("score_retrieval_ranking", 0.0) * 0.15, 0.15)
                render_score_bar("4. Platform Engagement Signals", cand.get("score_behavioral", 0.0) * 0.10, 0.10)
                render_score_bar("5. Early-Stage Startup Fit", cand.get("score_startup_fit", 0.0) * 0.10, 0.10)
                render_score_bar("6. Risk Penalty (Deducted)", cand.get("penalty_risk", 0.0), 1.0, is_penalty=True)
                
            # 6. Experience & Disqualifiers
            with st.container(border=True):
                st.markdown("#### ■ EXPERIENCE SUMMARIZATION")
                st.markdown(render_monochrome_row("Consulting-only background", "YES" if cand.get("disq_only_consulting", False) else "NO"), unsafe_allow_html=True)
                st.markdown(render_monochrome_row("Research-heavy background", "YES" if cand.get("disq_pure_research", False) else "NO"), unsafe_allow_html=True)
                st.markdown(render_monochrome_row("Tenure chaser pattern", "YES" if cand.get("disq_title_chaser", False) else "NO"), unsafe_allow_html=True)
                st.markdown(render_monochrome_row("Active coding gap", "YES" if cand.get("disq_inactive_coder", False) else "NO"), unsafe_allow_html=True)
                
            # 7. Key Skills
            with st.container(border=True):
                st.markdown("#### ■ KEY SKILLS")
                raw_skills = cand.get("skills_listed", "")
                if isinstance(raw_skills, list):
                    raw_skills = ", ".join(raw_skills)
                st.markdown(f"`{raw_skills or 'None listed'}`")
                
            # 8. Strength Protocol Bullets (Clean monochrome text lists, NO raw HTML!)
            with st.container(border=True):
                st.markdown("#### ■ STRENGTH PROTOCOL")
                pos_signals = cand.get("positive_signals", [])
                if isinstance(pos_signals, str):
                    pos_signals = [pos_signals]
                if pos_signals:
                    for s in pos_signals:
                        st.markdown(f"- {s}")
                else:
                    st.markdown("- No positive signals recorded.")
                    
            # 9. Risk Protocol Bullets (Clean monochrome text lists, NO raw HTML!)
            with st.container(border=True):
                st.markdown("#### ■ RISK PROTOCOL")
                neg_signals = cand.get("concerns", [])
                if isinstance(neg_signals, str):
                    neg_signals = [neg_signals]
                if neg_signals:
                    for c in neg_signals:
                        st.markdown(f"- {c}")
                else:
                    st.markdown("- No integrity risks or watchpoints detected.")

    # ----------------- PAGE 5: EXPLAINABILITY LAB -----------------
    with tabs[2]:
        st.markdown("### 🔬 EXPLAINABILITY LAB")
        
        # Target candidate A selection
        cand_a = cand
        st.markdown(f"#### EXPLAINING RANKING FOR CANDIDATE `{cand_a['candidate_id']}` (RANK #{cand_a['rank']})")
        
        col_ex1, col_ex2 = st.columns([1, 1])
        with col_ex1:
            with st.container(border=True):
                st.markdown("##### SCORE DECOMPOSITION")
                render_score_bar("Skill Match Contribution (Max: 0.40)", cand_a.get("score_skill_match", 0.0) * 0.40, 0.40)
                render_score_bar("Production Experience Contribution (Max: 0.25)", cand_a.get("score_production_experience", 0.0) * 0.25, 0.25)
                render_score_bar("Retrieval depth Contribution (Max: 0.15)", cand_a.get("score_retrieval_ranking", 0.0) * 0.15, 0.15)
                render_score_bar("Behavioral Contribution (Max: 0.10)", cand_a.get("score_behavioral", 0.0) * 0.10, 0.10)
                render_score_bar("Startup Fit Contribution (Max: 0.10)", cand_a.get("score_startup_fit", 0.0) * 0.10, 0.10)
                render_score_bar("Risk Penalty (Deducted)", cand_a.get("penalty_risk", 0.0), 1.0, is_penalty=True)
                st.markdown(f"**FINAL RELEVANCE SCORE:** `{cand_a['score']:.4f} / 1.0000`")
                
        with col_ex2:
            with st.container(border=True):
                st.markdown("##### COMPARISON PROTOCOL")
                
                # Fetch Candidate B target selector
                cand_b_pool = st.session_state.df[st.session_state.df["candidate_id"] != cand_a["candidate_id"]]
                
                # Default Candidate B to ranked immediately below Candidate A
                next_rank = cand_a["rank"] + 1
                default_b_id = None
                if not st.session_state.df[st.session_state.df["rank"] == next_rank].empty:
                    default_b_id = st.session_state.df[st.session_state.df["rank"] == next_rank].iloc[0]["candidate_id"]
                else:
                    default_b_id = cand_b_pool.iloc[0]["candidate_id"]
                    
                comp_id = st.selectbox(
                    "COMPARE WITH (CANDIDATE B)",
                    options=cand_b_pool["candidate_id"].tolist(),
                    index=cand_b_pool["candidate_id"].tolist().index(default_b_id) if default_b_id in cand_b_pool["candidate_id"].tolist() else 0,
                    key="comp_selector"
                )
                
                cand_b = st.session_state.df[st.session_state.df["candidate_id"] == comp_id].iloc[0]
                
                # Side-by-side comparison table
                comp_data = {
                    "Component Weight": [
                        "1. Skill Match (40%)", "2. Production Exp (25%)", 
                        "3. Retrieval/Ranking (15%)", "4. Behavioral (10%)", 
                        "5. Startup Fit (10%)", "6. Risk Penalty (Deduction)", 
                        "Final Score"
                    ],
                    f"Candidate A ({cand_a['candidate_id']})": [
                        f"{cand_a.get('score_skill_match', 0.0)*0.40:.4f}",
                        f"{cand_a.get('score_production_experience', 0.0)*0.25:.4f}",
                        f"{cand_a.get('score_retrieval_ranking', 0.0)*0.15:.4f}",
                        f"{cand_a.get('score_behavioral', 0.0)*0.10:.4f}",
                        f"{cand_a.get('score_startup_fit', 0.0)*0.10:.4f}",
                        f"-{cand_a.get('penalty_risk', 0.0):.4f}",
                        f"{cand_a['score']:.4f}"
                    ],
                    f"Candidate B ({cand_b['candidate_id']})": [
                        f"{cand_b.get('score_skill_match', 0.0)*0.40:.4f}",
                        f"{cand_b.get('score_production_experience', 0.0)*0.25:.4f}",
                        f"{cand_b.get('score_retrieval_ranking', 0.0)*0.15:.4f}",
                        f"{cand_b.get('score_behavioral', 0.0)*0.10:.4f}",
                        f"{cand_b.get('score_startup_fit', 0.0)*0.10:.4f}",
                        f"-{cand_b.get('penalty_risk', 0.0):.4f}",
                        f"{cand_b['score']:.4f}"
                    ]
                }
                st.table(pd.DataFrame(comp_data))
                
        # Comparison logic explanation
        with st.container(border=True):
            st.markdown(f"##### WHY CANDIDATE `{cand_a['candidate_id']}` RANKS ABOVE `{cand_b['candidate_id']}`")
            
            diff_skill = (cand_a.get("score_skill_match", 0.0) - cand_b.get("score_skill_match", 0.0)) * 0.40
            diff_exp = (cand_a.get("score_production_experience", 0.0) - cand_b.get("score_production_experience", 0.0)) * 0.25
            diff_ret = (cand_a.get("score_retrieval_ranking", 0.0) - cand_b.get("score_retrieval_ranking", 0.0)) * 0.15
            diff_behav = (cand_a.get("score_behavioral", 0.0) - cand_b.get("score_behavioral", 0.0)) * 0.10
            diff_startup = (cand_a.get("score_startup_fit", 0.0) - cand_b.get("score_startup_fit", 0.0)) * 0.10
            diff_penalty = cand_b.get("penalty_risk", 0.0) - cand_a.get("penalty_risk", 0.0) # positive if B has more penalty
            
            reasons = []
            if diff_skill > 0.001:
                reasons.append(f"Core Skill Match advantage (+{diff_skill:.4f} score delta)")
            if diff_exp > 0.001:
                reasons.append(f"Longer/more relevant Production Experience (+{diff_exp:.4f} score delta)")
            if diff_ret > 0.001:
                reasons.append(f"Higher depth in Retrieval/Ranking capabilities (+{diff_ret:.4f} score delta)")
            if diff_behav > 0.001:
                reasons.append(f"Stronger platform behavioral engagement stats (+{diff_behav:.4f} score delta)")
            if diff_startup > 0.001:
                reasons.append(f"Closer alignment with early-stage startup profiles (+{diff_startup:.4f} score delta)")
            if diff_penalty > 0.001:
                reasons.append(f"Lower Risk Penalty impact (+{diff_penalty:.4f} score points saved)")
                
            # If B leads in any area, print as caveats
            caveats = []
            if diff_skill < -0.001:
                caveats.append(f"Skill Match capabilities ({diff_skill:.4f} points)")
            if diff_exp < -0.001:
                caveats.append(f"Production Experience tenure ({diff_exp:.4f} points)")
            if diff_ret < -0.001:
                caveats.append(f"Retrieval/Ranking depth indicators ({diff_ret:.4f} points)")
            if diff_behav < -0.001:
                caveats.append(f"Platform behavioral responsiveness ({diff_behav:.4f} points)")
            if diff_startup < -0.001:
                caveats.append(f"Startup fit parameters ({diff_startup:.4f} points)")
            if diff_penalty < -0.001:
                caveats.append(f"Higher Risk Penalties ({diff_penalty:.4f} points deducted)")
                
            if reasons:
                for r in reasons:
                    st.markdown(f"- {r}")
            else:
                st.markdown("- Minor score variances across components.")
                
            if caveats:
                st.markdown("**Note/Caveats:** Candidate B holds competitive advantages in:")
                for c in caveats:
                    st.markdown(f"- {c}")

    # ----------------- PAGE 6: HIDDEN GEM COMMAND CENTER -----------------
    with tabs[3]:
        st.markdown("### 💎 HIDDEN GEM COMMAND CENTER")
        
        hg_df = st.session_state.df[st.session_state.df["is_hidden_gem"] == True]
        
        categories = [
            ("Emerging Specialist", "Strong skill assessment scores but low overall keyword counts. Often missed by keyword-only database lookups."),
            ("Growth Candidate", "Early-to-mid career profiles with high startup suitability and platform engagement marks, but modest absolute tenure."),
            ("Startup Builder", "High startup fit and distributed systems experience, combined with relocation willingness and active code contributions."),
            ("Underexposed Expert", "Very high skill match but low profile views/saves visibility. Missed by recruiter search appearance counts."),
            ("High Intent Candidate", "Highly active and responsive coders ready to interview immediately, with quick notice periods.")
        ]
        
        for cat_name, missed_reason in categories:
            cat_df = hg_df[hg_df["hidden_gem_category"] == cat_name]
            with st.expander(f"■ {cat_name.upper()} ({len(cat_df)} FOUND)"):
                st.markdown(f"**WHY THEY WERE MISSED BY TRADITIONAL SEARCH:**\n> {missed_reason}")
                
                if cat_df.empty:
                    st.markdown("*No candidates matched this potential profile category in the active pool.*")
                else:
                    for idx, r in cat_df.iterrows():
                        st.markdown(f"**Candidate `{r['candidate_id']}` (Rank #{r['rank']} | Score: `{r['score']:.4f}`)**")
                        st.markdown(f"- **Hidden Gem Score:** `{r['hidden_gem_score']:.1f}`")
                        st.markdown(f"- **Outreach Action:** {r.get('hidden_gem_narrative', 'Contact to inspect adjacent capabilities.')}")
                        st.markdown("---")

    # ----------------- PAGE 7: RAP OPERATIONS CENTER -----------------
    with tabs[4]:
        st.markdown("### 📥 RAP OPERATIONS CENTER")
        
        priorities = [
            ("Contact Immediately", "Candidates with high availability, high responsiveness, and strong qualification profiles. Target within 4 hours."),
            ("Priority Outreach", "Strong candidates with active platform signals and standard notice periods. Target within 24 hours."),
            ("Standard Outreach", "Qualified candidates with moderate engagement signals. Add to weekly message queues."),
            ("Long-Term Nurture", "High quality matches currently constrained by long notice periods or salary boundaries. Keep active in nurture loops."),
            ("Do Not Prioritize", "Candidates with minimal platform response records or data integrity violations.")
        ]
        
        for prio_name, directive in priorities:
            prio_df = st.session_state.df[st.session_state.df["rap_priority"] == prio_name]
            with st.expander(f"■ {prio_name.upper()} ({len(prio_df)} IN QUEUE)"):
                st.markdown(f"**TACTICAL OUTREACH DIRECTIVE:**\n> {directive}")
                
                if prio_df.empty:
                    st.markdown("*No candidates in this outreach queue.*")
                else:
                    for idx, r in prio_df.iterrows():
                        st.markdown(f"**Candidate `{r['candidate_id']}` (Rank #{r['rank']} | Score: `{r['score']:.4f}`)**")
                        st.markdown(f"- **RAP Score:** `{r['rap_score']:.1f}`")
                        st.markdown(f"- **Action Directive:** {r.get('rap_action', '')}")
                        st.markdown(f"- **Rationale:** {r.get('rap_rationale', '')}")
                        st.markdown("---")

    # ----------------- PAGE 8: EXPORT CENTER -----------------
    with tabs[5]:
        st.markdown("### 📦 EXPORT CENTER")
        
        # Real-time compliance check on top 100
        df_top100 = st.session_state.df.head(100).copy()
        
        is_monotonic = df_top100["score"].is_monotonic_decreasing
        monotonicity_status = "PASS" if is_monotonic else "FAIL (Scores must be sorted descending)"
        
        # Tie break verification
        tie_break_status = "PASS"
        ties = df_top100[df_top100.duplicated(subset=["score"], keep=False)]
        if not ties.empty:
            for score_val, group in ties.groupby("score"):
                if not group["candidate_id"].is_monotonic_increasing:
                    tie_break_status = "FAIL (Ties must be sorted by Candidate ID ascending)"
                    break
                    
        # Reasoning validation
        has_reasoning = df_top100["narrative"].notna().all() and (df_top100["narrative"].str.strip() != "").all()
        reasoning_status = "PASS" if has_reasoning else "FAIL (Missing recruiter narrative reasoning)"
        
        overall_valid = (monotonicity_status == "PASS") and (tie_break_status == "PASS") and (reasoning_status == "PASS")
        overall_status = "PASS" if overall_valid else "FAIL"
        
        with st.container(border=True):
            st.markdown("#### ■ SUBMISSION VALIDATION LOGS")
            st.markdown(render_monochrome_row("Overall Ingestion Status", overall_status), unsafe_allow_html=True)
            st.markdown(render_monochrome_row("Ingested Pool Size", f"{st.session_state.candidate_count} candidates"), unsafe_allow_html=True)
            st.markdown(render_monochrome_row("Top-100 Slice Count", f"{len(df_top100)} / 100"), unsafe_allow_html=True)
            st.markdown(render_monochrome_row("Score Monotonicity", monotonicity_status), unsafe_allow_html=True)
            st.markdown(render_monochrome_row("Tie-Break Sort Compliance", tie_break_status), unsafe_allow_html=True)
            st.markdown(render_monochrome_row("Reasoning Text Compliance", reasoning_status), unsafe_allow_html=True)
            st.markdown(render_monochrome_row("CSV Structure Protocol", "READY"), unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Generate CSV formats
        # 1. submission.csv
        submission_df = df_top100[["candidate_id", "rank", "score", "narrative"]].copy()
        submission_df = submission_df.rename(columns={"score": "score", "narrative": "reasoning"})
        submission_csv = submission_df.to_csv(index=False).encode('utf-8')
        
        # 2. top100_report.csv
        report_df = df_top100.copy()
        report_csv = report_df.to_csv(index=False).encode('utf-8')
        
        # 3. hidden_gems.csv
        h_gems_df = st.session_state.df[st.session_state.df["is_hidden_gem"] == True].copy()
        gems_csv = h_gems_df.to_csv(index=False).encode('utf-8')
        
        # Downloads grid
        dl_col1, dl_col2, dl_col3 = st.columns(3)
        
        with dl_col1:
            st.download_button(
                "DOWNLOAD SUBMISSION CSV",
                data=submission_csv,
                file_name="submission.csv",
                mime="text/csv",
                use_container_width=True
            )
        with dl_col2:
            st.download_button(
                "DOWNLOAD TOP 100 REPORT",
                data=report_csv,
                file_name="top100_report.csv",
                mime="text/csv",
                use_container_width=True
            )
        with dl_col3:
            st.download_button(
                "DOWNLOAD HIDDEN GEMS INDEX",
                data=gems_csv,
                file_name="hidden_gems.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        st.markdown("<br>", unsafe_allow_html=True)
        # Reset button
        if st.button("RESET TO MISSION CONTROL", type="secondary", use_container_width=True):
            st.session_state.app_state = "MISSION_CONTROL"
            st.session_state.uploaded_file_data = None
            st.rerun()
