import os
import pandas as pd
from datetime import datetime

from models.city import CityWeather
from models.weather_dataset import WeatherDataset
from utils.fetch import fetch_weather_data_for_city
from models.historical import HistoricalWeather
from pdf_generator import generate_weather_pdf

def clear_screen():
    """
    Clears the console screen for better readability.
    :return:
    """
    os.system("cls" if os.name == "nt" else "clear")

def run_console_app():
    """
    Main function to run the interactive console application.
    :return:
    """
    weather_analysis = perform_new_analysis()

    while True:
        print("\n📊 Weather Analysis Console")
        print("0. View Full Startup Report")
        print("1. Explore City Data")
        print("2. Compare Cities")
        print("3. Export Data")
        print("4. Generate PDF Report")
        print("5. Exit")
        choice = input("Select an option (0–5): ")

        if choice == "0":
            show_full_report(weather_analysis)
        elif choice == "1":
            explore_city_data(weather_analysis)
        elif choice == "2":
            compare_cities(weather_analysis)
        elif choice == "3":
            export_city_data(weather_analysis)
        elif choice == "4":
            generate_pdf_report_interactive(weather_analysis)
        elif choice == "5":
            print("Goodbye! 👋")
            break
        else:
            print("❗ Invalid input. Please try again.")

def perform_new_analysis():
    """
    Performs a new weather analysis for a set of cities in Slovenia.
    :return:
    """
    CITIES = ['Ljubljana', 'Maribor', 'Koper', 'Celje', 'Novo Mesto', 'Velenje', 'Kranj', 'Ptuj', 'Murska Sobota']
    CITY_COORDS = {
        'Ljubljana': (46.0569, 14.5058),
        'Maribor': (46.5547, 15.6459),
        'Koper': (45.5481, 13.7300),
        'Celje': (46.2309, 15.2604),
        'Novo Mesto': (45.8030, 15.1689),
        'Velenje': (46.3592, 15.1106),
        'Kranj': (46.2389, 14.3556),
        'Ptuj': (46.4200, 15.8700),
        'Murska Sobota': (46.6625, 16.1667)
    }

    cities = []
    weather_analysis = {}

    # Fetch and analyze weather data for each city
    for name in CITIES:
        print(f"⏳ Fetching and analyzing current weather data for {name}...")
        data = fetch_weather_data_for_city(name)
        city = CityWeather(name, data)
        city.analyze(silent=True)
        city.visualize()
        city.detect_anomalies(silent=True)
        cities.append(city)

        summary = city.get_summary()
        images = city.get_plot_paths()

        weather_analysis[name] = {
            "summary": summary,
            "images": images,
            "anomalies": city.get_anomaly_rows(),
            "extremes": city.get_extremes_summary(),
            "city_object": city,
            "city_dataframe": city.df.to_dict(orient="records")
        }

    # Perform dataset-level analysis across all cities
    dataset = WeatherDataset(cities)
    weather_analysis["comparison_text"] = dataset.compare_cities(silent=True)
    weather_analysis["correlation_text"] = dataset.correlation_analysis(silent=True)
    weather_analysis["extremes_text"] = dataset.extreme_weather_analysis(silent=True)
    dataset.plot_comparison()
    print("✅ Current weather data analysis complete!\n")

    # Perform historical weather analysis
    history_texts = []
    for name in CITIES:
        print(f"⏳ Performing historical weather analysis for {name}...")
        lat, lon = CITY_COORDS[name]
        hw = HistoricalWeather(name, lat, lon, years_back=20)
        hw.fetch(silent=True)
        hw.analyze(silent=True)
        hw.seasonal_analysis(silent=True)
        hw.analyze_historical_weather(silent=True)
        hw.forecast_temperature(silent=True)
        hw.visualize()

        # Update images
        existing_filenames = {os.path.basename(p) for p in weather_analysis[name]["images"]}
        for img in hw.get_plot_paths():
            if os.path.basename(img) not in existing_filenames:
                weather_analysis[name]["images"].append(img)

        history_texts.append(hw.get_full_report_text())

    weather_analysis["historical_text"] = "\n".join(history_texts)
    print("✅ Historical weather analysis complete!")

    return weather_analysis

def explore_city_data(weather_analysis):
    """
    Allows the user to explore weather data for a selected city.
    :param weather_analysis:
    :return:
    """
    while True:
        print("\n🔍 Explore City Data")
        print("1. View Summary")
        print("2. View Extremes")
        print("3. View Anomalies")
        print("4. View Data by Date")
        print("5. Go Back")
        choice = input("Select an option: ")

        if choice == "1":
            show_city_summary(weather_analysis)
        elif choice == "2":
            show_extremes(weather_analysis)
        elif choice == "3":
            show_anomalies(weather_analysis)
        elif choice == "4":
            show_data_by_date(weather_analysis)
        elif choice == "5":
            break
        else:
            print("❗ Invalid input.")

def choose_city(weather_analysis):
    """
    Prompts the user to select a city from the available options.
    :param weather_analysis:
    :return:
    """
    cities = [name for name in weather_analysis if "city_object" in weather_analysis[name]]
    print("\nAvailable cities:")
    for i, city in enumerate(cities, 1):
        print(f"{i}. {city}")
    while True:
        choice = input("Select a city: ")
        if choice.isdigit() and 1 <= int(choice) <= len(cities):
            return cities[int(choice) - 1]
        print("❗ Invalid selection.")

def show_city_summary(weather_analysis):
    """
    Displays a summary of weather data for a selected city.
    :param weather_analysis:
    :return:
    """
    city = choose_city(weather_analysis)
    print(f"\n📋 Summary for {city}:\n")
    print(weather_analysis[city]["summary"])

def show_extremes(weather_analysis):
    """
    Displays extreme weather events for a selected city.
    :param weather_analysis:
    :return:
    """
    city = choose_city(weather_analysis)
    print(f"\n🌡️ Extremes for {city}:")
    for row in weather_analysis[city].get("extremes", []):
        print(f"{row[0]:<20} {row[1]:<12} {row[2]}")

def show_anomalies(weather_analysis):
    """
    Displays detected weather anomalies for a selected city.
    :param weather_analysis:
    :return:
    """
    city = choose_city(weather_analysis)
    print(f"\n⚠️ Detected anomalies in {city}:")
    rows = weather_analysis[city].get("anomalies", [])
    if not rows:
        print("No anomalies detected.")
        return
    print(f"{'Date':<12} {'Temperature':<15} {'Rain':<15}")
    for row in rows:
        print(f"{row[0]:<12} {row[1]:<15} {row[2]:<15}")

def compare_cities(weather_analysis):
    """
    Allows the user to compare weather data across multiple cities.
    :param weather_analysis:
    :return:
    """
    while True:
        print("\n🔄 City Comparison:")
        print("1. Compare key metrics summary")
        print("2. Compare daily values for selected metric")
        print("3. Go back")
        choice = input("Select an option: ")

        if choice == "1":
            compare_summary_table(weather_analysis)
        elif choice == "2":
            show_metric_comparison(weather_analysis)
        elif choice == "3":
            break
        else:
            print("❗ Invalid input.")

def compare_summary_table(weather_analysis):
    """
    Displays a summary table comparing key weather metrics across all cities.
    :param weather_analysis:
    :return:
    """
    print("\n📋 City Metrics Summary:\n")
    metrics = [
        "Average temperature", "Maximum temperature", "Minimum temperature",
        "Total precipitation", "Average wind speed", "Average air pressure"
    ]

    cities = [name for name in weather_analysis if "city_object" in weather_analysis[name]]

    # Header
    header = f"{'Metric':<25}" + "".join(f"{city:<15}" for city in cities)
    print(header)
    print("-" * len(header))

    # Data rows
    for metric in metrics:
        row = f"{metric:<25}"
        for city in cities:
            summary = weather_analysis[city]["summary"]
            value = extract_metric_from_summary(summary, metric)
            row += f"{value:<15}"
        print(row)

def export_city_data(weather_analysis):
    """
    Exports the weather data for a selected city to a CSV file.
    :param weather_analysis:
    :return:
    """
    city = choose_city(weather_analysis)
    city_obj = weather_analysis[city]["city_object"]

    if city_obj is None:
        print(f"❗ City object for {city} is missing. Cannot export data.")
        return

    df = city_obj.df.copy()

    column_renames = {
        "temperature": "temperature (°C)",
        "humidity": "humidity (%)",
        "rain": "rain (mm)",
        "clouds": "clouds (%)",
        "wind_speed": "wind speed (m/s)",
        "pressure": "pressure (hPa)",
        "predicted": "predicted temperature (°C)"
    }

    df = df.rename(columns=column_renames)
    df["city"] = city

    os.makedirs("exports", exist_ok=True)
    filepath = f"exports/{city.lower()}_weather_data.csv"
    df.to_csv(filepath, index=False)

    print(f"\n✅ Data for {city} exported to {filepath}")

def extract_metric_from_summary(summary_text, metric_name):
    """
    Extracts a specific metric value from the summary text.
    :param summary_text:
    :param metric_name:
    :return:
    """
    for line in summary_text.splitlines():
        if line.lower().startswith(metric_name.lower()):
            return line.split(":")[1].strip()
    return "-"

def show_data_by_date(weather_analysis):
    """
    Allows the user to filter and display weather data for a selected city by date or date range.
    :param weather_analysis:
    :return:
    """
    city = choose_city(weather_analysis)
    city_obj = weather_analysis[city]["city_object"]
    df = city_obj.df.copy()

    # Display available date range first
    available_dates = df['date'].sort_values()
    print(f"\n📅 Available data range: {available_dates.min()} to {available_dates.max()}")

    print("\n📅 You can filter data by:")
    print("1. Specific date (e.g. 2025-04-16)")
    print("2. Date range (e.g. 2025-04-15 to 2025-04-18)")
    print("3. Cancel")

    choice = input("Choose filter type: ")

    if choice == "1":
        date_str = input("Enter the date (YYYY-MM-DD): ")
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            filtered = df[df['date'] == date]
        except ValueError:
            print("❗ Invalid date format.")
            return

    elif choice == "2":
        start_str = input("Enter start date (YYYY-MM-DD): ")
        end_str = input("Enter end date (YYYY-MM-DD): ")
        try:
            start = datetime.strptime(start_str, "%Y-%m-%d").date()
            end = datetime.strptime(end_str, "%Y-%m-%d").date()
            filtered = df[(df['date'] >= start) & (df['date'] <= end)]
        except ValueError:
            print("❗ Invalid date format.")
            return

    else:
        return

    if filtered.empty:
        print("⚠️ No data for selected date(s).")
        return

    # Display the filtered data
    print(f"\n🗓️ Weather data for {city}:\n")
    print(f"{'Date':<12} {'Temp (°C)':>12} {'Rain (mm)':>12} {'Wind (m/s)':>12} {'Pressure (hPa)':>17}")
    print("-" * 65)

    # Format the data for display
    for _, row in filtered.iterrows():
        date = row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date'])
        temp = f"{row['temperature']:.2f}"
        rain = f"{row['rain']:.2f}"
        wind = f"{row['wind_speed']:.2f}"
        pressure = f"{row['pressure']:.0f}" if not pd.isna(row['pressure']) else "N/A"

        print(f"{date:<12} {temp:>12} {rain:>12} {wind:>12} {pressure:>17}")

def show_metric_comparison(weather_analysis):
    """
    Displays a comparison of selected weather metrics across all cities.
    :param weather_analysis:
    :return:
    """
    print("\n📊 Available metrics:")
    metrics = {
        "1": ("temperature", "Temperature (°C)"),
        "2": ("rain", "Rain (mm)"),
        "3": ("wind_speed", "Wind Speed (m/s)"),
        "4": ("pressure", "Pressure (hPa)")
    }

    for key, (_, label) in metrics.items():
        print(f"{key}. {label}")
    choice = input("Select a metric to compare: ")

    if choice not in metrics:
        print("❗ Invalid choice.")
        return

    metric_key, metric_label = metrics[choice]

    # Display the comparison header
    print(f"\n📈 {metric_label} Comparison:\n")
    cities = [name for name in weather_analysis if "city_object" in weather_analysis[name]]
    header = f"{'Date':<12}" + "".join(f"{city:<13}" for city in cities)
    print(header)
    print("-" * len(header))

    # Display the data
    dates = weather_analysis[cities[0]]["city_object"].df['date']

    for date in dates:
        row = f"{str(date):<12}"
        for city in cities:
            df = weather_analysis[city]["city_object"].df
            value = df[df['date'] == date][metric_key]
            if not value.empty:
                row += f"{value.values[0]:<13.2f}"
            else:
                row += f"{'N/A':<13}"
        print(row)

def show_full_report(weather_analysis):
    """
    Displays the full startup report for all cities analyzed.
    :param weather_analysis:
    :return:
    """
    print("\n📃 FULL STARTUP REPORT\n")

    for city, data in weather_analysis.items():
        if not isinstance(data, dict) or "summary" not in data:
            continue

        print(f"Fetching data for {city}...\n")
        print(f"Analysis for {city}:")
        print(data["summary"])
        print()

        print(f"📍 Weather anomalies detected in {city} (window=3, threshold=2):")
        anomalies = data.get("anomalies", [])
        if not anomalies:
            print("  No anomalies found.")
        else:
            print(f"  {len(anomalies)} anomalies detected.")
        print()

    if "comparison_text" in weather_analysis:
        print("Combined analysis of all cities:\n")
        print(weather_analysis["comparison_text"])
        print()

    if "correlation_text" in weather_analysis:
        print("--- Correlation Analysis of Weather Variables ---")
        print(weather_analysis["correlation_text"])
        print()

    if "extremes_text" in weather_analysis:
        print("--- Extreme Weather Events Analysis ---")
        print(weather_analysis["extremes_text"])
        print()

    if "historical_text" in weather_analysis:
        print("Historical data analysis:\n")
        print(weather_analysis["historical_text"])
        print()


def generate_pdf_report_interactive(weather_analysis):
    """
    Generates a PDF report for selected cities based on the weather analysis data.
    :param weather_analysis:
    :return:
    """
    print("\n📝 PDF Report Generator")
    cities = [city for city in weather_analysis if isinstance(weather_analysis[city], dict)]

    # Select cities
    print("Select cities to include (comma-separated numbers):")
    for i, city in enumerate(cities, 1):
        print(f"{i}. {city}")
    selected = input("Enter selection: ")
    indices = [int(i.strip()) for i in selected.split(",") if
               i.strip().isdigit() and 1 <= int(i.strip()) <= len(cities)]
    selected_cities = [cities[i - 1] for i in indices]

    if not selected_cities:
        print("❗ No valid cities selected. Aborting PDF generation.")
        return

    export_data = {}

    for city_name in selected_cities:
        entry = weather_analysis[city_name]
        city_obj = entry["city_object"]

        # Always use the full data without filtering
        filtered_df = city_obj.df.copy()

        filtered_city = CityWeather.from_dataframe(name=city_name, df=filtered_df)
        filtered_city.analyze(silent=True)
        filtered_city.detect_anomalies(silent=True)
        filtered_city.visualize()

        export_data[city_name] = {
            **entry,
            "city_object": filtered_city,
            "city_dataframe": filtered_df.to_dict("records")
        }

    # Select report sections
    print("\nSelect analysis sections to include (comma-separated):")
    print("1. Comparison")
    print("2. Correlation")
    print("3. Extremes")
    print("4. Historical")
    section_input = input("Enter selection: ")
    section_map = {
        "1": "comparison_text",
        "2": "correlation_text",
        "3": "extremes_text",
        "4": "historical_text"
    }
    selected_sections = [section_map[i.strip()] for i in section_input.split(",") if i.strip() in section_map]

    dataset = WeatherDataset([entry["city_object"] for entry in export_data.values()])
    if "comparison_text" in selected_sections:
        export_data["comparison_text"] = dataset.compare_cities(silent=True)
    if "correlation_text" in selected_sections:
        export_data["correlation_text"] = dataset.correlation_analysis(silent=True)
    if "extremes_text" in selected_sections:
        export_data["extremes_text"] = dataset.extreme_weather_analysis(silent=True)
    if "historical_text" in selected_sections and "historical_text" in weather_analysis:
        export_data["historical_text"] = weather_analysis["historical_text"]

    generate_weather_pdf(export_data)
    print("✅ PDF report generated for selected cities.")
