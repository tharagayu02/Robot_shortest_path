"""
Analytics & Data Export Engine.
Handles SQLite export to CSV and triggers R ggplot2 plot generation
with an automated Python Matplotlib fallback pipeline in Sage Green & Ivory theme.
"""

import os
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
from pathlib import Path
from typing import Dict, Any, Tuple
from src.config import (
    DETECTIONS_CSV, SEARCHES_CSV, MOVEMENTS_CSV, OUTPUTS_DIR, BASE_DIR, R_DIR
)
from src.database import get_connection


def export_sqlite_to_csv() -> Tuple[bool, str]:
    """Export SQLite tables to data/ CSV files for R and Python analytics."""
    try:
        conn = get_connection()

        # Detections
        df_det = pd.read_sql_query("SELECT * FROM detections", conn)
        df_det.to_csv(DETECTIONS_CSV, index=False)

        # Searches
        df_search = pd.read_sql_query("SELECT * FROM searches", conn)
        df_search.to_csv(SEARCHES_CSV, index=False)

        # Robot Movements
        df_move = pd.read_sql_query("SELECT * FROM robot_movements", conn)
        df_move.to_csv(MOVEMENTS_CSV, index=False)

        conn.close()
        return True, f"Successfully exported SQLite tables to {DETECTIONS_CSV.parent}"
    except Exception as e:
        return False, f"Error exporting SQLite data to CSV: {e}"


def generate_analytics_plots() -> Tuple[bool, str, str]:
    """
    Generate 6 statistical plots into outputs/plots/.
    First attempts execution via Rscript (R/plots.R).
    If Rscript is missing or fails, seamlessly runs Python matplotlib fallback.
    """
    # 1. Export fresh CSVs first
    success, msg = export_sqlite_to_csv()
    if not success:
        return False, msg, "export_error"

    # Ensure output directory exists
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Try Rscript execution
    try:
        r_script_path = R_DIR / "plots.R"
        result = subprocess.run(
            ["Rscript", str(r_script_path)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True, "Successfully generated 6 statistical plots using R ggplot2.", "R_ggplot2"
        else:
            print(f"[Analytics] Rscript stderr: {result.stderr}")
    except (FileNotFoundError, subprocess.SubprocessError) as e:
        print(f"[Analytics] Rscript execution unavailable ({e}). Using Python matplotlib fallback.")

    # 3. Python Matplotlib Fallback Plot Generator in Sage Green & Ivory
    try:
        _generate_python_fallback_plots()
        return True, "Generated 6 statistical plots using Python Matplotlib fallback engine (Rscript unavailable).", "Python_Fallback"
    except Exception as e:
        return False, f"Failed to generate analytics plots: {e}", "error"


def _generate_python_fallback_plots() -> None:
    """Generate 6 high-resolution plots matching R output formatting using matplotlib/pandas in Sage Green & Ivory palette."""
    plt.rcParams.update({'font.sans-serif': 'Segoe UI', 'axes.edgecolor': '#B8C9B9'})

    bg_color = '#F5F2EB'       # Warm Ivory
    panel_color = '#EAE5DA'    # Ivory Card
    sage_primary = '#4F6E56'   # Deep Sage
    sage_secondary = '#647A65' # Mid Sage
    sage_light = '#8A9F8B'     # Light Sage
    accent_amber = '#D97706'   # Warm Clay
    text_color = '#1E291E'     # Deep Forest Charcoal

    # Read CSVs
    df_det = pd.read_csv(DETECTIONS_CSV) if DETECTIONS_CSV.exists() else pd.DataFrame()
    df_search = pd.read_csv(SEARCHES_CSV) if SEARCHES_CSV.exists() else pd.DataFrame()
    df_move = pd.read_csv(MOVEMENTS_CSV) if MOVEMENTS_CSV.exists() else pd.DataFrame()

    # Plot 1: Object Detection Frequency
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=bg_color)
    ax.set_facecolor(panel_color)
    if not df_det.empty and 'object_name' in df_det.columns:
        counts = df_det['object_name'].value_counts()
        ax.barh(counts.index, counts.values, color=sage_primary, edgecolor=bg_color, height=0.55)
        ax.set_title("Object Detection Frequency", fontsize=14, color=text_color, fontweight='bold', pad=12)
        ax.set_xlabel("Detection Count", color=text_color)
        ax.set_ylabel("Object Name", color=text_color)
        ax.tick_params(colors=text_color)
        ax.grid(color='#D8D2C2', linestyle='--', linewidth=0.5)
    else:
        ax.text(0.5, 0.5, "No Detection Data Available", ha='center', va='center', color='#526353')
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "plot1_detection_freq.png", dpi=150)
    plt.close()

    # Plot 2: Detection Count Over Time / Confidence Trend
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=bg_color)
    ax.set_facecolor(panel_color)
    if not df_det.empty and 'confidence' in df_det.columns:
        ax.plot(range(1, len(df_det) + 1), df_det['confidence'], marker='o', color=sage_primary, linewidth=2, label='Confidence %')
        ax.set_title("Object Detection Timeline & Confidence", fontsize=14, color=text_color, fontweight='bold', pad=12)
        ax.set_xlabel("Observation Index", color=text_color)
        ax.set_ylabel("Confidence (%)", color=text_color)
        ax.tick_params(colors=text_color)
        ax.grid(color='#D8D2C2', linestyle='--', linewidth=0.5)
    else:
        ax.text(0.5, 0.5, "No Detection Timeline Data", ha='center', va='center', color='#526353')
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "plot2_detection_timeline.png", dpi=150)
    plt.close()

    # Plot 3: Average Search Distance by Object
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=bg_color)
    ax.set_facecolor(panel_color)
    if not df_search.empty and 'object_name' in df_search.columns:
        found_df = df_search[df_search['status'] == 'Found']
        if not found_df.empty:
            avg_dist = found_df.groupby('object_name')['path_distance'].mean()
            ax.bar(avg_dist.index, avg_dist.values, color=sage_secondary, width=0.5, edgecolor=bg_color)
            ax.set_title("Average Search Path Distance by Object", fontsize=14, color=text_color, fontweight='bold', pad=12)
            ax.set_xlabel("Object Name", color=text_color)
            ax.set_ylabel("Average Grid Distance", color=text_color)
            ax.tick_params(colors=text_color)
            ax.grid(color='#D8D2C2', linestyle='--', linewidth=0.5)
        else:
            ax.text(0.5, 0.5, "No Successful Search Distances", ha='center', va='center', color='#526353')
    else:
        ax.text(0.5, 0.5, "No Search History Data", ha='center', va='center', color='#526353')
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "plot3_avg_search_distance.png", dpi=150)
    plt.close()

    # Plot 4: Search Success Rate
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=bg_color)
    ax.set_facecolor(panel_color)
    if not df_search.empty and 'status' in df_search.columns:
        status_counts = df_search['status'].value_counts()
        bar_colors = [sage_primary if s == 'Found' else '#D9534F' for s in status_counts.index]
        ax.bar(status_counts.index, status_counts.values, color=bar_colors, width=0.4)
        ax.set_title("Search Outcome Distribution", fontsize=14, color=text_color, fontweight='bold', pad=12)
        ax.set_xlabel("Search Status", color=text_color)
        ax.set_ylabel("Query Count", color=text_color)
        ax.tick_params(colors=text_color)
        ax.grid(color='#D8D2C2', linestyle='--', linewidth=0.5)
    else:
        ax.text(0.5, 0.5, "No Search Query History", ha='center', va='center', color='#526353')
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "plot4_search_success_rate.png", dpi=150)
    plt.close()

    # Plot 5: Robot Movement Distance Over Time
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=bg_color)
    ax.set_facecolor(panel_color)
    if not df_move.empty and 'distance' in df_move.columns:
        ax.fill_between(range(1, len(df_move) + 1), df_move['distance'], color=sage_light, alpha=0.5)
        ax.plot(range(1, len(df_move) + 1), df_move['distance'], color=sage_primary, marker='o', linewidth=2)
        ax.set_title("Robot Movement Distance per Trip", fontsize=14, color=text_color, fontweight='bold', pad=12)
        ax.set_xlabel("Trip Index", color=text_color)
        ax.set_ylabel("Distance Traversed", color=text_color)
        ax.tick_params(colors=text_color)
        ax.grid(color='#D8D2C2', linestyle='--', linewidth=0.5)
    else:
        ax.text(0.5, 0.5, "No Movement Log Data", ha='center', va='center', color='#526353')
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "plot5_movement_distance.png", dpi=150)
    plt.close()

    # Plot 6: Object Location Spatial History
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=bg_color)
    ax.set_facecolor(panel_color)
    if not df_det.empty and 'x' in df_det.columns and 'y' in df_det.columns:
        scatter = ax.scatter(df_det['x'], df_det['y'], c=df_det.index, cmap='YlGn', s=120, edgecolors=sage_primary, alpha=0.9)
        ax.set_xlim(0, 24)
        ax.set_ylim(0, 16)
        ax.set_title("2D Spatial Memory Map of Object Detections", fontsize=14, color=text_color, fontweight='bold', pad=12)
        ax.set_xlabel("Grid X Coordinate", color=text_color)
        ax.set_ylabel("Grid Y Coordinate", color=text_color)
        ax.tick_params(colors=text_color)
        ax.grid(color='#D8D2C2', linestyle='--', linewidth=0.5)
    else:
        ax.text(0.5, 0.5, "No Spatial Location Detections", ha='center', va='center', color='#526353')
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "plot6_object_location_history.png", dpi=150)
    plt.close()
