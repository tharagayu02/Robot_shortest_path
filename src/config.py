"""
Configuration settings for the Lost-Object Memory Robot system.
Includes grid dimensions, database paths, Sage Green & Ivory visual themes, and sample object metadata.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs" / "plots"
R_DIR = BASE_DIR / "R"
ASSETS_DIR = BASE_DIR / "assets" / "images"
UPLOADED_IMAGES_DIR = DATA_DIR / "uploaded_images"

# Ensure required directories exist
for folder in [DATA_DIR, MODELS_DIR, OUTPUTS_DIR, R_DIR, ASSETS_DIR, UPLOADED_IMAGES_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Database file
DB_PATH = BASE_DIR / "robot_memory.db"

# CSV Export Paths for R Analytics
DETECTIONS_CSV = DATA_DIR / "detections.csv"
SEARCHES_CSV = DATA_DIR / "searches.csv"
MOVEMENTS_CSV = DATA_DIR / "robot_movements.csv"

# Simulation Grid Settings
GRID_WIDTH = 24    # 24 cells wide
GRID_HEIGHT = 16   # 16 cells high
CELL_SIZE = 35     # Pixels per cell in Pygame canvas rendering

# Grid Cell Types
CELL_EMPTY = 0
CELL_OBSTACLE = 1
CELL_OBJECT = 2
CELL_ROBOT = 3
CELL_PATH = 4
CELL_TARGET = 5

# Color Palette (Sage Green & Ivory Theme)
COLORS = {
    "background": "#F5F2EB",      # Warm Ivory
    "panel": "#EAE5DA",           # Deep Cream / Ivory Card
    "grid_line": "#D8D2C2",       # Soft Ivory Gridline
    "wall": "#647A65",            # Primary Sage Green (Obstacles)
    "table": "#8A9F8B",           # Mid Sage Green
    "shelf": "#A8BBA9",           # Soft Light Sage
    "robot": "#3A4F3B",           # Deep Forest Sage (Robot Body)
    "robot_glow": "#647A65",      # Sage Green Glow Ring
    "object": "#0284C7",          # Ocean Cyan Object Marker
    "target": "#D97706",          # Warm Clay Amber Target Marker
    "path": "#4F6E56",            # Deep Sage Path Line
    "visited": "#D6DFD5",         # Soft Sage Tint
    "text": "#1E291E",            # Deep Charcoal Forest (High Contrast)
    "text_muted": "#526353"       # Muted Sage Text
}

# COCO Pretrained Model Config
YOLO_MODEL_NAME = "yolov8n.pt"  # Nano model, light on CPU
CONFIDENCE_THRESHOLD = 0.25     # Flexible detection confidence filter for uploaded room photos

# Supported COCO Objects of Interest
TRACKED_OBJECT_CLASSES = [
    "bottle", "book", "chair", "laptop", "cell phone", "mouse", 
    "keyboard", "cup", "backpack", "umbrella", "clock", "scissors", "teddy bear",
    "tv", "couch", "bed", "dining table", "remote", "refrigerator", "vase"
]
