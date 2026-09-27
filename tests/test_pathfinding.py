"""
Unit tests for A* Pathfinding algorithm implementation.
"""

import unittest
from src.pathfinding import astar_search, heuristic


class TestPathfinding(unittest.TestCase):

    def setUp(self):
        # 5x5 grid with obstacle wall in column 2
        self.grid = [
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]

    def test_heuristic_calculation(self):
        h_val = heuristic((0, 0), (3, 4), method="euclidean")
        self.assertEqual(h_val, 5.0)

    def test_clear_path(self):
        clear_grid = [[0]*5 for _ in range(5)]
        result = astar_search(clear_grid, (0, 0), (4, 4), allow_diagonal=True)
        self.assertTrue(result["success"])
        self.assertGreater(len(result["path"]), 0)
        self.assertEqual(result["path"][0], (0, 0))
        self.assertEqual(result["path"][-1], (4, 4))

    def test_obstacle_avoidance(self):
        result = astar_search(self.grid, (0, 0), (4, 0), allow_diagonal=True)
        self.assertTrue(result["success"])
        # Ensure path goes around obstacle wall at y=3 or y=4
        for x, y in result["path"]:
            self.assertNotEqual(self.grid[y][x], 1, f"Path passed through obstacle at ({x}, {y})")

    def test_unreachable_target(self):
        blocked_grid = [
            [0, 1, 0],
            [1, 1, 0],
            [0, 0, 0]
        ]
        result = astar_search(blocked_grid, (0, 0), (2, 2))
        self.assertFalse(result["success"])


if __name__ == "__main__":
    unittest.main()
