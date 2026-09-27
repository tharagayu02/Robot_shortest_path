"""
Spatial Memory Manager Module.
Provides high-level memory operations for object storage, spatial mapping,
location updates, and detection query routing to SQLite storage.
"""

from typing import List, Dict, Any, Optional, Tuple
from src.database import (
    save_detection_event,
    get_all_objects,
    get_object_by_name,
    get_all_detections,
    save_search_event,
    save_movement_event,
    get_performance_metrics
)


class SpatialMemorySystem:
    """Interface for managing virtual robot spatial memory and object locations."""

    def __init__(self):
        pass

    def remember_object(
        self,
        object_name: str,
        grid_x: int,
        grid_y: int,
        confidence: float,
        image_source: str = "simulation"
    ) -> Tuple[bool, str]:
        """
        Record or update an object's spatial location in memory.
        Enforces rule 8: Updates latest known location while preserving historical records.
        """
        clean_name = object_name.strip().capitalize()
        return save_detection_event(
            object_name=clean_name,
            x=grid_x,
            y=grid_y,
            confidence=confidence,
            image_source=image_source
        )

    def locate_object(self, object_name: str) -> Optional[Dict[str, Any]]:
        """
        Query memory for the latest known coordinates of a requested object.
        Returns dictionary with object properties or None if never detected.
        """
        return get_object_by_name(object_name)

    def get_memory_summary(self) -> List[Dict[str, Any]]:
        """Retrieve table of all currently remembered objects and their coordinates."""
        return get_all_objects()

    def get_detection_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve raw historical detection event logs."""
        return get_all_detections(limit=limit)

    def log_search(
        self,
        object_name: str,
        start_pos: Tuple[int, int],
        target_pos: Optional[Tuple[int, int]],
        distance: float,
        status: str
    ) -> int:
        """Record a search attempt in memory logs."""
        tx = target_pos[0] if target_pos else None
        ty = target_pos[1] if target_pos else None
        return save_search_event(
            object_name=object_name.capitalize(),
            start_x=start_pos[0],
            start_y=start_pos[1],
            target_x=tx,
            target_y=ty,
            path_distance=distance,
            status=status
        )

    def log_movement(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], distance: float, status: str = "completed") -> int:
        """Record robot movement event."""
        return save_movement_event(
            start_x=start_pos[0],
            start_y=start_pos[1],
            end_x=end_pos[0],
            end_y=end_pos[1],
            distance=distance,
            status=status
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Retrieve aggregated spatial memory performance metrics."""
        return get_performance_metrics()
