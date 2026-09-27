# R Analytics Module - Lost-Object Memory Robot

This directory contains the R data processing and statistical visualization pipeline for the Lost-Object Memory Robot project.

## Scripts

1. `analysis.R`: Performs data aggregation and generates numerical summaries of object detection counts, average confidence, and search distances.
2. `plots.R`: Uses `ggplot2`, `dplyr`, and `readr` to render 6 high-resolution statistical visualizations stored in `outputs/plots/`.

## Inputs

The scripts read CSV data exported by Python from the SQLite database:
- `data/detections.csv`: Historical object detections
- `data/searches.csv`: User search queries & path planning results
- `data/robot_movements.csv`: Robot trajectory distances

## Output Visualizations

The generated plots include:
1. `plot1_detection_freq.png`: Object detection frequency
2. `plot2_detection_timeline.png`: Detection confidence over time
3. `plot3_avg_search_distance.png`: Average search distance by object
4. `plot4_search_success_rate.png`: Successful vs unsuccessful search attempts
5. `plot5_movement_distance.png`: Robot movement distance over time
6. `plot6_object_location_history.png`: 2D spatial memory map of detected objects

## How to Run

### Automated (via Streamlit Python Application)
The Streamlit web application automatically exports SQLite data to CSV and invokes `Rscript R/plots.R`.

### Manual CLI Execution
```bash
Rscript R/analysis.R
Rscript R/plots.R
```
