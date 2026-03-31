import streamlit as st


def inject_css():
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=Source+Sans+3:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Source Sans 3', sans-serif;
        font-weight: 300;
        color: #1a1a1a;
    }

    .stApp {
        background-color: #f5f2ee;
    }

    .main-header {
        border-top: 3px solid #1a1a1a;
        border-bottom: 1px solid #c8c0b4;
        padding: 2.5rem 0 2rem 0;
        margin-bottom: 2.5rem;
    }
    .main-header h1 {
        font-family: 'Playfair Display', serif;
        font-size: 2.4rem;
        font-weight: 600;
        color: #1a1a1a;
        letter-spacing: -0.5px;
        margin: 0 0 0.4rem 0;
    }
    .main-header p {
        font-size: 1rem;
        color: #6b635a;
        font-weight: 300;
        margin: 0;
    }

    [data-testid="stSidebar"] {
        background-color: #ede9e3;
        border-right: 1px solid #c8c0b4;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stSlider label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #6b635a;
        font-weight: 500;
    }

    h2, h3 {
        font-family: 'Playfair Display', serif !important;
        font-weight: 600 !important;
        color: #1a1a1a !important;
    }

    .stButton > button[kind="primary"] {
        background-color: #1a1a1a !important;
        color: #f5f2ee !important;
        border: none !important;
        border-radius: 0 !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        padding: 0.7rem 1.5rem !important;
        transition: background-color 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #3d3530 !important;
    }

    .stDownloadButton > button {
        background-color: transparent !important;
        color: #1a1a1a !important;
        border: 1px solid #1a1a1a !important;
        border-radius: 0 !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton > button:hover {
        background-color: #1a1a1a !important;
        color: #f5f2ee !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid #c8c0b4;
        gap: 0;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #6b635a;
        padding: 0.6rem 1.2rem;
        border-bottom: 2px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #1a1a1a !important;
        border-bottom: 2px solid #1a1a1a !important;
        background: transparent !important;
    }

    .score-card {
        border-left: 3px solid #1a1a1a;
        padding: 1.2rem 1.5rem;
        background: #ede9e3;
        margin: 1rem 0;
    }

    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: #a09890;
        border: 1px dashed #c8c0b4;
    }
    .empty-state .big-number {
        font-family: 'Playfair Display', serif;
        font-size: 5rem;
        font-weight: 400;
        color: #c8c0b4;
        line-height: 1;
        margin-bottom: 1rem;
    }
    .empty-state p {
        font-size: 0.95rem;
        margin: 0;
    }

    hr {
        border: none;
        border-top: 1px solid #c8c0b4;
        margin: 2rem 0;
    }

    .footer {
        text-align: center;
        color: #a09890;
        font-size: 0.78rem;
        letter-spacing: 0.5px;
        padding: 1.5rem 0;
        border-top: 1px solid #c8c0b4;
        margin-top: 2rem;
    }

    [data-testid="stFileUploader"] {
        border: 1px dashed #c8c0b4 !important;
        border-radius: 0 !important;
        background: #ede9e3 !important;
    }
</style>
""", unsafe_allow_html=True)


def render_header():
    st.markdown("""
<div class="main-header">
    <h1>CourdiCV Lab</h1>
    <h3>Analysez, améliorez et reformulez vos documents professionnels en quelques secondes.</h3>
</div>
""", unsafe_allow_html=True)


def render_empty_state():
    st.markdown("""
<div class="empty-state">
    <div class="big-number">&mdash;</div>
    <p>Importez votre document pour voir l'analyse apparaître ici.</p>
</div>
""", unsafe_allow_html=True)


def render_score(score):
    color = "#c0392b" if score < 5 else "#b8860b" if score < 7 else "#2d6a4f"
    st.markdown(f"""
<div class="score-card">
    <h2 style="color: {color}; font-size: 2rem; margin: 0;">{score} / 10</h2>
    <p style="margin: 0.3rem 0 0 0; font-size: 0.78rem; text-transform: uppercase;
              letter-spacing: 1px; color: #6b635a;">Score global</p>
</div>
""", unsafe_allow_html=True)


def render_footer():
    st.markdown("""
<div class="footer">
    Coach IA &nbsp;&bull;&nbsp; Powered by Groq (LLaMA 3.3 70B) &nbsp;&bull;&nbsp; Projet Académique
</div>
""", unsafe_allow_html=True)