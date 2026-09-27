"""
Sample Data & Demo Mode Utility.
Generates synthetic/sample dataset images (bottle, laptop, book, chair, keys)
and seeds initial spatial memory & search logs for instant demonstration.
"""

import os
import random
import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from src.config import ASSETS_DIR
from src.database import init_db, save_detection_event, save_search_event, save_movement_event, clear_database


def generate_sample_images() -> None:
    """Generate sample images representing objects from COCO categories."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    samples = [
        ("sample_bottle.jpg", "Water Bottle on Table", "#0F172A", "#06B6D4", "BOTTLE"),
        ("sample_laptop.jpg", "Laptop Desk Workspace", "#0F172A", "#38BDF8", "LAPTOP"),
        ("sample_book.jpg", "Textbook on Library Shelf", "#0F172A", "#EC4899", "BOOK"),
        ("sample_chair.jpg", "Office Ergonomic Chair", "#0F172A", "#10B981", "CHAIR"),
        ("sample_keys.jpg", "Keychain on Living Table", "#0F172A", "#F59E0B", "KEYS")
    ]

    for fname, title, bg_hex, fg_hex, label in samples:
        fpath = ASSETS_DIR / fname
        if not fpath.exists():
            img = Image.new("RGB", (640, 480), color=bg_hex)
            draw = ImageDraw.Draw(img)

            # Draw decorative backdrop container
            draw.rectangle([60, 60, 580, 420], fill="#1E293B", outline=fg_hex, width=3)
            draw.rectangle([120, 120, 520, 360], fill=bg_hex, outline=fg_hex, width=2)

            # Center text banner
            draw.text((200, 180), title, fill="#F8FAFC")
            draw.text((240, 240), f"[ COCO DATASET OBJECT: {label} ]", fill=fg_hex)
            draw.text((180, 300), "Detected by YOLOv8 Vision Model", fill="#94A3B8")

            img.save(fpath, "JPEG")


def seed_demo_mode_data() -> None:
    """Populate database with sample detections, spatial memory, and search histories."""
    init_db()
    clear_database()
    generate_sample_images()

    # Pre-populate spatial memory for Demo Mode objects
    objects_data = [
        ("Bottle", 18, 3, 94.2, "sample_bottle.jpg"),
        ("Book", 5, 4, 88.7, "sample_book.jpg"),
        ("Chair", 5, 12, 91.4, "sample_chair.jpg"),
        ("Laptop", 17, 11, 96.0, "sample_laptop.jpg"),
        ("Keys", 11, 8, 92.5, "sample_keys.jpg")
    ]

    for name, x, y, conf, img_src in objects_data:
        save_detection_event(name, x, y, conf, image_source=img_src)

    # Seed historical searches
    searches = [
        ("Keys", 2, 2, 11, 8, 14.5, "Found"),
        ("Bottle", 2, 2, 18, 3, 19.8, "Found"),
        ("Laptop", 2, 2, 17, 11, 21.2, "Found"),
        ("Umbrella", 2, 2, None, None, 0.0, "Not Found"),
        ("Book", 2, 2, 5, 4, 7.8, "Found")
    ]

    for name, sx, sy, tx, ty, dist, status in searches:
        save_search_event(name, sx, sy, tx, ty, dist, status)

    # Seed movement history
    movements = [
        (2, 2, 11, 8, 14.5, "completed"),
        (11, 8, 18, 3, 9.2, "completed"),
        (18, 3, 17, 11, 8.5, "completed"),
        (17, 11, 5, 4, 16.4, "completed")
    ]

    for sx, sy, ex, ey, dist, status in movements:
        save_movement_event(sx, sy, ex, ey, dist, status)
