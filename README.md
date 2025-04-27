# Weather Data Analysis Project

This project offers a comprehensive analysis of weather data for selected cities.  
Leveraging information from a weather API and historical datasets, it calculates key statistics including temperature, precipitation, wind speed, and air pressure.  
The system detects weather anomalies, identifies extreme events, and compares metrics across different cities.

An interactive console application enables users to explore data by city, date, or specific metrics in an intuitive way.  
Additionally, the project automatically generates a professional PDF report featuring graphs, summaries, and tables, and supports exporting full analyses to CSV files (easily openable in Excel).

---

## Features

- Fetch real-time and historical weather data for Slovenian cities
- Calculate summary statistics (temperature, rain, wind, pressure)
- Detect weather anomalies and extreme weather events
- Compare weather metrics across multiple cities
- Explore data interactively by city, date, and metric
- Export analysis results to:
  - **PDF reports** (with tables, graphs, and summaries)
  - **CSV files** (compatible with Excel)
- Forecast future temperatures based on historical data
- Perform seasonal weather analysis (Spring, Summer, Autumn, Winter)

---

## Installation

1. Make sure you have **Python 3.9+** installed.
2. Clone the repository or download the source code.
3. Install the required Python libraries:

   ```bash
   pip install -r requirements.txt


## Usage

1. Run the main script:

   python main.py

2. Use the interactive console to:
   - View full startup report
   - Explore city data (summaries, extremes, anomalies, daily records)
   - Compare statistics between cities
   - Export data to CSV
   - Generate detailed PDF reports

3. All exported files (plots, CSVs, PDFs) are automatically saved in the corresponding folders (`plots/`, `exports/`).

---

## Project Structure

├── main.py                 # Main entry point for the application
├── interactive_console.py   # Interactive console application
├── models/
│   ├── city.py              # Model for city weather analysis
│   ├── historical.py        # Model for historical weather analysis
│   ├── weather_dataset.py   # Model for cross-city weather dataset analysis
├── utils/
│   ├── fetch.py             # Fetching weather data
│   ├── plotting.py          # Utility functions for creating plots
├── pdf_generator.py         # Generates PDF reports based on the analysis
├── pdf_exporter.py          # Helper class for PDF formatting and exporting
├── exports/                 # Folder where exported CSV files are saved
├── plots/                   # Folder where generated plots are saved
└── requirements.txt         # List of project dependencies

---

## Notes

- The `plots/` and `exports/` folders are automatically created if they do not exist.
- An active internet connection is required to fetch real-time and historical weather data.
- All CSV exports can be directly opened in Excel for further analysis or visualization.
- The PDF reports include summaries, tables, detected anomalies, extremes, and visual graphs.

---
