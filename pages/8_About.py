"""
Page 8: About & System Architecture Page
"""

import streamlit as st

def render():
    st.title("ℹ️ About Lost-Object Memory Robot")
    st.markdown("""
    ### 🤖 Software-Only AI & Virtual Robotics Architecture

    The **Lost-Object Memory Robot** is an autonomous virtual robotics system operating entirely in software. 
    It eliminates the need for physical hardware (Arduino, Raspberry Pi, motors, sensors) by digitally simulating 
    sensor perception, spatial memory, path planning, and data analytics.

    ---

    ### 🧩 Core Algorithmic Components

    #### 1. Computer Vision (Ultralytics YOLOv8 / OpenCV)
    * Uses a lightweight nano pretrained model (`yolov8n.pt`) trained on the **COCO Dataset** (80 object classes).
    * Performs real-time bounding box detection, class identification, and confidence calculation.
    * Converts visual detections into 2D spatial grid coordinates inside the simulated room.

    #### 2. Spatial Memory System (SQLite)
    * Implements persistent relational database tables (`objects`, `detections`, `searches`, `robot_movements`).
    * **Memory Logic**: When an object is re-detected, its latest known location is updated in the primary `objects` table while historical records are preserved in `detections` without deletion.

    #### 3. Autonomous A* Path Planning (Scratch Python Implementation)
    * Implemented from scratch using a min-heap priority queue (`heapq`).
    * Computes optimal 8-directional paths on a 2D grid matrix ($24 \\times 16$).
    * Employs Euclidean heuristic distance $h(n) = \\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$ to guarantee shortest path length while dynamically avoiding wall and furniture obstacles.

    #### 4. Statistical Analytics Pipeline (R + ggplot2)
    * Automatically exports SQLite relational tables into standard CSV files (`data/`).
    * Invokes `Rscript` with `ggplot2`, `dplyr`, and `readr` to calculate statistical trends and export 6 high-resolution plots to `outputs/plots/`.
    * Includes an automated Python Matplotlib fallback engine to ensure deployability across all cloud environments without crashing.

    ---

    ### 🏗️ Database Schema Summary

    * **`objects`**: `(id, object_name, first_seen, last_seen, last_x, last_y, confidence, image_source)`
    * **`detections`**: `(id, timestamp, object_name, x, y, confidence, image_source)`
    * **`searches`**: `(id, timestamp, object_name, start_x, start_y, target_x, target_y, path_distance, status)`
    * **`robot_movements`**: `(id, timestamp, start_x, start_y, end_x, end_y, distance, status)`
    """)

if __name__ == "__main__":
    render()
