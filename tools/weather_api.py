import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool
import os

load_dotenv()  

@tool
def get_coordinates(location: str) -> str:
    """Convert a location name into latitude and longitude."""

    api_key = os.getenv("WEATHER_API_KEY")

    url = "https://api.openweathermap.org/geo/1.0/direct"

    params = {
        "q": location,
        "limit": 1,
        "appid": api_key
    }

    response = httpx.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    if not data:
        return f"Could not find location: {location}"

    place = data[0]

    return (
        f"Location: {place['name']}, {place.get('state', '')}, "
        f"{place['country']}\n"
        f"Latitude: {place['lat']}\n"
        f"Longitude: {place['lon']}"
    )

@tool
def get_weather(latitude: float, longitude: float) -> str:
    """
    Get the current weather for a given latitude and longitude.

    Args:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.

    Returns:
        str: A string describing the current weather conditions.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"

    try:
        response = httpx.get(url)
        response.raise_for_status()
        data = response.json()

        weather_description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        return (
            f"Current weather at ({latitude}, {longitude}):\n"
            f"- Description: {weather_description}\n"
            f"- Temperature: {temperature}°C\n"
            f"- Humidity: {humidity}%\n"
            f"- Wind Speed: {wind_speed} m/s"
        )
    except httpx.RequestError as e:
        return f"An error occurred while fetching the weather data: {e}"
    except httpx.HTTPStatusError as e:
        return f"HTTP error occurred: {e.response.status_code} - {e.response.text}"