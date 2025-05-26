from os import path
import numpy as np
import xarray
from matplotlib.colors import ListedColormap


current_dir = path.dirname(__file__)

surface_data = xarray.open_dataset(path.join(current_dir, "surface.nc")).sel(
    # longitude=np.arange(105, 121, 0.25),
    # latitude=np.arange(20, 31, 0.25),
)
surface_data["msl"] /= 100

geopotential_data = xarray.open_dataset(path.join(current_dir, "geopotential.nc")).sel(
    # longitude=np.arange(105, 121, 0.25),
    # latitude=np.arange(20, 31, 0.25),
)
geopotential_data["z"] /= 98.1

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
