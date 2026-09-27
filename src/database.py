"""
Database Management Module using SQLite.
Handles persistence for object locations, spatial memory updates, detection logs,
uploaded room images, robot movements, and search attempt histories.
"""

import sqlite3
import datetime
from typing import List, Dict, Any, Optional, Tuple
from src.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    """Establish and return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize SQLite database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Table 1: Primary Spatial Memory of Objects (Latest Known Position)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS objects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        object_name TEXT UNIQUE NOT NULL,
        first_seen TEXT NOT NULL,
        last_seen TEXT NOT NULL,
        last_x INTEGER NOT NULL,
        last_y INTEGER NOT NULL,
        confidence REAL NOT NULL,
        image_source TEXT
    );
    """)

    # Table 2: Complete Historical Detections Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        object_name TEXT NOT NULL,
        x INTEGER NOT NULL,
        y INTEGER NOT NULL,
        confidence REAL NOT NULL,
        image_source TEXT
    );
    """)

    # Table 3: Robot Movement History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS robot_movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        start_x INTEGER NOT NULL,
        start_y INTEGER NOT NULL,
        end_x INTEGER NOT NULL,
        end_y INTEGER NOT NULL,
        distance REAL NOT NULL,
        status TEXT NOT NULL
    );
    """)

    # Table 4: Object Search Query & Path Planning Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        object_name TEXT NOT NULL,
        start_x INTEGER NOT NULL,
        start_y INTEGER NOT NULL,
        target_x INTEGER,
        target_y INTEGER,
        path_distance REAL NOT NULL,
        status TEXT NOT NULL
    );
    """)

    # Table 5: Uploaded Room Images & Environment Registry
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS uploaded_rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        room_name TEXT NOT NULL,
        image_filename TEXT NOT NULL,
        image_path TEXT NOT NULL,
        num_objects INTEGER NOT NULL
    );
    """)

    conn.commit()
    conn.close()


def save_uploaded_room(room_name: str, image_filename: str, image_path: str, num_objects: int) -> int:
    """Register an uploaded room image in SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO uploaded_rooms (timestamp, room_name, image_filename, image_path, num_objects)
    VALUES (?, ?, ?, ?, ?)
    """, (now_str, room_name, image_filename, image_path, num_objects))

    room_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return room_id


def get_all_rooms() -> List[Dict[str, Any]]:
    """Retrieve list of registered room images."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM uploaded_rooms ORDER BY timestamp DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def save_detection_event(
    object_name: str,
    x: int,
    y: int,
    confidence: float,
    image_source: str = "simulation"
) -> Tuple[bool, str]:
    """
    Record an object detection event.
    Updates the main `objects` table (latest position) while appending
    to the `detections` historical ledger.
    """
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Insert into historical detections table
    cursor.execute("""
    INSERT INTO detections (timestamp, object_name, x, y, confidence, image_source)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (now_str, object_name, x, y, confidence, image_source))

    # 2. Check if object already exists in primary memory
    cursor.execute("SELECT id, first_seen FROM objects WHERE object_name = ?", (object_name,))
    row = cursor.fetchone()

    if row is None:
        # First time seeing object
        cursor.execute("""
        INSERT INTO objects (object_name, first_seen, last_seen, last_x, last_y, confidence, image_source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (object_name, now_str, now_str, x, y, confidence, image_source))
        status_msg = f"New object memory created: {object_name} at ({x}, {y})"
    else:
        # Update existing object location & timestamp
        cursor.execute("""
        UPDATE objects
        SET last_seen = ?, last_x = ?, last_y = ?, confidence = ?, image_source = ?
        WHERE object_name = ?
        """, (now_str, x, y, confidence, image_source, object_name))
        status_msg = f"Updated memory position for {object_name} to ({x}, {y})"

    conn.commit()
    conn.close()
    return True, status_msg


def save_search_event(
    object_name: str,
    start_x: int,
    start_y: int,
    target_x: Optional[int],
    target_y: Optional[int],
    path_distance: float,
    status: str
) -> int:
    """Record a user search attempt and path planning result."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO searches (timestamp, object_name, start_x, start_y, target_x, target_y, path_distance, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (now_str, object_name, start_x, start_y, target_x, target_y, path_distance, status))

    search_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return search_id


def save_movement_event(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    distance: float,
    status: str = "completed"
) -> int:
    """Record a robot travel execution."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO robot_movements (timestamp, start_x, start_y, end_x, end_y, distance, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (now_str, start_x, start_y, end_x, end_y, distance, status))

    move_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return move_id


def get_all_objects() -> List[Dict[str, Any]]:
    """Retrieve all remembered objects with their latest coordinates."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM objects ORDER BY last_seen DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_object_by_name(object_name: str) -> Optional[Dict[str, Any]]:
    """Query object spatial memory by name (case-insensitive)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM objects WHERE LOWER(object_name) = LOWER(?)", (object_name.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_detections(limit: int = 200) -> List[Dict[str, Any]]:
    """Retrieve historical detection logs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detections ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_all_searches(limit: int = 200) -> List[Dict[str, Any]]:
    """Retrieve search query history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM searches ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_all_movements(limit: int = 200) -> List[Dict[str, Any]]:
    """Retrieve robot movement history logs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM robot_movements ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_performance_metrics() -> Dict[str, Any]:
    """Calculate key runtime metrics from empirical database records."""
    conn = get_connection()
    cursor = conn.cursor()

    # Detections metrics
    cursor.execute("SELECT COUNT(*), AVG(confidence), COUNT(DISTINCT object_name) FROM detections")
    det_count, avg_conf, unique_objs = cursor.fetchone()

    # Searches metrics
    cursor.execute("SELECT COUNT(*) FROM searches")
    total_searches = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM searches WHERE status = 'Found'")
    successful_searches = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM searches WHERE status = 'Not Found' OR status = 'No Path'")
    unsuccessful_searches = cursor.fetchone()[0] or 0

    cursor.execute("SELECT AVG(path_distance), MIN(path_distance), MAX(path_distance) FROM searches WHERE status = 'Found' AND path_distance > 0")
    avg_dist, min_dist, max_dist = cursor.fetchone()

    # Movement metrics
    cursor.execute("SELECT SUM(distance), COUNT(*) FROM robot_movements")
    total_move_dist, total_moves = cursor.fetchone()

    conn.close()

    success_rate = (successful_searches / total_searches * 100.0) if total_searches > 0 else 0.0

    return {
        "total_detections": det_count or 0,
        "avg_confidence": round(avg_conf or 0.0, 3),
        "unique_objects": unique_objs or 0,
        "total_searches": total_searches,
        "successful_searches": successful_searches,
        "unsuccessful_searches": unsuccessful_searches,
        "search_success_rate": round(success_rate, 1),
        "avg_path_length": round(avg_dist or 0.0, 1),
        "min_path_length": round(min_dist or 0.0, 1),
        "max_path_length": round(max_dist or 0.0, 1),
        "total_movement_distance": round(total_move_dist or 0.0, 1),
        "total_movements": total_moves or 0
    }


def clear_database() -> None:
    """Reset database tables for clean testing."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM objects")
    cursor.execute("DELETE FROM detections")
    cursor.execute("DELETE FROM searches")
    cursor.execute("DELETE FROM robot_movements")
    cursor.execute("DELETE FROM uploaded_rooms")
    conn.commit()
    conn.close()
