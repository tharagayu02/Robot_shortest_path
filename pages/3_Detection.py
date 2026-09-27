"""
Page 3: Computer Vision Room Analysis, YOLO Detection, & A* Path Planning Page
"""

import os
import random
import datetime
import streamlit as st
import pandas as pd
from PIL import Image
from src.object_detection import get_object_detector
from src.memory import SpatialMemorySystem
from src.simulation import RoomSimulation
from src.robot import RobotAgent
from src.pathfinding import astar_search
from src.database import save_uploaded_room, get_all_rooms
from src.sample_data import generate_sample_images
from src.config import ASSETS_DIR, UPLOADED_IMAGES_DIR, GRID_WIDTH, GRID_HEIGHT


def adjust_to_nearest_reachable_cell(gx: int, gy: int, grid_matrix: list) -> tuple:
    """If target cell is inside an obstacle wall/furniture, adjust to nearest adjacent free cell."""
    h = len(grid_matrix)
    w = len(grid_matrix[0]) if h > 0 else 0

    if 0 <= gy < h and 0 <= gx < w and grid_matrix[gy][gx] == 0:
        return (gx, gy)

    # Search adjacent 8-neighbor cells for nearest free space
    dirs = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    for dx, dy in dirs:
        nx, ny = gx + dx, gy + dy
        if 0 <= ny < h and 0 <= nx < w and grid_matrix[ny][nx] == 0:
            return (nx, ny)

    return (gx, gy)


def render():
    st.title("📷 Room Image Detection & A* Path Navigation")
    st.markdown("Upload a room image or select a sample. YOLO detects objects, maps bounding box centers to room structure grid coordinates, stores records in SQLite, and computes A* shortest paths.")

    detector = get_object_detector()
    memory = SpatialMemorySystem()

    if "sim" not in st.session_state:
        st.session_state.sim = RoomSimulation()
    if "robot" not in st.session_state:
        st.session_state.robot = RobotAgent(start_x=2, start_y=2)

    sim = st.session_state.sim
    robot = st.session_state.robot

    generate_sample_images()

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("1. Select or Upload Room Image")
        source_type = st.radio("Choose Input Source:", ["Upload Custom Room Image", "Sample COCO Dataset Image"], horizontal=True)

        selected_image = None
        image_name = "room_upload.jpg"
        save_path = None

        if source_type == "Upload Custom Room Image":
            uploaded_file = st.file_uploader("Upload Room Photo (JPG, PNG, JPEG)", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                selected_image = Image.open(uploaded_file)
                image_name = f"upload_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                save_path = UPLOADED_IMAGES_DIR / image_name
                selected_image.save(save_path)
        else:
            sample_files = list(ASSETS_DIR.glob("*.jpg"))
            if sample_files:
                sample_choice = st.selectbox("Select Sample COCO Room Image:", [f.name for f in sample_files])
                selected_image = Image.open(ASSETS_DIR / sample_choice)
                image_name = sample_choice
                save_path = ASSETS_DIR / sample_choice
            else:
                generate_sample_images()
                st.rerun()

        if selected_image is not None:
            st.image(selected_image, caption=f"Selected Input Room ({image_name})", use_container_width=True)
            run_btn = st.button("🔍 Run YOLO Detection & Store Room Objects", type="primary", use_container_width=True)

    with col_right:
        st.subheader("2. YOLO Detection & Spatial Database Memory")

        # Execute Detection Pipeline
        if selected_image is not None and ('run_btn' in locals() and run_btn or 'current_room_dets' not in st.session_state):
            with st.spinner("Executing YOLO Object Recognition & Grid Coordinate Mapping..."):
                dets, ann_img = detector.detect_objects(selected_image)

                # Store in Session State
                st.session_state.current_room_dets = dets
                st.session_state.current_ann_img = ann_img

                # Save Room & Objects to Database
                if save_path:
                    save_uploaded_room(
                        room_name=f"Room_{image_name}",
                        image_filename=image_name,
                        image_path=str(save_path),
                        num_objects=len(dets)
                    )

                # Update 2D simulation room objects strictly matching mapped bounding box grid coordinates
                grid_mat = sim.get_grid_matrix()
                for d in dets:
                    obj_name = d["object_name"]
                    conf = d["confidence"]
                    # Map to exact grid cell matching room structure
                    raw_gx, raw_gy = d["grid_x"], d["grid_y"]
                    valid_gx, valid_gy = adjust_to_nearest_reachable_cell(raw_gx, raw_gy, grid_mat)

                    d["grid_x"] = valid_gx
                    d["grid_y"] = valid_gy

                    memory.remember_object(obj_name, valid_gx, valid_gy, conf, image_source=image_name)
                    sim.add_object_to_room(obj_name, "📍", valid_gx, valid_gy, conf)

        if 'current_ann_img' in st.session_state:
            st.image(st.session_state.current_ann_img, caption="YOLO Bounding Boxes & Mapped 2D Grid Coordinates", use_container_width=True)
            dets = st.session_state.current_room_dets

            if dets:
                st.success(f"✅ Successfully detected {len(dets)} objects mapped to room structure! Stored in SQLite Spatial DB.")
                df_dets = pd.DataFrame(dets)
                st.dataframe(df_dets[["object_name", "confidence", "grid_x", "grid_y", "bbox"]], use_container_width=True, hide_index=True)
            else:
                st.warning("No objects detected in this image above threshold.")

    st.markdown("---")

    # Section 3: Instant A* Shortest Path Navigation Panel
    st.subheader("3. 🎯 Instant A* Shortest Path Navigation")
    st.markdown("Select an object detected in this room to calculate the obstacle-avoiding shortest path and watch the robot navigate to it.")

    objects_in_mem = memory.get_memory_summary()

    if objects_in_mem:
        col_nav_ctrl, col_nav_map = st.columns([1, 2])

        with col_nav_ctrl:
            target_obj_name = st.selectbox(
                "Select Target Object to Reach:",
                options=[o["object_name"] for o in objects_in_mem]
            )

            calc_path_btn = st.button("🚀 Calculate Shortest A* Route", type="primary", use_container_width=True)

            if calc_path_btn and target_obj_name:
                target_data = memory.locate_object(target_obj_name)
                if target_data:
                    tx, ty = target_data["last_x"], target_data["last_y"]
                    start_pos = (robot.x, robot.y)
                    goal_pos = (tx, ty)

                    # Compute A* Path
                    grid_matrix = sim.get_grid_matrix()
                    plan = astar_search(grid_matrix, start_pos, goal_pos, allow_diagonal=True)

                    if plan["success"]:
                        st.success(f"✅ Shortest A* Path Computed! Length: {plan['path_length']} units ({plan['num_steps']} steps). Time: {plan['planning_time_ms']} ms.")
                        robot.assign_navigation_task(target_obj_name, goal_pos, plan["path"])
                        memory.log_search(target_obj_name, start_pos, goal_pos, plan["path_length"], "Found")
                        memory.log_movement(start_pos, goal_pos, plan["path_length"], "completed")
                    else:
                        st.error(f"❌ Path calculation failed: {plan['error']}")
                        memory.log_search(target_obj_name, start_pos, goal_pos, 0.0, "No Path")

            if robot.current_target and robot.current_path:
                st.markdown("---")
                st.write(f"**Target**: `{robot.target_name}`")
                st.write(f"**Robot Position**: `({robot.x}, {robot.y})`")
                st.write(f"**Status**: `{robot.status}`")

                if st.button("▶️ Step Robot Navigation", type="primary", use_container_width=True):
                    arrived, pos = robot.step_along_path()
                    if arrived:
                        st.success(f"🎯 Robot arrived at {robot.target_name} position {pos}!")
                    st.rerun()

                if st.button("⏩ Complete Full Path Navigation", use_container_width=True):
                    while not robot.step_along_path()[0]:
                        pass
                    st.success(f"🎯 Robot arrived at {robot.target_name} position ({robot.x}, {robot.y})!")
                    st.rerun()

        with col_nav_map:
            img_map = sim.render_pygame_frame(
                robot_pos=(robot.x, robot.y),
                robot_orientation=robot.orientation,
                path=robot.current_path,
                target_pos=robot.current_target
            )
            st.image(img_map, caption="Visual 2D Room Grid Matrix & Calculated A* Route", use_container_width=True)

if __name__ == "__main__":
    render()
