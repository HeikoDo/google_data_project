import requests
from pprint import pprint
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
from urllib.request import urlopen
import datetime as dt
import pytz
import os
import datashader as ds
import colorcet
import holoviews as hv
import hvplot.pandas
import panel as pn
import pandas_profiling as pf

# setting bokeh as backend
hv.extension("bokeh")
from bokeh.plotting import show

### For Linux's Users
import os

os.environ[
    "PROJ_LIB"
] = r"/home/heiko/anaconda3/pkgs/proj4-5.2.0-he6710b0_1 / share / proj"

# ### For Window's Users
#       import os
#       os.environ['PROJ_LIB'] = r'C:\Users\XXXXX\Anaconda3\pkgs\proj4-5.2.0- ha925a31_1\Library\share'

from mpl_toolkits.basemap import Basemap

if 1:
    # load the google location history data
    df_gps = pd.read_json("data/Google_Location_History.json")
    print("There are {:,} rows in the location history dataset".format(len(df_gps)))

    # parse lat, lon, and timestamp from the dict inside the locations column
    df_gps["lon"] = df_gps["locations"].map(lambda x: x["longitudeE7"])
    df_gps["lat"] = df_gps["locations"].map(lambda x: x["latitudeE7"])
    df_gps["timestamp_ms"] = df_gps["locations"].map(lambda x: x["timestampMs"])

    # convert lat/lon to decimalized degrees and the timestamp to date-time
    df_gps["lon"] = df_gps["lon"] / 10.0 ** 7
    df_gps["lat"] = df_gps["lat"] / 10.0 ** 7
    df_gps["timestamp_ms"] = df_gps["timestamp_ms"].astype(float) / 1000
    df_gps["datetime"] = df_gps["timestamp_ms"].map(
        lambda x: dt.datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S")
    )
    date_range = "{}-{}".format(
        df_gps["datetime"].min()[:4], df_gps["datetime"].max()[:4]
    )

    # create "easting" and "northing" from longitude and latitude
    # https://holoviews.org/reference_manual/holoviews.element.html#holoviews.element.Tiles.lon_lat_to_easting_northing
    (
        df_gps["easting"],
        df_gps["northing"],
    ) = hv.element.Tiles.lon_lat_to_easting_northing(df_gps["lon"], df_gps["lat"])
    #  hv.element.Tiles.easting_northing_to_lon_lat(easting, northing) -> also possible

    # drop columns we don't need, then show a slice of the dataframe
    df_gps = df_gps.drop(labels=["locations", "timestamp_ms"], axis=1, inplace=False)
    # df_gps[1000:1005]

    # define map colors
    land_color = "#f5f5f3"
    water_color = "#cdd2d4"
    coastline_color = "#f5f5f3"
    border_color = "#bbbbbb"
    meridian_color = "#f5f5f3"
    marker_fill_color = "#cc3300"
    marker_edge_color = "None"

    # create the plot
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(111, facecolor="#ffffff", frame_on=False)
    ax.set_title(
        "Google Location History, {}".format(date_range), fontsize=24, color="#333333"
    )

    # draw the basemap and its features
    m = Basemap(projection="kav7", lon_0=0, resolution="c", area_thresh=10000)
    m.drawmapboundary(color=border_color, fill_color=water_color)
    m.drawcoastlines(color=coastline_color)
    m.drawcountries(color=border_color)
    m.fillcontinents(color=land_color, lake_color=water_color)
    m.drawparallels(np.arange(-90.0, 120.0, 30.0), color=meridian_color)
    m.drawmeridians(np.arange(0.0, 420.0, 60.0), color=meridian_color)

    # project the location history points then scatter plot them
    x, y = m(df_gps["lon"].values, df_gps["lat"].values)
    m.scatter(
        x,
        y,
        s=8,
        color=marker_fill_color,
        edgecolor=marker_edge_color,
        alpha=1,
        zorder=3,
    )

    # show the map
    plt.savefig(
        "./google_location_history_world_map.png",
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.2,
    )
    plt.show()

    # first define a transverse mercator projection for cologne
    map_width_m = 1000 * 1000
    map_height_m = 1200 * 1000
    target_crs = {
        "datum": "WGS84",
        "ellps": "WGS84",
        "proj": "tmerc",
        # 'lon_0': -119,
        # 'lat_0': 37.5}
        "lon_0": 6.9,
        "lat_0": 50.9,
    }

    # plot the map
    fig_width = 6
    fig = plt.figure(figsize=[fig_width, fig_width * map_height_m / float(map_width_m)])
    ax = fig.add_subplot(111, facecolor="#ffffff", frame_on=False)
    ax.set_title(
        "Cologne Location History, {}".format(date_range), fontsize=16, color="#333333"
    )

    m = Basemap(
        ellps=target_crs["ellps"],
        projection=target_crs["proj"],
        lon_0=target_crs["lon_0"],
        lat_0=target_crs["lat_0"],
        width=map_width_m,
        height=map_height_m,
        resolution="l",
        area_thresh=10000,
    )

    m.drawcoastlines(color=coastline_color)
    m.drawcountries(color=border_color)
    m.fillcontinents(color=land_color, lake_color=water_color)
    m.drawstates(color=border_color)
    m.drawmapboundary(fill_color=water_color)

    x, y = m(df_gps["lon"].values, df_gps["lat"].values)
    m.scatter(
        x,
        y,
        s=5,
        color=marker_fill_color,
        edgecolor=marker_edge_color,
        alpha=0.6,
        zorder=3,
    )

    plt.savefig(
        "./google_location_history_cng_map.png",
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.2,
    )
    plt.show()
    # profile = pf.ProfileReport(df_gps, title="Report of my GPS-Data", correlations=None)
    # profile.to_file("profile_report.html")
    profile = pf.ProfileReport(df_gps, title="Report of my GPS-Data", minimal=True)
    profile.to_file("profile_report.html")


if 0:
    print(df_gps.head())
    cvs = ds.Canvas(plot_width=850, plot_height=500)
    agg = cvs.points(df_gps, "lon", "lat")
    img = ds.tf.shade(agg, cmap=colorcet.CET_L4[::-1], how="eq_hist")
    ds.utils.export_image(
        img=img, filename="histo", fmt=".png", background=None, export_path="."
    )

if 0:
    subset = df_gps.sample(frac=0.001)
    print("There are {:,} rows in the location history dataset".format(len(subset)))
    print(subset.head())
    StamenTerrain = hv.element.tiles.StamenTerrain()  # 'ESRI'
    hv_plot = subset.hvplot(
        x="easting",
        y="northing",
        tiles=StamenTerrain,
        kind="points",
        xlabel="Longitude",
        ylabel="Latitude",
        hover_cols=list(subset.columns),
    )
    show(hv.render(hv_plot))

    # import panel as pn
    # pn.serve(hv_plot)

    # hv_tiles = hv.Layout([ts().relabel(name) for name, ts in hv.element.tiles.tile_sources.items()]).opts(
    #     hv.opts.Tiles(xaxis=None, yaxis=None, width=225, height=225)).cols(4)
    # show(hv.render(hv_tiles))

if 1:
    esri = (
        hv.element.tiles.ESRI()
        .redim(x="easting", y="northing")
        .opts(xlim=(1.5e4, 4.22e5), ylim=(6.25e6, 6.7e6))
    )

    points = hv.Points(df_gps, kdims=["easting", "northing"])

    raster = hv.operation.datashader.rasterize(points).opts(
        cnorm="eq_hist", cmap=colorcet.CET_L4[::-1], responsive=True, colorbar=True
    )
    # (widt=800,xlabel='Longitude', ylabel='Latitude')

    highlight = hv.operation.datashader.inspect(raster).opts(
        marker="o", size=10, fill_alpha=0, color="white", tools=["hover"]
    )
    overlay = (
        esri * raster.opts(cmap="fire", cnorm="eq_hist", min_height=400) * highlight
    )

    # pn.Column('## Test')
    # show(hv.render(hv_plot))

    pn.serve(overlay)

    # hv_tiles = hv.Layout([ts().relabel(name) for name, ts in hv.element.tiles.tile_sources.items()]).opts(
    #     hv.opts.Tiles(xaxis=None, yaxis=None, width=225, height=225)).cols(4)
    # show(hv.render(hv_tiles))
print("end")
