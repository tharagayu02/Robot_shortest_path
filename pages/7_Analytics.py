"""
Page 7: R Data Analytics & Visualization Page
"""

import streamlit as st
import os
from pathlib import Path
from src.analytics import generate_analytics_plots
from src.config import OUTPUTS_DIR


def render():
    st.title("📊 R Data Analytics & Visualizations")
    st.markdown("Statistical analysis and `ggplot2` visualizations generated from SQLite historical database records.")

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        run_analytics = st.button("📈 Run R Analytics Pipeline", type="primary", use_container_width=True)

    if run_analytics or not any(OUTPUTS_DIR.glob("*.png")):
        with st.spinner("Exporting SQLite CSVs & rendering R ggplot2 plots..."):
            success, msg, engine = generate_analytics_plots()
            if success:
                st.success(f"[{engine}] {msg}")
            else:
                st.error(f"Error generating analytics: {msg}")

    st.markdown("---")

    # Display 6 Plots in 2-column Grid Layout
    plot_files = [
        ("plot1_detection_freq.png", "Plot 1: Object Detection Frequency"),
        ("plot2_detection_timeline.png", "Plot 2: Detection Count & Confidence Timeline"),
        ("plot3_avg_search_distance.png", "Plot 3: Average Search Distance by Object"),
        ("plot4_search_success_rate.png", "Plot 4: Search Outcome Distribution"),
        ("plot5_movement_distance.png", "Plot 5: Robot Trajectory Movement Distances"),
        ("plot6_object_location_history.png", "Plot 6: 2D Spatial Memory Location History")
    ]

    p_col1, p_col2 = st.columns(2)

    for idx, (pf, title) in enumerate(plot_files):
        img_path = OUTPUTS_DIR / pf
        target_col = p_col1 if idx % 2 == 0 else p_col2
        with target_col:
            st.subheader(title)
            if img_path.exists():
                st.image(str(img_path), use_container_width=True)
            else:
                st.warning(f"Plot '{pf}' not yet generated. Click 'Run R Analytics Pipeline' above.")

if __name__ == "__main__":
    render()
