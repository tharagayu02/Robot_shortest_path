"""
A* Pathfinding Algorithm implemented from scratch.
Computes optimal 2D grid routes for autonomous robot navigation,
avoiding walls and obstacles.
"""

import heapq
import time
import math
from typing import List, Tuple, Dict, Optional, Set, Any


class Node:
    """Represents a cell node in the A* search tree."""
    def __init__(self, x: int, y: int, g_cost: float = float('inf'), h_cost: float = 0.0, parent: Optional['Node'] = None):
        self.x = x
        self.y = y
        self.g_cost = g_cost  # Cost from start to current node
        self.h_cost = h_cost  # Estimated cost from current node to goal
        self.f_cost = g_cost + h_cost  # Total estimated cost
        self.parent = parent

    def __lt__(self, other: 'Node') -> bool:
        return self.f_cost < other.f_cost

    @property
    def pos(self) -> Tuple[int, int]:
        return (self.x, self.y)


def heuristic(p1: Tuple[int, int], p2: Tuple[int, int], method: str = "euclidean") -> float:
    """Calculate heuristic estimate between two coordinates."""
    dx = abs(p1[0] - p2[0])
    dy = abs(p1[1] - p2[1])
    if method == "octile":
        # Octile distance for 8-directional movement
        return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)
    elif method == "manhattan":
        return dx + dy
    else:
        # Euclidean distance
        return math.sqrt(dx * dx + dy * dy)


def astar_search(
    grid: List[List[int]],
    start: Tuple[int, int],
    goal: Tuple[int, int],
    allow_diagonal: bool = True
) -> Dict[str, Any]:
    """
    Perform A* path planning on a 2D grid from scratch.

    :param grid: 2D matrix where 0 = free space, 1 = obstacle
    :param start: (x, y) start coordinate
    :param goal: (x, y) target goal coordinate
    :param allow_diagonal: Whether 8-directional movement is permitted
    :return: Dictionary with path, path_length, num_steps, planning_time_ms, success
    """
    start_time = time.perf_counter()
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0

    sx, sy = start
    gx, gy = goal

    # Validation
    if not (0 <= sx < width and 0 <= sy < height):
        return {"path": [], "path_length": 0.0, "num_steps": 0, "planning_time_ms": 0.0, "success": False, "error": "Start out of bounds"}

    if not (0 <= gx < width and 0 <= gy < height):
        return {"path": [], "path_length": 0.0, "num_steps": 0, "planning_time_ms": 0.0, "success": False, "error": "Goal out of bounds"}

    # If goal cell is an obstacle, find nearest adjacent free cell
    if grid[gy][gx] == 1:
        neighbors = get_neighbors(gx, gy, width, height, grid, allow_diagonal=False)
        if neighbors:
            gx, gy = neighbors[0][0], neighbors[0][1]
        else:
            return {"path": [], "path_length": 0.0, "num_steps": 0, "planning_time_ms": 0.0, "success": False, "error": "Goal blocked"}

    # Directions: (dx, dy, step_cost)
    if allow_diagonal:
        movements = [
            (0, -1, 1.0), (0, 1, 1.0), (-1, 0, 1.0), (1, 0, 1.0),
            (-1, -1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (1, 1, 1.414)
        ]
    else:
        movements = [(0, -1, 1.0), (0, 1, 1.0), (-1, 0, 1.0), (1, 0, 1.0)]

    open_set: List[Node] = []
    open_dict: Dict[Tuple[int, int], Node] = {}
    closed_set: Set[Tuple[int, int]] = set()

    start_node = Node(sx, sy, g_cost=0.0, h_cost=heuristic((sx, sy), (gx, gy)))
    heapq.heappush(open_set, start_node)
    open_dict[(sx, sy)] = start_node

    found_node: Optional[Node] = None

    while open_set:
        current = heapq.heappop(open_set)
        curr_pos = current.pos

        if curr_pos in open_dict:
            del open_dict[curr_pos]

        if curr_pos == (gx, gy):
            found_node = current
            break

        closed_set.add(curr_pos)

        for dx, dy, cost in movements:
            nx, ny = current.x + dx, current.y + dy

            # Bounds check
            if not (0 <= nx < width and 0 <= ny < height):
                continue

            # Obstacle check
            if grid[ny][nx] == 1:
                continue

            # Prevent corner cutting for diagonal moves
            if dx != 0 and dy != 0:
                if grid[current.y][current.x + dx] == 1 or grid[current.y + dy][current.x] == 1:
                    continue

            neighbor_pos = (nx, ny)
            if neighbor_pos in closed_set:
                continue

            new_g = current.g_cost + cost
            existing_node = open_dict.get(neighbor_pos)

            if existing_node is None:
                h = heuristic(neighbor_pos, (gx, gy))
                neighbor_node = Node(nx, ny, g_cost=new_g, h_cost=h, parent=current)
                heapq.heappush(open_set, neighbor_node)
                open_dict[neighbor_pos] = neighbor_node
            elif new_g < existing_node.g_cost:
                existing_node.g_cost = new_g
                existing_node.f_cost = new_g + existing_node.h_cost
                existing_node.parent = current
                heapq.heapify(open_set)  # Re-heapify after update

    planning_time = (time.perf_counter() - start_time) * 1000.0  # in ms

    if found_node is None:
        return {
            "path": [],
            "path_length": 0.0,
            "num_steps": 0,
            "planning_time_ms": round(planning_time, 3),
            "success": False,
            "error": "No reachable path found"
        }

    # Reconstruct path from goal to start
    raw_path: List[Tuple[int, int]] = []
    curr: Optional[Node] = found_node
    total_length = found_node.g_cost

    while curr:
        raw_path.append(curr.pos)
        curr = curr.parent

    raw_path.reverse()

    return {
        "path": raw_path,
        "path_length": round(total_length, 2),
        "num_steps": len(raw_path),
        "planning_time_ms": round(planning_time, 3),
        "success": True,
        "error": None
    }


def get_neighbors(x: int, y: int, width: int, height: int, grid: List[List[int]], allow_diagonal: bool = False) -> List[Tuple[int, int]]:
    """Return adjacent unblocked neighbor coordinates for a given cell."""
    res = []
    dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    if allow_diagonal:
        dirs += [(-1, -1), (1, -1), (-1, 1), (1, 1)]

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height and grid[ny][nx] == 0:
            res.append((nx, ny))
    return res
