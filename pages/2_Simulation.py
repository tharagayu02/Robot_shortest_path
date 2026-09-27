"""
Page 2: Robot 2D Room Simulation Page
"""

import streamlit as st
import time
from src.simulation import RoomSimulation
from src.robot import RobotAgent
from src.database import get_all_objects

def render():
    st.title("🗺️ 2D Room Simulation Environment")
    st.markdown("Visual 2D room grid containing walls, furniture, detected object markers, and autonomous robot.")

    if "sim" not in st.session_state:
        st.session_state.sim = RoomSimulation()
    if "robot" not in st.session_state:
        st.session_state.robot = RobotAgent(start_x=2, start_y=2)

    sim = st.session_state.sim
    robot = st.session_state.robot

    # Control Columns
    col_sim, col_ctrl = st.columns([3, 1])

    with col_ctrl:
        st.subheader("⚙️ Robot Controls")
        st.write(f"**Current Position**: ({robot.x}, {robot.y})")
        st.write(f"**Status**: `{robot.status}`")
        st.write(f"**Target**: {robot.target_name or 'None'}")

        st.markdown("---")
        st.write("**Manual Teleoperation**")
        m_col1, m_col2, m_col3 = st.columns(3)

        with m_col2:
            if st.button("⬆️ Up", key="btn_up"):
                if robot.y > 1 and sim.grid[robot.y - 1][robot.x] == 0:
                    robot.set_position(robot.x, robot.y - 1)
                    robot.orientation = 270.0
                    st.rerun()

        m_row2_1, m_row2_2, m_row2_3 = st.columns(3)
        with m_row2_1:
            if st.button("⬅️ Left", key="btn_left"):
                if robot.x > 1 and sim.grid[robot.y][robot.x - 1] == 0:
                    robot.set_position(robot.x - 1, robot.y)
                    robot.orientation = 180.0
                    st.rerun()

        with m_row2_3:
            if st.button("➡️ Right", key="btn_right"):
                if robot.x < sim.width - 2 and sim.grid[robot.y][robot.x + 1] == 0:
                    robot.set_position(robot.x + 1, robot.y)
                    robot.orientation = 0.0
                    st.rerun()

        with m_col2:
            if st.button("⬇️ Down", key="btn_down"):
                if robot.y < sim.height - 2 and sim.grid[robot.y + 1][robot.x] == 0:
                    robot.set_position(robot.x, robot.y + 1)
                    robot.orientation = 90.0
                    st.rerun()

        st.markdown("---")
        if st.button("🔄 Reset Environment", use_container_width=True):
            sim.build_default_room()
            robot.set_position(2, 2)
            robot.reset_target()
            st.rerun()

    with col_sim:
        img = sim.render_pygame_frame(
            robot_pos=(robot.x, robot.y),
            robot_orientation=robot.orientation,
            path=robot.current_path,
            target_pos=robot.current_target
        )
        st.image(img, caption="Live 2D Room Grid Matrix (24x16)", use_container_width=True)

if __name__ == "__main__":
    render()
