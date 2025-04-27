import pandas as pd
import numpy as np
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression

import matplotlib.pyplot as plt

class CityWeather:
    """
    Class for analyzing and visualizing weather data for a specific city.
    """
    def __init__(self, name, raw_data):
        """
        Initialize the CityWeather object.
        :param name:
        :param raw_data:
        """
        if raw_data is None:
            raise ValueError("CityWeather requires raw_data unless using from_dataframe()")
        self.name = name
        self.raw_data = raw_data
        self.df = self._process_data()

    def _process_data(self):
        """
        Process the raw weather data into a DataFrame.
        :return:
        """
        records = []
        # Convert the raw data into a list of dictionaries
        for entry in self.raw_data['list']:
            dt = datetime.fromtimestamp(entry['dt'])
            temp = entry['temp']['day']
            humidity = entry['humidity']
            rain = entry.get('rain', 0.0)
            clouds = entry.get('clouds', 0)
            wind_speed = entry.get('speed', 0.0)
            description = entry['weather'][0]['description'] if 'weather' in entry else ''
            pressure = entry.get('pressure', None)

            # Create a dictionary for each entry
            records.append({
                'datetime': dt,
                'temperature': temp,
                'humidity': humidity,
                'rain': rain,
                'clouds': clouds,
                'wind_speed': wind_speed,
                'description': description,
                'pressure': pressure
            })

        # Create a DataFrame from the records
        df = pd.DataFrame(records)
        df['timestamp'] = df['datetime'].astype(np.int64) // 10**9
        df['date'] = df['datetime'].dt.date
        return df

    def analyze(self, silent=False):
        """
        Analyze the weather data and print the results.
        :param silent:
        :return:
        """
        # Calculate various statistics
        self.avg_temp = self.df['temperature'].mean()
        self.max_temp = self.df['temperature'].max()
        self.min_temp = self.df['temperature'].min()
        self.total_rain = self.df['rain'].sum()
        self.avg_wind = self.df['wind_speed'].mean()
        self.avg_pressure = self.df['pressure'].mean() if 'pressure' in self.df else None

        if not silent:
            print(f"\nAnalysis for {self.name}:")
            print("Average temperature:", round(self.avg_temp, 2), "°C")
            print("Maximum temperature:", self.max_temp, "°C")
            print("Minimum temperature:", self.min_temp, "°C")
            print("Total precipitation:", round(self.total_rain, 2), "mm")
            print("Average wind speed:", round(self.avg_wind, 2), "m/s")
            if self.avg_pressure is not None:
                print("Average air pressure:", round(self.avg_pressure, 2), "hPa")

    def visualize(self):
        """
        Visualize the weather data and save the plots.
        :return:
        """
        X = self.df[['timestamp']]
        y = self.df['temperature']
        model = LinearRegression().fit(X, y)
        self.df['predicted'] = model.predict(X)

        os.makedirs('plots', exist_ok=True)

        # Temperature and prediction plot
        plt.figure(figsize=(10, 5))
        plt.plot(self.df['datetime'], self.df['temperature'], label='Actual temperature', color='blue')
        plt.plot(self.df['datetime'], self.df['predicted'], label='Predicted temperature', linestyle='--',
                 color='orange')
        plt.title(f"Temperature and trend for {self.name}")
        plt.xlabel("Date")
        plt.ylabel("°C")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"plots/{self.name.lower()}_temperature_and_prediction.png")
        plt.close()

        # Air pressure plot
        plt.figure(figsize=(10, 5))
        plt.plot(self.df['datetime'], self.df['pressure'], label='Air pressure', color='green')
        plt.title(f"Air pressure over time in {self.name}")
        plt.xlabel("Date")
        plt.ylabel("Pressure (hPa)")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"plots/{self.name.lower()}_pressure.png")
        plt.close()

    def get_summary(self):
        """
        Get a summary of the weather data.
        :return:
        """
        return (
            f"Average temperature: {self.avg_temp:.2f} °C\n"
            f"Maximum temperature: {self.max_temp:.2f} °C\n"
            f"Minimum temperature: {self.min_temp:.2f} °C\n"
            f"Total precipitation: {self.total_rain:.2f} mm\n"
            f"Average wind speed: {self.avg_wind:.2f} m/s\n"
            f"Average air pressure: {self.avg_pressure:.2f} hPa"
        )

    def get_plot_paths(self):
        """
        Get the paths of the generated plots.
        :return:
        """
        return [
            f"{self.name.lower()}_temperature_and_prediction.png",
            f"{self.name.lower()}_pressure.png",
            f"{self.name.lower()}_seasonal_temperature.png",
            f"{self.name.lower()}_forecast_temperature.png",
            f"{self.name.lower()}_anomalies.png"
        ]

    def detect_anomalies(self, window=3, threshold=2, silent=False):
        """
        Detect weather anomalies based on rolling mean and standard deviation.
        :param window:
        :param threshold:
        :param silent:
        :return:
        """
        # Temperature anomalies
        df = self.df.copy()
        df['temp_ma'] = df['temperature'].rolling(window=window, center=True).mean()
        df['temp_std'] = df['temperature'].rolling(window=window, center=True).std()
        df['temp_anomaly'] = abs(df['temperature'] - df['temp_ma']) > threshold * df['temp_std']

        # Rainfall anomalies
        df['rain_ma'] = df['rain'].rolling(window=window, center=True).mean()
        df['rain_std'] = df['rain'].rolling(window=window, center=True).std()
        df['rain_anomaly'] = abs(df['rain'] - df['rain_ma']) > threshold * df['rain_std']

        anomalies = df[(df['temp_anomaly']) | (df['rain_anomaly'])]
        self.anomalies = anomalies

        # Save the anomalies to a CSV file
        if not silent:
            print(f"\n📍 Weather anomalies detected in {self.name} (window={window}, threshold={threshold}):")
            if anomalies.empty:
                print("  No anomalies found.")
            else:
                print(anomalies[['datetime', 'temperature', 'rain', 'temp_anomaly', 'rain_anomaly']])

        os.makedirs('plots', exist_ok=True)

        # Plot the anomalies
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(df['datetime'], df['temperature'], label='Temperature', color='blue')
        ax1.plot(df['datetime'], df['temp_ma'], label='Temp MA', linestyle='--', color='cyan')
        ax1.scatter(df[df['temp_anomaly']]['datetime'], df[df['temp_anomaly']]['temperature'],
                    color='red', label='Temp Anomaly', zorder=5)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Temperature (°C)", color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        ax2 = ax1.twinx()
        ax2.plot(df['datetime'], df['rain'], label='Rain', color='green')
        ax2.plot(df['datetime'], df['rain_ma'], label='Rain MA', linestyle='--', color='lime')
        ax2.scatter(df[df['rain_anomaly']]['datetime'], df[df['rain_anomaly']]['rain'],
                    color='orange', label='Rain Anomaly', zorder=5)
        ax2.set_ylabel("Rain (mm)", color='green')
        ax2.tick_params(axis='y', labelcolor='green')

        fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
        plt.title(f"Weather Anomalies in {self.name}")
        plt.tight_layout()
        plt.savefig(f"plots/{self.name.lower()}_anomalies.png")
        plt.close()

    def get_anomaly_rows(self, top_n=5):
        """
        Get the top N anomalies detected in the weather data.
        :param top_n:
        :return:
        """
        if not hasattr(self, 'anomalies') or self.anomalies.empty:
            return []

        # Calculate the differences for sorting
        anomalies = self.anomalies.copy()
        anomalies['temp_diff'] = abs(anomalies['temperature'] - anomalies['temp_ma'])
        anomalies['rain_diff'] = abs(anomalies['rain'] - anomalies['rain_ma'])
        anomalies['total_diff'] = anomalies['temp_diff'].fillna(0) + anomalies['rain_diff'].fillna(0)
        top = anomalies.sort_values(by='total_diff', ascending=False).head(top_n)

        # Prepare the rows for the table
        rows = []
        for _, row in top.iterrows():
            rows.append([
                row['datetime'].strftime('%Y-%m-%d'),
                f"{row['temperature']:.2f} °C" if row['temp_anomaly'] else "-",
                f"{row['rain']:.2f} mm" if row['rain_anomaly'] else "-"
            ])
        return rows

    def get_extremes_summary(self):
        """
        Get a summary of the weather extremes detected in the data.
        :return:
        """
        hottest = self.df.loc[self.df['temperature'].idxmax()]
        coldest = self.df.loc[self.df['temperature'].idxmin()]
        rainiest = self.df.loc[self.df['rain'].idxmax()]
        windiest = self.df.loc[self.df['wind_speed'].idxmax()]

        return [
            ["Hottest Day", hottest['datetime'].strftime('%Y-%m-%d'), f"{hottest['temperature']:.2f} °C"],
            ["Coldest Day", coldest['datetime'].strftime('%Y-%m-%d'), f"{coldest['temperature']:.2f} °C"],
            ["Most Rainfall", rainiest['datetime'].strftime('%Y-%m-%d'), f"{rainiest['rain']:.2f} mm"],
            ["Windiest Day", windiest['datetime'].strftime('%Y-%m-%d'), f"{windiest['wind_speed']:.2f} m/s"]
        ]

    @classmethod
    def from_dataframe(cls, name, df):
        """
        Create a CityWeather object from a DataFrame.
        :param name:
        :param df:
        :return:
        """
        obj = cls.__new__(cls)  # Create a new instance without calling __init__
        obj.name = name
        obj.raw_data = None
        obj.df = df
        obj.analyzed = False
        obj.anomalies = []
        obj.images = []
        return obj
