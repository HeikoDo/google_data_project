import requests
from pprint import pprint
import numpy as np
import pandas as pd
import json
from urllib.request import urlopen
from datetime import datetime
import pytz

# API Key - NOT TO SHARE
from data.keys import open_weather_API


def local_to_utc_timestamp(
    datetime_string="2020-01-21 02:00:00", timezone="Europe/Berlin"
):
    local = pytz.timezone(timezone)
    naive = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")
    local_dt = local.localize(
        naive, is_dst=None
    )  # or naive.astimezone(timezone('Europe/Berlin')
    utc_dt = local_dt.astimezone(pytz.utc)
    return str(int(utc_dt.timestamp()))


API_key = open_weather_API
city_name = "cologne"
country_code = ""
number_of_the_month = "12"
number_of_the_day = "3"

# lat = str(round(50.93885496238991, 3))
# lon = str(round(6.961827270245965, 3))
lat = str(round(28.079376559588994, 3))
lon = str(round(-16.679407493908965, 3))

print(lat)
print(lon)

start = local_to_utc_timestamp(
    "2021-01-21 02:00:00"
)  # Start date (unix time, UTC time zone)
end = local_to_utc_timestamp(
    "2021-01-21 02:59:00"
)  # End date (unix time, UTC time zone)

print(start)
print(end)

if 0:
    # https://realpython.com/python-string-formatting/
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_key}&units=metric"

    response = urlopen(url)
    json_data = response.read().decode("utf-8", "replace")
    d = json.loads(json_data)
    df_weather = pd.json_normalize(d["weather"])
    df_coord = pd.json_normalize(d["coord"])
    df_main = pd.json_normalize(d["main"])
    df = pd.concat(
        [df_weather["main"], df_weather["description"], df_coord, df_main],
        axis=1,
        join="inner",
    )

    # res = requests.get(url)
    # data = res.json()
    # temp = data['main']['temp']
    # wind_speed = data['wind']['speed']
    # latitude = data['coord']['lat']
    # longitude = data['coord']['lon']
    # description = data['weather'][0]['description']
    # print(f'Temperature : {temp} degree celcius')
    # print(f'Wind Speed : {wind_speed} m/s')
    # print(f'Latitude : {latitude}')
    # print(f'Longitude : {longitude}')
    # print(f'Description : {description}')

if 0:
    url = f"http://history.openweathermap.org/data/2.5/aggregated/year?q={city_name},{country_code}&appid={API_key}"
    response = urlopen(url)
    json_data = response.read().decode("utf-8", "replace")
    d = json.loads(json_data)
    df = pd.json_normalize(d["result"])
    df.to_excel(f"history_{city_name}.xlsx", index=False)

if 1:  # call as hour
    url = f"http://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={start}&end={end}&appid={API_key}"
    print(url)
    response = urlopen(url)
    json_data = response.read().decode("utf-8", "replace")
    d = json.loads(json_data)
    df = pd.json_normalize(d["list"])

    # Kelvin in Celsius
    df["main.temp"] = df["main.temp"] - 273.15
    df["main.feels_like"] = df["main.feels_like"] - 273.15
    df["main.temp_min"] = df["main.temp_min"] - 273.15
    df["main.temp_max"] = df["main.temp_max"] - 273.15

    # Get Data from list and dict in jason file which is not correctly extracted with normalize
    weather_description = []
    weather_main = []
    for index, value in enumerate(d["list"]):
        weather_description.append(d["list"][index]["weather"][0]["description"])
        weather_main.append(d["list"][index]["weather"][0]["main"])
    df["description"] = np.asarray(weather_description)
    df["main"] = np.asarray(weather_main)

    # Timestamp in datetime
    # https://www.codegrepper.com/code-examples/python/pandas+unix+timestamp+to+datetime
    df["datetime_utc"] = pd.to_datetime(df["dt"], unit="s", utc=True)
    df["datetime_local"] = df["datetime_utc"].dt.tz_convert("Europe/Berlin")
    # df.to_excel(f"history_{city_name}.xlsx", index=False)

print(datetime.fromtimestamp(1369728000))
print(datetime.fromtimestamp(1369789200))
print(datetime.fromtimestamp(float(start)))
print(datetime.fromtimestamp(float(end)))
