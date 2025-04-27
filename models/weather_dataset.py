import pandas as pd
from utils.plotting import plot_multi_line, plot_histogram
import seaborn as sns
import matplotlib.pyplot as plt
import os

class WeatherDataset:
    """
    Class for analyzing and visualizing weather data across multiple cities.
    """
    def __init__(self, cities):
        """
        Initialize the WeatherDataset object.
        :param cities:
        """
        self.cities = cities
        self.df = self._combine_dataframes()

    def _combine_dataframes(self):
        """
        Combine the dataframes of all cities into a single dataframe.
        :return:
        """
        frames = []
        for city in self.cities:
            df = city.df.copy()
            df['city'] = city.name
            frames.append(df)
        return pd.concat(frames, ignore_index=True)

    def compare_cities(self, silent=False):
        """
        Compare weather data across all cities and print the results.
        :param silent:
        :return:
        """
        result = ["--- City Comparison ---"]

        result.append("Average temperatures (°C):")
        for city, temp in self.df.groupby('city')['temperature'].mean().items():
            result.append(f"  {city:<10}: {temp:.2f}")

        result.append("\nTotal precipitation (mm):")
        for city, rain in self.df.groupby('city')['rain'].sum().items():
            result.append(f"  {city:<10}: {rain:.2f}")

        result.append("\nAverage wind speed (m/s):")
        for city, wind in self.df.groupby('city')['wind_speed'].mean().items():
            result.append(f"  {city:<10}: {wind:.2f}")

        result.append("\nDays with highest precipitation (mm):")
        for city, rain_max in self.df.groupby('city')['rain'].max().items():
            result.append(f"  {city:<10}: {rain_max:.2f}")

        result.append("\nStrongest wind gusts (m/s):")
        for city, wind_max in self.df.groupby('city')['wind_speed'].max().items():
            result.append(f"  {city:<10}: {wind_max:.2f}")

        result.append("\nAverage air pressure (hPa):")
        for city, pressure in self.df.groupby('city')['pressure'].mean().items():
            if pd.notna(pressure):
                result.append(f"  {city:<10}: {pressure:.2f}")

        dates = self.df['datetime'].dt.date
        period = f"{dates.min()} to {dates.max()}"
        result.append(f"\nAnalysis period: {period}")

        full_report = "\n".join(result)
        if not silent:
            print(full_report)
        return full_report

    def plot_comparison(self):
        """
        Plot comparison graphs for temperature, precipitation, and wind speed across all cities.
        :return:
        """
        plot_multi_line(
            df=self.df,
            group_col='city',
            x_col='datetime',
            y_col='temperature',
            title="Temperature Comparison Between Cities",
            xlabel="Date",
            ylabel="Temperature (°C)",
            filename="temperature_comparison.png"
        )

        plot_multi_line(
            df=self.df,
            group_col='city',
            x_col='datetime',
            y_col='rain',
            title="Precipitation Comparison Between Cities",
            xlabel="Date",
            ylabel="Precipitation (mm)",
            filename="precipitation_comparison.png"
        )

        plot_multi_line(
            df=self.df,
            group_col='city',
            x_col='datetime',
            y_col='wind_speed',
            title="Wind Speed Comparison Between Cities",
            xlabel="Date",
            ylabel="Wind Speed (m/s)",
            filename="wind_comparison.png"
        )

        # Plot histograms for each city
        for city in self.df['city'].unique():
            df_city = self.df[self.df['city'] == city]
            plot_histogram(
                series=df_city['rain'],
                dates=df_city['datetime'].dt.date,
                title=f"Daily Precipitation in {city}",
                xlabel="Date",
                ylabel="Precipitation (mm)",
                filename=f"{city.lower()}_precipitation_hist.png"
            )

    def correlation_analysis(self, silent=False):
        """
        Perform correlation analysis on weather variables and save the correlation matrix plot.
        :param silent:
        :return:
        """
        if not silent:
            print("\n--- Correlation Analysis of Weather Variables ---")

        # Drop columns with all NaN values
        numeric_df = self.df[['temperature', 'wind_speed', 'rain', 'humidity', 'clouds', 'pressure']].dropna(axis=1, how='all')
        corr_matrix = numeric_df.corr()
        if not silent:
            print(corr_matrix)

        # Plot the correlation matrix
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title("Correlation Matrix of Weather Variables")
        plt.tight_layout()
        os.makedirs("plots", exist_ok=True)
        plt.savefig("plots/correlation_matrix.png")
        plt.close()

        return corr_matrix.round(6).to_string()

    def extreme_weather_analysis(self, silent=False):
        """
        Analyze extreme weather events (e.g., heatwaves, heavy rainfall) and print the results.
        :param silent:
        :return:
        """
        if not silent:
            print("\n--- Extreme Weather Events Analysis ---")

        # Identify extreme weather events
        extreme_temp_days = self.df[self.df['temperature'] > 30]
        extreme_rain_days = self.df[self.df['rain'] > 50]

        result = []

        result.append(f"\nDays with extremely high temperatures (>30°C): {len(extreme_temp_days)}")
        if not extreme_temp_days.empty:
            result.append(extreme_temp_days[['datetime', 'city', 'temperature']].to_string(index=False))

        result.append(f"\nDays with extreme rainfall (>50mm): {len(extreme_rain_days)}")
        if not extreme_rain_days.empty:
            result.append(extreme_rain_days[['datetime', 'city', 'rain']].to_string(index=False))

        text = "\n".join(result)
        if not silent:
            print(text)
        return text
