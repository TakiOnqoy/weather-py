import argparse
import json
import sys
from configparser import ConfigParser
from urllib import error, parse, request

import style

BASE_WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

def read_user_cli_args():
    """Handles the CLI user interaction

    returns:
        argparse.Namespace: Populated namespace object
    """
    parser = argparse.ArgumentParser(
        description="gets weather and temperature information for a city"
    )
    parser.add_argument(
        "city", nargs="+", type=str, help="enter the city name"
    )
    parser.add_argument(
        "-i",
        "--imperial",
        action="store_true",
        help="display the temperature in imperial units",
    )
    return parser.parse_args()

def build_weather_query(city_input, imperial=False):
    """Builds the URL for an API request to OpenWeather's weather API.

    Args:
        city_input (List[str]): Name of a city as collected by argparse
        imperial (bool): Whether or not to use imperial units for temperature

    Returns:
        str: URL formatted for a call to OpenWeather's city name endpoint
    """
    api_key = _get_api_key()
    city_name = " ".join(city_input)
    url_encoded_city_name = parse.quote_plus(city_name)
    units = "imperial" if imperial else "metric"
    url = (
        f"{BASE_WEATHER_API_URL}?q={url_encoded_city_name}"
        f"&units={units}&appid={api_key}"
    )
    return url

def get_weather_data(query_url):
    """Sends a get method to receive data from Weather API, then translates data
    from the JSON payload response.

    Args:
        query_url (str): receives the fully joined url to make the API request
    Returns:
        Dict: displays weather data from requested city.
    """
    try:
        response = request.urlopen(query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401:  # 401 Unauthorized
            sys.exit(f"Access denied. Please check your API key and try again.")
        elif http_error.code == 404:  # 404 No    t found
            sys.exit(f"Can't find weather data for this city.")
        else:
            sys.exit(f"Something went wrong... ({http_error.code})")
    data = response.read()
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Couldn't read the server response.")

def _get_api_key():
    """
    Fetches the API key from your configuration file

    Expects a config file named "secrets.ini" with structure:

    [openweather]
    api_key={$API_KEY}
    """

    config = ConfigParser()
    config.read('secrets.ini')
    return config['openweather']['api_key']

def print_result(weather_data, imperial=False):
    city_name = weather_data['name']
    city_country = weather_data['sys']['country']
    weather_description = weather_data['weather'][0]['description']
    temperature = weather_data['main']['temp']
    style.change_color(style.REVERSE)
    style.change_color(style.RED)
    print(f"{city_name:^{style.PADDING}}, {city_country}", end="")
    style.change_color(style.RESET)
    style.change_color(style.RED)
    print(
        f"\t{weather_description.capitalize():^{style.PADDING}}",
        end=" ",
    )
    style.change_color(style.RESET)
    print(f"({temperature}°{'F' if imperial else 'C'})")

if __name__ == "__main__":
    user_args = read_user_cli_args()
    query_url = build_weather_query(user_args.city, user_args.imperial)
    weather_data = get_weather_data(query_url)
    print_result(weather_data, user_args.imperial)
