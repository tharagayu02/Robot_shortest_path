"""
Main Application Entrypoint for Lost-Object Memory Robot.
Provides global sidebar navigation, Sage Green & Ivory CSS styling, and page router.
"""

import importlib
import base64
from pathlib import Path
import streamlit as st
from src.database import init_db
from src.config import BASE_DIR

# Configure Streamlit Page Settings
st.set_page_config(
    page_title="Lost-Object Memory Robot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Sage Green & Ivory Custom CSS Theme
st.markdown("""
<style>
    /* Remove Top Gap & Standard Margins */
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 95% !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0px !important;
        display: none !important;
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Core Sage Green & Ivory Theme Colors */
    .stApp {
        background-color: #F6F4EE !important;
        color: #1E281F !important;
        font-family: 'Segoe UI', -apple-system, sans-serif;
    }

    /* Global Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #2D3A2E;
        font-weight: 700;
    }
    p, span, label {
        color: #2D3A2E;
    }

    /* Hero & Green Banner Boxes (FORCED WHITE FONT) */
    .hero-box, .green-box, .green-card {
        background: linear-gradient(135deg, #3A4F3B 0%, #283829 100%) !important;
        padding: 1.8rem !important;
        border-radius: 14px !important;
        border: 1.5px solid #647A65 !important;
        box-shadow: 0 6px 16px rgba(40, 56, 41, 0.25) !important;
        margin-bottom: 1.2rem !important;
        color: #FFFFFF !important;
    }
    .hero-box *, .green-box *, .green-card * {
        color: #FFFFFF !important;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
    }
    .hero-box h1, .green-box h1 {
        font-size: 2.3rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        color: #FFFFFF !important;
    }
    .hero-box p, .green-box p {
        font-size: 1.1rem !important;
        margin-top: 0.5rem !important;
        max-width: 90% !important;
        color: #FFFFFF !important;
    }

    /* Streamlit Alert Notifications (Info/Success/Warning inside Green Boxes) */
    div[data-testid="stNotification"], div[data-baseweb="notification"] {
        background-color: #3A4F3B !important;
        border: 1px solid #647A65 !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
    }
    div[data-testid="stNotification"] *, div[data-baseweb="notification"] * {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Sidebar Styling (Sage Green & Ivory) */
    section[data-testid="stSidebar"] {
        background-color: #E8ECE6 !important;
        border-right: 2px solid #C4D2C5 !important;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        color: #2D3A2E !important;
    }
    div[data-testid="stSidebarNav"] {
        background-color: #E8ECE6 !important;
    }

    /* Custom Metric Cards */
    div[data-testid="stMetric"] {
        background: #EFECE3 !important;
        border: 1.5px solid #C4D2C5 !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        box-shadow: 0 4px 12px rgba(60, 78, 61, 0.08) !important;
    }
    div[data-testid="stMetric"] label {
        color: #586B5A !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #2D3A2E !important;
        font-weight: 800 !important;
    }

    /* Primary Buttons (Green Box - White Font) */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #4F6E56 0%, #3A4F3B 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(79, 110, 86, 0.3) !important;
    }
    .stButton>button[kind="primary"] * {
        color: #FFFFFF !important;
    }
    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #3A4F3B 0%, #283829 100%) !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 14px rgba(79, 110, 86, 0.4) !important;
    }

    /* Secondary Buttons */
    .stButton>button[kind="secondary"] {
        background: #FAF8F5 !important;
        color: #2D3A2E !important;
        border: 1.5px solid #A4B8A5 !important;
    }
    .stButton>button[kind="secondary"]:hover {
        background: #E8ECE6 !important;
        border-color: #4F6E56 !important;
    }

    /* Input Controls & Selectboxes */
    div[data-baseweb="select"] > div {
        background-color: #FAF8F5 !important;
        border-color: #B8C9B9 !important;
        color: #1E281F !important;
        border-radius: 8px !important;
    }

    /* Dataframes & Tables */
    div[data-testid="stDataFrame"] {
        border: 1.5px solid #C4D2C5 !important;
        border-radius: 10px !important;
        background-color: #FAF8F5 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize SQLite Database Schema
init_db()

# Sidebar Navigation Router with local robot header
robot_bg_path = BASE_DIR / "assets" / "images" / "robot_background.jpg"
if robot_bg_path.exists():
    st.sidebar.image(str(robot_bg_path), use_container_width=True)

st.sidebar.title("🤖 Lost-Object Robot")
st.sidebar.caption("Sage Green & Ivory AI Robotics Console")

pages_map = {
    "1. Home Dashboard": "pages.1_Home",
    "2. 2D Room Simulation": "pages.2_Simulation",
    "3. Object Detection (YOLO)": "pages.3_Detection",
    "4. Spatial Memory System": "pages.4_Memory",
    "5. Find an Object (A*)": "pages.5_Search",
    "6. Search History": "pages.6_History",
    "7. R Analytics & Visualizations": "pages.7_Analytics",
    "8. About & Architecture": "pages.8_About"
}

selected_page_name = st.sidebar.radio("Go to Page:", list(pages_map.keys()))

st.sidebar.markdown("---")
st.sidebar.info("""
**Tech Stack:**
- Python 3.11+ & Pygame
- Ultralytics YOLOv8
- SQLite Spatial DB
- Scratch A* Algorithm
- R ggplot2 Analytics
""", icon="🌱")

# Dynamic Page Loading via importlib
module_path = pages_map[selected_page_name]
page_module = importlib.import_module(module_path)
page_module.render()
