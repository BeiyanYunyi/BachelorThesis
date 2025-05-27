from os import path
import numpy as np
import xarray
from matplotlib.colors import ListedColormap
from .era5 import (
    download_single_level_data,
    download_geopotential_data,
    download_single_station_data,
)
import zipfile


current_dir = path.dirname(__file__)

try:
    surface_data = xarray.open_dataset(path.join(current_dir, "surface.nc"))
except FileNotFoundError:
    if not path.exists(path.join(current_dir, "surface.zip")):
        print("Single level data not found, attempt downloading...")
        download_single_level_data()
    print("Extracting single level data from zip file...")
    with zipfile.ZipFile(path.join(current_dir, "surface.zip"), "r") as zip_ref:
        with (
            zip_ref.open("data_stream-oper_stepType-instant.nc") as source,
            open(path.join(current_dir, "surface.nc"), "wb") as target,
        ):
            target.write(source.read())
    surface_data = xarray.open_dataset(path.join(current_dir, "surface.nc"))

surface_data["msl"] /= 100

try:
    geopotential_data = xarray.open_dataset(path.join(current_dir, "geopotential.nc"))
except FileNotFoundError:
    print("Geopotential data not found, attempt downloading...")
    download_geopotential_data()
    geopotential_data = xarray.open_dataset(path.join(current_dir, "geopotential.nc"))

geopotential_data["z"] /= 98.1

try:
    single_station_data = xarray.open_dataset(
        path.join(current_dir, "single_station.nc")
    )
except FileNotFoundError:
    print("Single station data not found, attempt downloading...")
    download_single_station_data()
    single_station_data = xarray.open_dataset(
        path.join(current_dir, "single_station.nc")
    )

radar_colors = [
    "#04e9e7",
    "#019ff4",
    "#0300f4",
    "#02fd02",
    "#01c501",
    "#008e00",
    "#fdf802",
    "#e5bc00",
    "#fd9500",
    "#fd0000",
    "#d40000",
    "#bc0000",
    "#f800fd",
]

radar_cmap = ListedColormap(radar_colors)
radar_cmap.set_under("#ffffff")
radar_cmap.set_over("#9854c6")
radar_levels = np.arange(0, 66, 5)
