import pandas as pd
import warnings
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression
from meteostat import Point, Daily
from sklearn.preprocessing import PolynomialFeatures

from utils.plotting import plot_line

warnings.filterwarnings("ignore", category=FutureWarning)

class HistoricalWeather:
    """
    Class for analyzing and visualizing historical weather data for a specific city.
    """
    def __init__(self, city, lat, lon, years_back=10):
        """
        Initialize the HistoricalWeather object.
        :param city:
        :param lat:
        :param lon:
        :param years_back:
        """
        self.city = city
        self.lat = lat
        self.lon = lon
        self.years_back = years_back
        self.df = pd.DataFrame()
        self.yearly_avg_temp = pd.DataFrame()

    def fetch(self, silent=False):
        """
        Fetch historical weather data for the specified city.
        :param silent:
        :return:
        """
        end = datetime.now()
        start = datetime(end.year - self.years_back, 1, 1)
        location = Point(self.lat, self.lon)

        if not silent:
            print(f"\nHistorical analysis for {self.city} ({start.year}–{end.year - 1}):")

        data = Daily(location, start, end)
        data = data.fetch()

        if data.empty:
            if not silent:
                print("No data available for this location.")
            return

        data['year'] = data.index.year
        self.df = data.groupby('year')['tavg'].mean().reset_index()
        self.df.rename(columns={'tavg': 'temperature'}, inplace=True)

        current_year = datetime.now().year
        self.df = self.df[self.df['year'] < current_year]

        for _, row in self.df.iterrows():
            if pd.notna(row['temperature']):
                if not silent:
                    print(f"  {int(row['year'])}: {row['temperature']:.2f} °C")
            else:
                if not silent:
                    print(f"  {int(row['year'])}: No data")

        self.df.dropna(subset=['temperature'], inplace=True)

    def analyze(self, silent=False):
        """
        Analyze the historical weather data and print the results.
        :param silent:
        :return:
        """
        current_year = datetime.now().year

        if self.df.empty:
            if not silent:
                print("No data available for analysis.")
            return

        df_filtered = self.df[self.df['year'] < current_year]

        if not silent:
            print("\nAverage annual temperatures (excluding current year):")
            print(df_filtered)

        X = df_filtered[['year']]
        y = df_filtered['temperature']

        # Fit linear and polynomial regression models
        linear_model = LinearRegression()
        linear_model.fit(X, y)
        self.df['linear_trend'] = linear_model.predict(self.df[['year']])

        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)
        poly_model = LinearRegression()
        poly_model.fit(X_poly, y)

        self.df['poly_trend'] = poly_model.predict(poly.transform(self.df[['year']]))

        if not silent:
            print(f"\nLinear trend slope: {linear_model.coef_[0]:.3f} °C/year")
            print(f"Polynomial trend coefficients: {poly_model.coef_}")

    def analyze_historical_weather(self, silent=False):
        """
        Analyze the historical weather data and print the results.
        :param silent:
        :return:
        """
        if self.df.empty:
            if not silent:
                print("No historical data available for analysis.")
            return

        self.yearly_avg_temp = self.df.copy()

        if not silent:
            print("\nAverage annual temperatures:")
            print(self.yearly_avg_temp)

    def forecast_temperature(self, forecast_years=5, silent=False):
        """
        Forecast future temperatures using linear regression.
        :param forecast_years:
        :param silent:
        :return:
        """
        df = self.yearly_avg_temp.copy()

        current_year = datetime.now().year
        df = df[df['year'] < current_year]

        # Fit linear regression model
        X = df['year'].values.reshape(-1, 1)
        y = df['temperature'].values
        model = LinearRegression()
        model.fit(X, y)

        # Predict future temperatures
        future_years = np.array(
            [year for year in range(df['year'].max() + 1, df['year'].max() + forecast_years + 1)]
        ).reshape(-1, 1)

        predicted_temps = model.predict(future_years)

        os.makedirs("plots", exist_ok=True)

        # Plot historical and forecasted temperatures
        plt.figure(figsize=(10, 5))
        plt.plot(df['year'], df['temperature'], label='Historical temperatures', marker='o')
        plt.plot(future_years.flatten(), predicted_temps, label='Forecasted temperatures', linestyle='--', marker='o')
        plt.title(f"Forecasted average temperature in {self.city}")
        plt.xlabel("Year")
        plt.ylabel("Temperature (°C)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"plots/{self.city.lower()}_forecast_temperature.png")
        plt.close()

        if not silent:
            print(f"Forecasted temperatures for {self.city}:")
            for year, temp in zip(future_years.flatten(), predicted_temps):
                print(f"  {year}: {temp:.2f} °C")

    def seasonal_analysis(self, silent=False):
        """
        Perform seasonal analysis of historical weather data.
        :param silent:
        :return:
        """
        end = datetime.now()
        start = datetime(end.year - self.years_back, 1, 1)
        location = Point(self.lat, self.lon)

        if not silent:
            print("\n--- Seasonal analysis (historical data) ---")

        # Fetch daily data for the specified location
        daily_data = Daily(location, start, end).fetch().reset_index()
        daily_data['month'] = daily_data['time'].dt.month
        daily_data['season'] = daily_data['month'].apply(lambda m: (
            'Winter' if m in [12, 1, 2] else
            'Spring' if m in [3, 4, 5] else
            'Summer' if m in [6, 7, 8] else
            'Autumn'))

        # Calculate seasonal averages
        seasonal_avg = daily_data.groupby('season')['tavg'].mean().reindex(['Winter', 'Spring', 'Summer', 'Autumn'])
        seasonal_rain = daily_data.groupby('season')['prcp'].sum().reindex(['Winter', 'Spring', 'Summer', 'Autumn'])

        if not silent:
            for season in ['Winter', 'Spring', 'Summer', 'Autumn']:
                print(
                    f"{season}: Avg. temperature: {seasonal_avg[season]:.2f} °C, Total precipitation: {seasonal_rain[season]:.2f} mm")

        os.makedirs("plots", exist_ok=True)

        # Plot seasonal averages
        plt.figure(figsize=(10, 5))
        seasonal_avg.plot(kind='bar', color='salmon', alpha=0.7)
        plt.ylabel("Average temperature (°C)")
        plt.title(f"Seasonal average temperature in {self.city} ({start.year}-{end.year})")
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(f"plots/{self.city.lower()}_seasonal_temperature.png")
        plt.close()

        # Plot seasonal precipitation
        plt.figure(figsize=(10, 5))
        seasonal_rain.plot(kind='bar', color='skyblue', alpha=0.7)
        plt.ylabel("Total precipitation (mm)")
        plt.title(f"Seasonal precipitation in {self.city} ({start.year}-{end.year})")
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(f"plots/{self.city.lower()}_seasonal_precipitation.png")
        plt.close()

    def visualize(self):
        """
        Visualize the historical weather data.
        :return:
        """
        if self.df.empty:
            return

        plot_line(
            self.df,
            x_col='year',
            y_col='temperature',
            title=f"Average annual temperature in {self.city}",
            xlabel="Year",
            ylabel="Temperature (°C)",
            filename=f"plots/{self.city.lower()}_historical_temperatures.png",
            legend_label="Average temperature"
        )

        # Plot linear and polynomial trends
        plt.figure(figsize=(10, 5))
        plt.plot(self.df['year'], self.df['temperature'], label='Observed', marker='o')
        plt.plot(self.df['year'], self.df['linear_trend'], label='Linear Trend', linestyle='--')
        plt.plot(self.df['year'], self.df['poly_trend'], label='Polynomial Trend', linestyle=':')
        plt.title(f"Temperature trend in {self.city} (linear vs polynomial)")
        plt.xlabel("Year")
        plt.ylabel("Temperature (°C)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        os.makedirs("plots", exist_ok=True)
        plt.savefig(f"plots/{self.city.lower()}_trend_comparison.png")
        plt.close()

    def get_plot_paths(self):
        """
        Get the paths of the generated plots.
        :return:
        """
        return [
            f"plots/{self.city.lower()}_seasonal_temperature.png",
            f"plots/{self.city.lower()}_seasonal_precipitation.png",
            f"plots/{self.city.lower()}_forecast_temperature.png",
            f"plots/{self.city.lower()}_historical_temperatures.png",
            f"plots/{self.city.lower()}_trend_comparison.png"
        ]

    def get_full_report_text(self):
        """
        Generate a full report text for the historical weather analysis.
        :return:
        """
        lines = []

        # Add title
        lines.append(f"\nHistorical analysis for {self.city} ({self.df['year'].min()}–{self.df['year'].max()}):")
        for _, row in self.df.iterrows():
            year = int(row['year'])
            temp = row['temperature']
            if pd.notna(temp):
                lines.append(f"  {year}: {temp:.2f} °C")
            else:
                lines.append(f"  {year}: No data")

        lines.append("\nAverage annual temperatures:")
        lines.append(self.yearly_avg_temp.to_string(index=False))

        lines.append(f"\nLinear trend slope: {self.df['linear_trend'].diff().mean():.3f} °C/year")
        lines.append(f"Polynomial trend preview:")
        lines.append(self.df[['year', 'temperature', 'linear_trend', 'poly_trend']].to_string(index=False))

        return "\n".join(lines)
