# R Analysis Module for Lost-Object Memory Robot
# Summarizes spatial memory, object detection frequencies, and path planning performance metrics.

suppressPackageStartupMessages({
  if (!require("dplyr", quietly = TRUE)) install.packages("dplyr", repos = "https://cloud.r-project.org")
  if (!require("readr", quietly = TRUE)) install.packages("readr", repos = "https://cloud.r-project.org")
})

library(dplyr)
library(readr)

analyze_robot_data <- function(data_dir = "data") {
  det_path <- file.path(data_dir, "detections.csv")
  search_path <- file.path(data_dir, "searches.csv")
  move_path <- file.path(data_dir, "robot_movements.csv")
  
  if (file.exists(det_path)) {
    detections <- read_csv(det_path, show_col_types = FALSE)
    cat("\n--- OBJECT DETECTION SUMMARY ---\n")
    print(detections %>% group_by(object_name) %>% summarize(
      count = n(),
      avg_confidence = mean(confidence, na.rm = TRUE)
    ))
  }
  
  if (file.exists(search_path)) {
    searches <- read_csv(search_path, show_col_types = FALSE)
    cat("\n--- SEARCH EFFICIENCY SUMMARY ---\n")
    print(searches %>% group_by(status) %>% summarize(
      total_queries = n(),
      mean_distance = mean(path_distance, na.rm = TRUE)
    ))
  }
}

# Run analysis if script is called directly
if (sys.nframe() == 0) {
  analyze_robot_data()
}
