"""
Page 1: Home Dashboard & Overview with Sage Green & Ivory Aesthetic
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from src.database import init_db, get_performance_metrics, get_all_objects
from src.sample_data import seed_demo_mode_data
from src.config import BASE_DIR


def render():
    # Hero Banner Card with Robot Background Image
    bg_img_path = BASE_DIR / "assets" / "images" / "robot_background.jpg"

    st.markdown("""
        <div class="hero-box">
            <h1>🤖 Lost-Object Memory Robot</h1>
            <p>
                Autonomous Software-Only Virtual Robotics System combining 
                <strong>YOLOv8 Computer Vision</strong>, <strong>SQLite Spatial Memory</strong>, 
                <strong>A* Pathfinding</strong>, and <strong>R ggplot2 Analytics</strong>.
            </p>
        </div>
    """, unsafe_allow_html=True)

    if bg_img_path.exists():
        st.image(str(bg_img_path), caption="Virtual Autonomous Robot in Sage Green & Ivory Laboratory Environment", use_container_width=True)

    # Initialize DB
    init_db()
    metrics = get_performance_metrics()

    # Top KPI Metrics Cards in Sage Green & Ivory
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Objects Remembered", value=metrics["unique_objects"], delta="Spatial Memory DB")

    with col2:
        st.metric(label="Total Detections", value=metrics["total_detections"], delta="Vision Logs")

    with col3:
        st.metric(label="Searches Conducted", value=metrics["total_searches"], delta=f"{metrics['search_success_rate']}% Success")

    with col4:
        st.metric(label="Avg Path Length", value=f"{metrics['avg_path_length']} units", delta="A* Optimized")

    st.markdown("---")

    # Main Layout
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("🌿 System Operational Summary")
        st.info("""
            **Virtual Robot Status**: `IDLE` (Ready for autonomous navigation)<br>
            **Environment**: 24 x 16 Grid Matrix (Walls, Tables, Shelves, Chairs)<br>
            **Object Detection Engine**: Ultralytics YOLOv8 / OpenCV<br>
            **Pathfinding Engine**: A* Search (Scratch Python Implementation)<br>
            **Analytics Module**: R `ggplot2` / `dplyr` Statistical Engine
        """, icon="🤖")

        st.subheader("⚡ Quick Actions & Demo Mode")
        demo_btn = st.button("🚀 Seed Demo Mode Data", type="primary", use_container_width=True)
        if demo_btn:
            seed_demo_mode_data()
            st.success("Successfully loaded sample room environment, COCO detections, and historical searches!")
            st.rerun()

    with col_right:
        st.subheader("🧠 Latest Remembered Objects")
        objects = get_all_objects()
        if objects:
            df = pd.DataFrame(objects)[["object_name", "last_x", "last_y", "confidence", "last_seen"]]
            df.columns = ["Object", "X", "Y", "Confidence %", "Last Seen"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("No objects remembered in spatial database yet. Click 'Seed Demo Mode Data' above or run detection!")

if __name__ == "__main__":
    render()
