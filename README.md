# 🤖 Lost-Object Memory Robot

### An AI-Based Virtual Robot for Object Detection, Spatial Memory and Autonomous Path Planning

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg)](https://github.com/ultralytics/ultralytics)
[![R Analytics](https://img.shields.io/badge/R-ggplot2-276DC3.svg)](https://www.r-project.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 1. Problem Statement
Humans frequently misplace household or office items such as keys, water bottles, textbooks, laptops, or eyeglasses. Traditional robotic search algorithms either rely on exhaustive random room exploration or require expensive continuous mapping hardware. There is a need for a software-only, data-driven virtual robot capable of observing objects, maintaining persistent spatial memory of their locations, and dynamically planning optimal routes when requested by a user.

## 2. Proposed Solution
The **Lost-Object Memory Robot** is a complete, software-only virtual robotics simulation system. It integrates computer vision (**YOLOv8**), persistent spatial memory (**SQLite**), optimal pathfinding (**A\* Algorithm from scratch**), interactive 2D room visualization (**Pygame / Canvas**), and statistical reporting (**R ggplot2**). 

The system operates entirely digitally without requiring physical hardware (Arduino, Raspberry Pi, motors, or physical camera sensors).

---

## 3. Key Features

- 📸 **Object Detection & Vision**: Detects indoor objects from uploaded images or sample COCO dataset images using YOLOv8 nano CPU model.
- 🧠 **Persistent Spatial Memory**: SQLite spatial memory ledger tracking latest known object coordinates `(last_x, last_y)`, timestamps, and confidence scores without deleting historical observation logs.
- 🗺️ **2D Interactive Simulation Grid**: 24x16 room matrix featuring walls, tables, chairs, shelves, robot, target markers, and animated step execution.
- 🔍 **A\* Path Planning from Scratch**: Optimal 8-directional shortest path algorithm avoiding obstacles and calculating path length and step count.
- 📊 **R ggplot2 Analytics Pipeline**: Generates 6 statistical plots analyzing detection frequency, search distance trends, search success rate, trajectory distances, and spatial memory maps.
- ⚡ **Demo Mode**: One-click seeding of sample COCO dataset observations and search query logs.

---

## 4. System Architecture Workflow

```text
               EXTERNAL REAL DATASET (COCO)
                            ↓
                    Sample/User Images
                            ↓
                     YOLOv8 Detection
                            ↓
                    Detected Objects
                            ↓
                  SQLite Spatial Memory
                            ↓
         ┌──────────────────┴──────────────────┐
         ↓                                     ↓
  Latest Location                         History Logs
         ↓                                     ↓
    User Search                           R Analytics
         ↓                                     ↓
    A* Planning                          Statistical
         ↓                                  Plots
   Virtual Robot
         ↓
  Navigate to Target
```

---

## 5. Technology Stack

- **Core & Simulation**: Python 3.11+, Pygame, PIL, NumPy, Pandas
- **Computer Vision**: Ultralytics YOLOv8 (Nano model `yolov8n.pt`), OpenCV Headless
- **Robot Intelligence & Pathfinding**: A\* Search Algorithm implemented from scratch
- **Database**: SQLite (`robot_memory.db`)
- **Web Interface**: Streamlit
- **Data Analytics**: R (`ggplot2`, `dplyr`, `readr`) with Python Matplotlib fallback engine

---

## 6. How Component Systems Work

### A. How Object Memory Works
Whenever an object is detected:
1. The system checks if the object exists in the `objects` SQLite table.
2. If absent, it creates a new spatial memory entry with coordinates and timestamps.
3. If present, it updates `last_x`, `last_y`, `confidence`, and `last_seen`.
4. The event is simultaneously appended to the `detections` historical table, preserving complete timeline history without deleting past entries.

### B. How A\* Path Planning Works
Implemented from scratch in `src/pathfinding.py`:
- **Nodes & Min-Heap**: Uses Python `heapq` priority queue ordering nodes by $f(n) = g(n) + h(n)$.
- **Cost Function**: Straight cell move = 1.0, diagonal move = 1.414.
- **Heuristic**: Euclidean distance $h(n) = \sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$.
- **Obstacle Avoidance**: Validates grid bounds and checks wall matrix before neighbor expansion.

### C. How YOLO Works in the Project
The `ObjectDetector` module (`src/object_detection.py`) passes BGR image frames to YOLOv8. It filters boxes exceeding confidence threshold ($\ge 40\%$), draws colored bounding boxes, labels class names, and extracts grid location metrics.

---

## 7. Project Structure

```text
lost-object-memory-robot/
│
├── app.py                      # Main Streamlit application entrypoint & router
├── requirements.txt            # Python dependencies
├── README.md                   # System documentation
├── .gitignore                  # Git exclusions
├── .env.example                # Configuration environment variables
├── Dockerfile                  # Containerized deployment specification
│
├── src/                        # Core Python Engine Modules
│   ├── __init__.py
│   ├── robot.py                # Virtual Robot Agent class
│   ├── simulation.py           # 2D Room Grid & Renderer Engine
│   ├── pathfinding.py          # Scratch A* Pathfinding Algorithm
│   ├── object_detection.py     # YOLO Object Detector & Bounding Box drawer
│   ├── memory.py               # Spatial Memory System Interface
│   ├── database.py             # SQLite DB manager & schema migrations
│   ├── analytics.py            # SQLite exporter & R/Python plotting engine
│   ├── sample_data.py          # Demo Mode dataset generator
│   └── config.py               # Application configuration settings
│
├── pages/                      # Streamlit Page Modules
│   ├── 1_Home.py               # Home Overview Dashboard
│   ├── 2_Simulation.py         # 2D Room Simulation Environment
│   ├── 3_Detection.py          # Computer Vision & Detection Interface
│   ├── 4_Memory.py             # Spatial Memory System Ledger
│   ├── 5_Search.py            # Object Search & Path Execution
│   ├── 6_History.py            # Search & Movement Audit Logs
│   ├── 7_Analytics.py          # R Statistical Analytics & ggplot2 Plots
│   └── 8_About.py              # System Architecture & Algorithm Details
│
├── data/                       # CSV Data Exports & Layout JSON
│   ├── sample_environment.json # 2D Room Layout Definition
│   ├── detections.csv          # Exported detection logs
│   ├── searches.csv            # Exported search logs
│   └── robot_movements.csv     # Exported movement logs
│
├── models/                     # Model Documentation & Weights
│   └── README.md
│
├── R/                          # R Analytics Module
│   ├── analysis.R              # R Data Aggregation script
│   ├── plots.R                 # R ggplot2 Plotting script
│   └── README.md               # R Module documentation
│
├── outputs/
│   └── plots/                  # Generated PNG statistical visualizations
│
├── tests/                      # Automated Unit Tests
│   ├── test_pathfinding.py
│   ├── test_memory.py
│   └── test_detection.py
│
└── assets/                     # COCO Sample Images & Icons
    └── images/
```

---

## 8. Installation & Local Setup

### Prerequisites
- Python 3.11 or higher
- R (Optional, for running native R `ggplot2` scripts; Python fallback included)

### Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/lost-object-memory-robot.git
   cd lost-object-memory-robot
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Automated Unit Tests**:
   ```bash
   python -m unittest discover tests
   ```

4. **Launch Application**:
   ```bash
   streamlit run app.py
   ```
   Open your browser to `http://localhost:8501`.

---

## 9. Running Analytics with R

To run R analytics manually via CLI:
```bash
Rscript R/analysis.R
Rscript R/plots.R
```
Visualizations will be written to `outputs/plots/`.

---

## 10. Deployment

### Streamlit Community Cloud
Deploy directly from GitHub repository targeting `app.py`. The application includes headless Pygame rendering and automatic Python Matplotlib fallbacks for cloud environments.

### Docker Deployment
Build and launch containerized application:
```bash
docker build -t lost-object-memory-robot .
docker run -p 8501:8501 lost-object-memory-robot
```

---

## 11. Limitations & Future Improvements

- **Grid Resolution**: Currently configured to 24x16 grid; can be scaled to 3D voxel grids in future revisions.
- **Dynamic Obstacles**: Future work could incorporate dynamic moving obstacles using D\* Lite pathfinding.
- **Physical Hardware Integration**: Can be extended to ROS2 / TurtleBot3 physical hardware nodes via WebSocket bridge.
