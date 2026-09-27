"""
2D Room Simulation & Renderer Engine.
Manages grid representation (walls, furniture, objects, robot), JSON layout loading,
Pygame image array rendering, and Streamlit visualization canvas.
"""

import json
import os
import numpy as np
from PIL import Image
import pygame
from typing import List, Dict, Any, Tuple, Optional
from src.config import (
    GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, COLORS,
    CELL_EMPTY, CELL_OBSTACLE, DATA_DIR
)


class SimulationEnvironment:
    """Manages the 2D grid matrix and room layout elements."""

    def __init__(self, width: int = GRID_WIDTH, height: int = GRID_HEIGHT):
        self.width = width
        self.height = height
        self.grid = np.zeros((self.height, self.width), dtype=int)
        self.furniture: List[Dict[str, Any]] = []
        self.placed_objects: List[Dict[str, Any]] = []
        self.load_default_environment()

    def reset_grid(self) -> None:
        """Clear grid matrix."""
        self.grid.fill(CELL_EMPTY)

    def load_default_environment(self) -> None:
        """Load standard room layout with walls, tables, chairs, shelves, and objects."""
        self.furniture = [
            {"name": "Wall Top", "type": "wall", "x": 0, "y": 0, "w": 24, "h": 1},
            {"name": "Wall Bottom", "type": "wall", "x": 0, "y": 15, "w": 24, "h": 1},
            {"name": "Wall Left", "type": "wall", "x": 0, "y": 0, "w": 1, "h": 16},
            {"name": "Wall Right", "type": "wall", "x": 23, "y": 0, "w": 1, "h": 16},
            {"name": "Table Alpha", "type": "table", "x": 3, "y": 3, "w": 4, "h": 2},
            {"name": "Shelf Main", "type": "shelf", "x": 16, "y": 2, "w": 5, "h": 2},
            {"name": "Chair Desk", "type": "chair", "x": 4, "y": 11, "w": 3, "h": 2},
            {"name": "Office Desk", "type": "desk", "x": 15, "y": 10, "w": 5, "h": 3},
            {"name": "Storage Rack", "type": "shelf", "x": 10, "y": 6, "w": 2, "h": 4}
        ]
        self.grid.fill(CELL_EMPTY)
        for item in self.furniture:
            ix, iy, iw, ih = item["x"], item["y"], item["w"], item["h"]
            for y in range(iy, min(self.height, iy + ih)):
                for x in range(ix, min(self.width, ix + iw)):
                    self.grid[y][x] = CELL_OBSTACLE


class RoomSimulation:
    """Complete Room Simulation Engine with Pygame and PIL rendering capability."""

    def __init__(self, width: int = GRID_WIDTH, height: int = GRID_HEIGHT):
        self.width = width
        self.height = height
        self.grid = np.zeros((self.height, self.width), dtype=int)
        self.furniture: List[Dict[str, Any]] = []
        self.objects: List[Dict[str, Any]] = []
        self.env_json_path = DATA_DIR / "sample_environment.json"

        # Initialize Pygame in headless mode
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        self.surface = pygame.Surface((self.width * CELL_SIZE, self.height * CELL_SIZE))

        # Build initial environment
        self.load_environment()

    def load_environment(self) -> None:
        """Load environment layout from JSON file or build default if missing."""
        if self.env_json_path.exists():
            try:
                with open(self.env_json_path, "r") as f:
                    data = json.load(f)
                    self.furniture = data.get("furniture", [])
                    self.objects = data.get("objects", [])
                    self.rebuild_grid()
                    return
            except Exception as e:
                print(f"[Simulation] Error loading JSON environment: {e}")

        # Default fallback room layout
        self.build_default_room()
        self.save_environment()

    def build_default_room(self) -> None:
        """Construct standard room layout with boundary walls and furniture items."""
        self.furniture = [
            {"name": "Wall Top", "type": "wall", "x": 0, "y": 0, "w": 24, "h": 1},
            {"name": "Wall Bottom", "type": "wall", "x": 0, "y": 15, "w": 24, "h": 1},
            {"name": "Wall Left", "type": "wall", "x": 0, "y": 0, "w": 1, "h": 16},
            {"name": "Wall Right", "type": "wall", "x": 23, "y": 0, "w": 1, "h": 16},

            # Internal dividers & furniture
            {"name": "Table Alpha", "type": "table", "x": 3, "y": 3, "w": 4, "h": 2},
            {"name": "Shelf Main", "type": "shelf", "x": 16, "y": 2, "w": 5, "h": 2},
            {"name": "Chair Desk", "type": "chair", "x": 4, "y": 11, "w": 3, "h": 2},
            {"name": "Office Desk", "type": "desk", "x": 15, "y": 10, "w": 5, "h": 3},
            {"name": "Storage Rack", "type": "shelf", "x": 10, "y": 6, "w": 2, "h": 4}
        ]

        self.objects = [
            {"name": "Bottle", "icon": "🧴", "x": 18, "y": 3, "confidence": 94.2},
            {"name": "Book", "icon": "📕", "x": 5, "y": 4, "confidence": 88.7},
            {"name": "Chair", "icon": "🪑", "x": 5, "y": 12, "confidence": 91.4},
            {"name": "Laptop", "icon": "💻", "x": 17, "y": 11, "confidence": 96.0},
            {"name": "Keys", "icon": "🔑", "x": 11, "y": 8, "confidence": 92.5}
        ]
        self.rebuild_grid()

    def save_environment(self) -> None:
        """Save room configuration to JSON file."""
        data = {
            "width": self.width,
            "height": self.height,
            "furniture": self.furniture,
            "objects": self.objects
        }
        with open(self.env_json_path, "w") as f:
            json.dump(data, f, indent=2)

    def rebuild_grid(self) -> None:
        """Reconstruct 2D grid obstacle array from furniture positions."""
        self.grid = np.zeros((self.height, self.width), dtype=int)
        for item in self.furniture:
            ix, iy, iw, ih = item["x"], item["y"], item["w"], item["h"]
            for y in range(iy, min(self.height, iy + ih)):
                for x in range(ix, min(self.width, ix + iw)):
                    self.grid[y][x] = CELL_OBSTACLE

    def get_obstacle_grid(self) -> List[List[int]]:
        """Return 2D grid matrix for A* pathfinding."""
        return self.grid.tolist()

    def get_grid_matrix(self) -> List[List[int]]:
        """Return 2D grid array as python list of lists (0 = free, 1 = obstacle)."""
        return self.grid.tolist()

    def clear_room_objects(self) -> None:
        """Clear all active room objects before setting new detection objects."""
        self.objects = []
        self.save_environment()

    def add_object_to_room(self, name: str, icon: str, x: int, y: int, conf: float) -> None:
        """Add or update object in room layout at exact mapped grid coordinates."""
        clean_name = name.strip().capitalize()

        # Update existing or append
        for obj in self.objects:
            if obj["name"].lower() == clean_name.lower():
                obj["x"] = x
                obj["y"] = y
                obj["confidence"] = conf
                self.save_environment()
                return

        self.objects.append({"name": clean_name, "icon": icon, "x": x, "y": y, "confidence": conf})
        self.save_environment()

    def render_pygame_frame(
        self,
        robot_pos: Tuple[int, int],
        robot_orientation: float = 0.0,
        path: Optional[List[Tuple[int, int]]] = None,
        target_pos: Optional[Tuple[int, int]] = None
    ) -> Image.Image:
        """
        Render current room state using Pygame into a high-resolution PIL Image
        for Streamlit display.
        """
        def hex_to_rgb(h: str) -> Tuple[int, int, int]:
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        bg_color = hex_to_rgb(COLORS["background"])
        grid_color = hex_to_rgb(COLORS["grid_line"])
        wall_color = hex_to_rgb(COLORS["wall"])
        table_color = hex_to_rgb(COLORS["table"])
        shelf_color = hex_to_rgb(COLORS["shelf"])
        robot_color = hex_to_rgb(COLORS["robot"])
        robot_glow = hex_to_rgb(COLORS["robot_glow"])
        path_color = hex_to_rgb(COLORS["path"])
        target_color = hex_to_rgb(COLORS["target"])

        self.surface.fill(bg_color)

        # 1. Draw Grid lines
        for x in range(0, self.width * CELL_SIZE, CELL_SIZE):
            pygame.draw.line(self.surface, grid_color, (x, 0), (x, self.height * CELL_SIZE), 1)
        for y in range(0, self.height * CELL_SIZE, CELL_SIZE):
            pygame.draw.line(self.surface, grid_color, (0, y), (self.width * CELL_SIZE, y), 1)

        # 2. Draw Furniture & Obstacles
        for item in self.furniture:
            rect = (item["x"] * CELL_SIZE + 2, item["y"] * CELL_SIZE + 2, item["w"] * CELL_SIZE - 4, item["h"] * CELL_SIZE - 4)
            itype = item.get("type", "wall")
            col = wall_color if itype == "wall" else (shelf_color if itype == "shelf" else table_color)
            pygame.draw.rect(self.surface, col, rect, border_radius=4)
            # Label
            font = pygame.font.SysFont("Segoe UI", 12)
            lbl = font.render(item["name"], True, (200, 210, 225))
            self.surface.blit(lbl, (item["x"] * CELL_SIZE + 5, item["y"] * CELL_SIZE + 5))

        # 3. Draw Path (if present)
        if path and len(path) > 1:
            for idx in range(len(path) - 1):
                p1 = (path[idx][0] * CELL_SIZE + CELL_SIZE // 2, path[idx][1] * CELL_SIZE + CELL_SIZE // 2)
                p2 = (path[idx+1][0] * CELL_SIZE + CELL_SIZE // 2, path[idx+1][1] * CELL_SIZE + CELL_SIZE // 2)
                pygame.draw.line(self.surface, path_color, p1, p2, 4)
                pygame.draw.circle(self.surface, path_color, p1, 5)

        # 4. Draw Objects & Non-Overlapping Pill Badges
        # Group objects by grid coordinate to stack badges vertically when overlapping
        coord_stacks: Dict[Tuple[int, int], List[Dict[str, Any]]] = {}
        for obj in self.objects:
            pos_key = (obj["x"], obj["y"])
            if pos_key not in coord_stacks:
                coord_stacks[pos_key] = []
            coord_stacks[pos_key].append(obj)

        font_obj = pygame.font.SysFont("Segoe UI", 12, bold=True)

        for (ox, oy), stack in coord_stacks.items():
            cx = ox * CELL_SIZE + CELL_SIZE // 2
            cy = oy * CELL_SIZE + CELL_SIZE // 2

            # Draw base cyan dot marker for location
            pygame.draw.circle(self.surface, (2, 132, 199), (cx, cy), 12)
            pygame.draw.circle(self.surface, (255, 255, 255), (cx, cy), 14, 2)

            # Render pill text badges stacked vertically above the marker dot
            stack_offset_y = 20
            for idx, obj in enumerate(stack):
                name_str = obj['name']
                tw, th = font_obj.size(name_str)

                # Badge dimensions
                bx = cx - tw // 2 - 6
                by = cy - stack_offset_y - th - 6
                bw = tw + 12
                bh = th + 6

                # Draw pill container background & border
                badge_bg = (30, 41, 59)      # Slate dark background
                badge_border = (100, 122, 101)  # Sage border
                pygame.draw.rect(self.surface, badge_bg, (bx, by, bw, bh), border_radius=6)
                pygame.draw.rect(self.surface, badge_border, (bx, by, bw, bh), width=1, border_radius=6)

                # Render crisp white text inside pill badge
                txt = font_obj.render(name_str, True, (255, 255, 255))
                self.surface.blit(txt, (cx - tw // 2, by + 3))

                # Increment vertical offset for next stacked item
                stack_offset_y += (bh + 4)

        # 5. Draw Target Marker (if present)
        if target_pos:
            tx, ty = target_pos
            tcx = tx * CELL_SIZE + CELL_SIZE // 2
            tcy = ty * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(self.surface, target_color, (tcx, tcy), 18, 3)
            pygame.draw.circle(self.surface, target_color, (tcx, tcy), 6)

        # 6. Draw Robot
        rx, ry = robot_pos
        rcx = rx * CELL_SIZE + CELL_SIZE // 2
        rcy = ry * CELL_SIZE + CELL_SIZE // 2

        # Glow halo
        pygame.draw.circle(self.surface, robot_glow, (rcx, rcy), 18, 3)
        # Main robot body
        pygame.draw.circle(self.surface, robot_color, (rcx, rcy), 14)

        # Direction indicator line
        rad = np.radians(robot_orientation)
        dir_x = int(rcx + 18 * np.cos(rad))
        dir_y = int(rcy + 18 * np.sin(rad))
        pygame.draw.line(self.surface, (255, 255, 255), (rcx, rcy), (dir_x, dir_y), 3)

        # Convert Pygame Surface to PIL Image
        data = pygame.image.tostring(self.surface, "RGB")
        image = Image.frombytes("RGB", self.surface.get_size(), data)
        return image
