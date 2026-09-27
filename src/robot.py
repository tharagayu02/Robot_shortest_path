"""
Virtual Robot Agent Module.
Represents autonomous robot state, position, orientation, target tracking,
path step execution, and status reporting.
"""

import math
from typing import Tuple, List, Optional, Dict, Any


class RobotAgent:
    """Virtual autonomous robot operating inside 2D simulated environment."""

    def __init__(self, start_x: int = 2, start_y: int = 2, name: str = "Aegis-1"):
        self.name = name
        self.x: int = start_x
        self.y: int = start_y
        self.orientation: float = 0.0  # Angle in degrees (0 = East, 90 = South, 180 = West, 270 = North)
        self.speed: float = 1.0        # Grid cells per step
        self.current_target: Optional[Tuple[int, int]] = None
        self.target_name: Optional[str] = None
        self.current_path: List[Tuple[int, int]] = []
        self.path_index: int = 0
        self.status: str = "IDLE"  # IDLE, PLANNING, NAVIGATING, ARRIVED, NOT_FOUND, ERROR
        self.visited_cells: List[Tuple[int, int]] = [(start_x, start_y)]

    def set_position(self, x: int, y: int) -> None:
        """Update robot grid position."""
        self.x = x
        self.y = y
        if (x, y) not in self.visited_cells:
            self.visited_cells.append((x, y))

    def assign_navigation_task(self, target_name: str, target_pos: Tuple[int, int], path: List[Tuple[int, int]]) -> None:
        """Assign target location and A* calculated route to the robot."""
        self.target_name = target_name
        self.current_target = target_pos
        self.current_path = path
        self.path_index = 0
        self.status = "NAVIGATING" if path else "NOT_FOUND"

    def step_along_path(self) -> Tuple[bool, Tuple[int, int]]:
        """
        Advance the robot one step along its active path.

        :return: Tuple of (has_arrived, current_position)
        """
        if not self.current_path or self.path_index >= len(self.current_path):
            self.status = "ARRIVED" if self.current_target else "IDLE"
            return True, (self.x, self.y)

        next_cell = self.current_path[self.path_index]
        dx = next_cell[0] - self.x
        dy = next_cell[1] - self.y

        # Update orientation based on movement vector
        if dx != 0 or dy != 0:
            angle_rad = math.atan2(dy, dx)
            self.orientation = math.degrees(angle_rad) % 360.0

        self.set_position(next_cell[0], next_cell[1])
        self.path_index += 1

        if self.path_index >= len(self.current_path):
            self.status = "ARRIVED"
            return True, (self.x, self.y)

        return False, (self.x, self.y)

    def reset_target(self) -> None:
        """Clear active navigation target and path."""
        self.current_target = None
        self.target_name = None
        self.current_path = []
        self.path_index = 0
        self.status = "IDLE"

    def get_status_dict(self) -> Dict[str, Any]:
        """Return clean status dictionary for Streamlit UI cards."""
        return {
            "name": self.name,
            "position": (self.x, self.y),
            "orientation": f"{round(self.orientation, 1)}°",
            "status": self.status,
            "target": self.target_name or "None",
            "target_pos": self.current_target or "N/A",
            "path_remaining": len(self.current_path) - self.path_index if self.current_path else 0
        }
