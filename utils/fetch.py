import requests
import json
import os

API_KEY = 'f08f824abe9014787bbe5ac8243a5f0e'
BASE_URL = 'https://api.openweathermap.org/data/2.5/forecast/daily'

def fetch_weather_data_for_city(city_name, days=16):
    """
    Fetch weather data for a specific city using OpenWeatherMap API.
    :param city_name:
    :param days:
    :return:
    """
    params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'en',
        'cnt': days
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        os.makedirs('data', exist_ok=True)
        with open(f"data/{city_name.lower()}_daily.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return data
    else:
        raise Exception(f"Error fetching data for {city_name}: {response.status_code}")
