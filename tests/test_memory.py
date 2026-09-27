"""
Unit tests for Spatial Memory system and SQLite persistence.
"""

import unittest
import sqlite3
from src.database import init_db, clear_database, save_detection_event, get_object_by_name, get_all_detections


class TestSpatialMemory(unittest.TestCase):

    def setUp(self):
        init_db()
        clear_database()

    def tearDown(self):
        clear_database()

    def test_remember_new_object(self):
        success, msg = save_detection_event("Laptop", 15, 10, 95.5, "test_img.jpg")
        self.assertTrue(success)

        obj = get_object_by_name("Laptop")
        self.assertIsNotNone(obj)
        self.assertEqual(obj["last_x"], 15)
        self.assertEqual(obj["last_y"], 10)
        self.assertEqual(obj["confidence"], 95.5)

    def test_update_object_location_preserves_history(self):
        # First observation
        save_detection_event("Keys", 4, 7, 85.0, "img1.jpg")
        # Second observation at different location
        save_detection_event("Keys", 8, 3, 92.0, "img2.jpg")

        # Check primary memory (latest location)
        obj = get_object_by_name("Keys")
        self.assertEqual(obj["last_x"], 8)
        self.assertEqual(obj["last_y"], 3)

        # Check historical detections table (2 entries preserved)
        history = get_all_detections()
        keys_history = [d for d in history if d["object_name"].lower() == "keys"]
        self.assertEqual(len(keys_history), 2)


if __name__ == "__main__":
    unittest.main()
