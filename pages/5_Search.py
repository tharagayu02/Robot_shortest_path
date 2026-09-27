"""
Page 5: Object Search & A* Path Planning Execution Page
"""

import os
import streamlit as st
import time
import pandas as pd
from PIL import Image
from src.memory import SpatialMemorySystem
from src.pathfinding import astar_search
from src.simulation import RoomSimulation
from src.robot import RobotAgent
from src.sample_data import seed_demo_mode_data
from src.config import ASSETS_DIR, UPLOADED_IMAGES_DIR


def render():
    st.title("🔎 Find an Object & A* Path Navigation")
    st.markdown("Query spatial memory for an object, retrieve the original room image where it was detected, calculate an obstacle-avoiding A* route, and visually navigate the robot.")

    memory = SpatialMemorySystem()
    objects = memory.get_memory_summary()

    if "sim" not in st.session_state:
        st.session_state.sim = RoomSimulation()
    if "robot" not in st.session_state:
        st.session_state.robot = RobotAgent(start_x=2, start_y=2)

    sim = st.session_state.sim
    robot = st.session_state.robot

    # Object Search Form
    object_names = [o["object_name"] for o in objects] if objects else ["Keys", "Bottle", "Book", "Laptop", "Chair"]

    col_search, col_btn = st.columns([3, 1])

    with col_search:
        search_query = st.selectbox("Where is your object?", options=object_names, index=0 if object_names else None)

    with col_btn:
        st.write("")
        st.write("")
        run_search = st.button("🔍 SEARCH OBJECT", type="primary", use_container_width=True)

    if not objects:
        st.info("Spatial memory is empty. Click below to load demo object memory.")
        if st.button("🌱 Load Demo Memory Objects"):
            seed_demo_mode_data()
            st.rerun()
        return

    target_obj = None

    if run_search and search_query:
        target_obj = memory.locate_object(search_query)

        if not target_obj:
            st.error(f"❌ Object '{search_query}' not found in robot spatial memory.")
            memory.log_search(search_query, (robot.x, robot.y), None, 0.0, "Not Found")
            return

        tx, ty = target_obj["last_x"], target_obj["last_y"]
        start_pos = (robot.x, robot.y)
        goal_pos = (tx, ty)

        # Run A* Pathfinding
        grid_matrix = sim.get_grid_matrix()
        plan = astar_search(grid_matrix, start_pos, goal_pos, allow_diagonal=True)

        if plan["success"]:
            st.success(f"✅ Route Found! Object '{search_query}' located at Grid ({tx}, {ty}). Path distance: {plan['path_length']} units ({plan['num_steps']} steps).")
            robot.assign_navigation_task(search_query, goal_pos, plan["path"])
            memory.log_search(search_query, start_pos, goal_pos, plan["path_length"], "Found")
            memory.log_movement(start_pos, goal_pos, plan["path_length"], "completed")
        else:
            st.error(f"⚠️ Object found at ({tx}, {ty}), but no unblocked path could be calculated. Reason: {plan['error']}")
            memory.log_search(search_query, start_pos, goal_pos, 0.0, "No Path")

    # Display Original Room Photo & 2D A* Map Side-by-Side
    col_room_img, col_map = st.columns([1, 1])

    active_target_name = robot.target_name or (search_query if 'run_search' in locals() and run_search else None)
    if active_target_name:
        target_obj = memory.locate_object(active_target_name)

    with col_room_img:
        st.subheader("📷 Detected Room Source Image")
        if target_obj and target_obj.get("image_source"):
            img_src = target_obj["image_source"]
            possible_paths = [
                UPLOADED_IMAGES_DIR / img_src,
                ASSETS_DIR / img_src,
                ASSETS_DIR / f"sample_{img_src.lower()}.jpg"
            ]

            found_img_path = None
            for p in possible_paths:
                if p.exists():
                    found_img_path = p
                    break

            if found_img_path:
                st.image(Image.open(found_img_path), caption=f"Room Image Source: {img_src}", use_container_width=True)
            else:
                st.info(f"Room image `{img_src}` stored in database records.")
        else:
            st.info("Select an object and click SEARCH OBJECT to display its room detection source photo.")

    with col_map:
        st.subheader("🗺️ 2D Room Grid & A* Shortest Path Execution")
        img_map = sim.render_pygame_frame(
            robot_pos=(robot.x, robot.y),
            robot_orientation=robot.orientation,
            path=robot.current_path,
            target_pos=robot.current_target
        )
        st.image(img_map, caption="Visual 2D Room Matrix with A* Path Execution", use_container_width=True)

        if robot.current_target and robot.target_name:
            st.markdown(f"""
                <div style="background: #3A4F3B; padding: 1rem; border-radius: 8px; border-left: 4px solid #647A65; color: #FFFFFF !important;">
                    <h5 style="margin: 0; color: #FFFFFF !important; font-weight: 700;">Active Target: {robot.target_name}</h5>
                    <p style="margin-top: 0.4rem; color: #FFFFFF !important; font-size: 0.95rem;">
                        <strong style="color: #FFFFFF !important;">Coordinates</strong>: Grid ({robot.current_target[0]}, {robot.current_target[1]}) | 
                        <strong style="color: #FFFFFF !important;">Path Length</strong>: {len(robot.current_path)} steps | 
                        <strong style="color: #FFFFFF !important;">Status</strong>: <code style="color: #FFFFFF !important; background: #283829; padding: 2px 6px; border-radius: 4px;">{robot.status}</code>
                    </p>
                </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("▶️ Step Navigation", type="primary", use_container_width=True):
                    arrived, pos = robot.step_along_path()
                    if arrived:
                        st.success(f"🎯 Robot reached {robot.target_name} at position {pos}!")
                    st.rerun()

            with c2:
                if st.button("⏩ Complete Full Navigation Route", use_container_width=True):
                    while not robot.step_along_path()[0]:
                        pass
                    st.success(f"🎯 Robot reached {robot.target_name} at position ({robot.x}, {robot.y})!")
                    st.rerun()

if __name__ == "__main__":
    render()
