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
