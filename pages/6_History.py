"""
Page 6: Search & Movement History Audit Page
"""

import streamlit as st
import pandas as pd
from src.database import get_all_searches, get_all_movements

def render():
    st.title("📜 Search & Trajectory History")
    st.markdown("Filterable audit log of past user search queries, A* route lengths, and robot physical movements.")

    searches = get_all_searches(limit=200)

    if not searches:
        st.info("No search queries recorded yet. Conduct a search on Page 5!")
        return

    df_searches = pd.DataFrame(searches)

    # Filter Controls
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        status_filter = st.multiselect("Filter by Status:", options=list(df_searches["status"].unique()), default=list(df_searches["status"].unique()))
    with col_f2:
        obj_filter = st.multiselect("Filter by Object:", options=list(df_searches["object_name"].unique()), default=list(df_searches["object_name"].unique()))

    # Apply filters
    filtered_df = df_searches[
        (df_searches["status"].isin(status_filter)) &
        (df_searches["object_name"].isin(obj_filter))
    ]

    st.subheader("🔍 Search Query Ledger (`searches` table)")
    display_df = filtered_df[["id", "timestamp", "object_name", "start_x", "start_y", "target_x", "target_y", "path_distance", "status"]]
    display_df.columns = ["Search ID", "Timestamp", "Object Queried", "Start X", "Start Y", "Target X", "Target Y", "Distance (units)", "Status"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    st.subheader("🚜 Robot Movement Trajectory Ledger (`robot_movements` table)")
    movements = get_all_movements(limit=100)
    if movements:
        df_moves = pd.DataFrame(movements)[["id", "timestamp", "start_x", "start_y", "end_x", "end_y", "distance", "status"]]
        df_moves.columns = ["Trip ID", "Timestamp", "Start X", "Start Y", "End X", "End Y", "Distance Traversed", "Status"]
        st.dataframe(df_moves, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    render()
