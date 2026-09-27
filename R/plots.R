# ggplot2 Plotting Module for Lost-Object Memory Robot
# Generates 6 Sage Green & Ivory statistical visualizations from SQLite exported CSV datasets.

suppressPackageStartupMessages({
  if (!require("ggplot2", quietly = TRUE)) install.packages("ggplot2", repos = "https://cloud.r-project.org")
  if (!require("dplyr", quietly = TRUE)) install.packages("dplyr", repos = "https://cloud.r-project.org")
  if (!require("readr", quietly = TRUE)) install.packages("readr", repos = "https://cloud.r-project.org")
})

library(ggplot2)
library(dplyr)
library(readr)

# Directory Setup
data_dir <- "data"
out_dir <- file.path("outputs", "plots")
if (!dir.exists(out_dir)) dir.create(out_dir, recursive = TRUE)

# Custom Sage Green & Ivory Theme
theme_sage_ivory <- function() {
  theme_minimal(base_size = 13) +
    theme(
      plot.background = element_rect(fill = "#F5F2EB", color = NA),
      panel.background = element_rect(fill = "#EAE5DA", color = NA),
      panel.grid.major = element_line(color = "#D8D2C2", size = 0.5),
      panel.grid.minor = element_blank(),
      text = element_text(color = "#1E291E"),
      axis.text = element_text(color = "#3C4E3D"),
      axis.title = element_text(color = "#4F6E56", face = "bold"),
      plot.title = element_text(color = "#3A4F3B", size = 16, face = "bold", hjust = 0.5),
      plot.subtitle = element_text(color = "#526353", size = 11, hjust = 0.5),
      legend.background = element_rect(fill = "#F5F2EB", color = NA),
      legend.text = element_text(color = "#1E291E")
    )
}

# -------------------------------------------------------------
# Plot 1: Object Detection Frequency
# -------------------------------------------------------------
det_file <- file.path(data_dir, "detections.csv")
if (file.exists(det_file)) {
  detections <- read_csv(det_file, show_col_types = FALSE)
  
  if (nrow(detections) > 0) {
    p1 <- detections %>%
      count(object_name) %>%
      ggplot(aes(x = reorder(object_name, n), y = n, fill = object_name)) +
      geom_col(show.legend = FALSE, width = 0.6) +
      coord_flip() +
      scale_fill_manual(values = c("#4F6E56", "#647A65", "#8A9F8B", "#0284C7", "#D97706")) +
      labs(
        title = "Object Detection Frequency",
        subtitle = "Total observations recorded by virtual vision system",
        x = "Object Name",
        y = "Detection Count"
      ) +
      theme_sage_ivory()
    
    ggsave(file.path(out_dir, "plot1_detection_freq.png"), p1, width = 8, height = 5, dpi = 150)
  }
}

# -------------------------------------------------------------
# Plot 2: Detection Count Over Time
# -------------------------------------------------------------
if (file.exists(det_file)) {
  detections <- read_csv(det_file, show_col_types = FALSE)
  if (nrow(detections) > 0) {
    p2 <- detections %>%
      mutate(time_idx = row_number()) %>%
      ggplot(aes(x = time_idx, y = confidence, color = object_name)) +
      geom_line(size = 1.2) +
      geom_point(size = 3) +
      scale_color_manual(values = c("#3A4F3B", "#647A65", "#8A9F8B", "#0284C7", "#D97706")) +
      labs(
        title = "Object Detection Timeline & Confidence",
        subtitle = "Confidence trend over sequential camera observations",
        x = "Observation Index",
        y = "Confidence (%)",
        color = "Object"
      ) +
      theme_sage_ivory()
    
    ggsave(file.path(out_dir, "plot2_detection_timeline.png"), p2, width = 8, height = 5, dpi = 150)
  }
}

# -------------------------------------------------------------
# Plot 3: Average Search Distance by Object
# -------------------------------------------------------------
search_file <- file.path(data_dir, "searches.csv")
if (file.exists(search_file)) {
  searches <- read_csv(search_file, show_col_types = FALSE)
  if (nrow(searches) > 0) {
    p3 <- searches %>%
      filter(status == "Found") %>%
      group_by(object_name) %>%
      summarize(avg_dist = mean(path_distance, na.rm = TRUE)) %>%
      ggplot(aes(x = object_name, y = avg_dist, fill = object_name)) +
      geom_bar(stat = "identity", show.legend = FALSE, width = 0.5) +
      scale_fill_manual(values = c("#4F6E56", "#647A65", "#8A9F8B", "#0284C7", "#D97706")) +
      labs(
        title = "Average Search Path Distance by Object",
        subtitle = "A* grid path length (units) traversed to target object",
        x = "Object Name",
        y = "Average Grid Distance"
      ) +
      theme_sage_ivory()
    
    ggsave(file.path(out_dir, "plot3_avg_search_distance.png"), p3, width = 8, height = 5, dpi = 150)
  }
}

# -------------------------------------------------------------
# Plot 4: Search Success Rate (Found vs Not Found)
# -------------------------------------------------------------
if (file.exists(search_file)) {
  searches <- read_csv(search_file, show_col_types = FALSE)
  if (nrow(searches) > 0) {
    p4 <- searches %>%
      count(status) %>%
      ggplot(aes(x = status, y = n, fill = status)) +
      geom_col(width = 0.4, show.legend = FALSE) +
      scale_fill_manual(values = c("Found" = "#4F6E56", "Not Found" = "#D9534F", "No Path" = "#D97706")) +
      labs(
        title = "Search Outcome Distribution",
        subtitle = "Successful path executions vs unremembered queries",
        x = "Search Status",
        y = "Query Count"
      ) +
      theme_sage_ivory()
    
    ggsave(file.path(out_dir, "plot4_search_success_rate.png"), p4, width = 8, height = 5, dpi = 150)
  }
}

# -------------------------------------------------------------
# Plot 5: Robot Movement Distance Over Time
# -------------------------------------------------------------
move_file <- file.path(data_dir, "robot_movements.csv")
if (file.exists(move_file)) {
  movements <- read_csv(move_file, show_col_types = FALSE)
  if (nrow(movements) > 0) {
    p5 <- movements %>%
      mutate(trip_id = row_number()) %>%
      ggplot(aes(x = trip_id, y = distance)) +
      geom_area(fill = "#8A9F8B", alpha = 0.4) +
      geom_line(color = "#3A4F3B", size = 1.2) +
      geom_point(color = "#4F6E56", size = 3) +
      labs(
        title = "Robot Movement Distance per Trip",
        subtitle = "Grid traversal trajectory distances over execution history",
        x = "Trip Index",
        y = "Traversed Distance"
      ) +
      theme_sage_ivory()
    
    ggsave(file.path(out_dir, "plot5_movement_distance.png"), p5, width = 8, height = 5, dpi = 150)
  }
}

# -------------------------------------------------------------
# Plot 6: Object Location Spatial History Map
# -------------------------------------------------------------
if (file.exists(det_file)) {
  detections <- read_csv(det_file, show_col_types = FALSE)
  if (nrow(detections) > 0) {
    p6 <- ggplot(detections, aes(x = x, y = y, color = object_name)) +
      geom_point(size = 5, alpha = 0.9) +
      scale_x_continuous(limits = c(0, 24)) +
      scale_y_continuous(limits = c(0, 16)) +
      scale_color_manual(values = c("#3A4F3B", "#647A65", "#8A9F8B", "#0284C7", "#D97706")) +
      labs(
        title = "2D Spatial Memory Map of Object Detections",
        subtitle = "Grid locations (X, Y) where objects were detected",
        x = "Grid X",
        y = "Grid Y",
        color = "Object"
      ) +
      theme_sage_ivory()
    
    ggsave(file.path(out_dir, "plot6_object_location_history.png"), p6, width = 8, height = 5, dpi = 150)
  }
}

cat("Successfully generated 6 Sage Green & Ivory R ggplot2 statistical plots in outputs/plots/\n")
