"""
Page 4: Robot Spatial Memory Inspection Page
"""

import streamlit as st
import pandas as pd
from src.memory import SpatialMemorySystem
from src.database import clear_database
from src.sample_data import seed_demo_mode_data

def render():
    st.title("🧠 Robot Spatial Memory System")
    st.markdown("Persistent SQLite spatial memory database containing latest known object coordinates, timestamps, and detection histories.")

    memory = SpatialMemorySystem()
    objects = memory.get_memory_summary()

    # Metrics top bar
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("Objects in Memory", len(objects))
    with m_col2:
        avg_conf = round(sum(o["confidence"] for o in objects) / len(objects), 1) if objects else 0.0
        st.metric("Avg Memory Confidence", f"{avg_conf}%")
    with m_col3:
        st.metric("Memory Storage Engine", "SQLite (`objects` table)")

    st.markdown("---")

    if objects:
        st.subheader("📋 Primary Spatial Memory Ledger (`objects` table)")
        df_obj = pd.DataFrame(objects)
        display_df = df_obj[["id", "object_name", "last_x", "last_y", "confidence", "first_seen", "last_seen", "image_source"]]
        display_df.columns = ["ID", "Object Name", "Grid X", "Grid Y", "Confidence %", "First Detected", "Last Updated", "Source Image"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.subheader("📜 Complete Historical Detections Log (`detections` table)")
        st.caption("Historical log of all detection events. Preserves complete timeline history.")
        history = memory.get_detection_history(limit=100)
        if history:
            df_hist = pd.DataFrame(history)[["id", "timestamp", "object_name", "x", "y", "confidence", "image_source"]]
            df_hist.columns = ["Log ID", "Timestamp", "Object", "X", "Y", "Confidence %", "Image Source"]
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
    else:
        st.info("Spatial memory is currently empty.")
        if st.button("🌱 Populate Memory with Demo Objects", type="primary"):
            seed_demo_mode_data()
            st.rerun()

    st.markdown("---")
    col_reset, _ = st.columns([1, 2])
    with col_reset:
        if st.button("⚠️ Reset All Spatial Memory", type="secondary"):
            clear_database()
            st.warning("Database cleared.")
            st.rerun()

if __name__ == "__main__":
    render()
