import requests
from pprint import pprint
import numpy as np
import pandas as pd
import json
from urllib.request import urlopen
from datetime import datetime
import pytz
import pandas_profiling as pf

url = "https://offenedaten-koeln.de/api/3/action/package_show?id=7d8ce107-bbc4-49ac-a668-b43845c12e09"
response = urlopen(url)
json_data = response.read().decode("utf-8", "replace")
d = json.loads(json_data)
# df_data = pd.json_normalize(d["result"]["0"])

df = pd.DataFrame()
for i in range(0, 88, 1):
    print(i)
    url_format = d["result"][0]["resources"][i]["format"]
    if url_format == "json":
        url_name = d["result"][0]["resources"][i]["name"]
        url_json = d["result"][0]["resources"][i]["url"]
        response_json_file = urlopen(url_json)
        json_data_file = response_json_file.read().decode("utf-8", "replace")
        d_file = json.loads(json_data_file)
        df_json = pd.json_normalize(d_file["result"]["records"]).T
        print(df_json)
        df_json.reset_index(
            inplace=True, drop=True
        )  # reset the index and drop the old one, so you don't have duplicated indices
        df_json.columns = [df_json.iloc[0]]  # take the names from the first row
        df_json.drop(index=0, inplace=True)  # drop the first row
        df_json.reset_index(
            inplace=True, drop=True
        )  # Return the index counter to start from 0

        print(url_name)
        df_json.index.name = url_name
        df = df.append(df_json)
# df = df.groupby()
# df.head()
# profile = pf.ProfileReport(df_gps, title="Report of my GPS-Data", correlations=None)
# profile.to_file("profile_report.html")
# profile = pf.ProfileReport(df, title="Report Kriminalität")
# profile.to_file("kriminalitat_report.html")

# df_coord = pd.json_normalize(d["coord"])
# df_main = pd.json_normalize(d["main"])
# df = pd.concat(
#     [df_weather["main"], df_weather["description"], df_coord, df_main],
#     axis=1,
#     join="inner",
# )
