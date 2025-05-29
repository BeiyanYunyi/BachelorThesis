"""
图 2.2、图 4.11 和 图 4.12 的绘制
"""

from netCDF4 import Dataset
from wrf import (
    getvar,
    latlon_coords,
    get_cartopy,
    to_np,
    interplevel,
    CoordPair,
    vertcross,
)
import cartopy.crs as ccrs
from lib import Map, radar_cmap, radar_levels
from scipy.ndimage import gaussian_filter
import numpy as np
from matplotlib import pyplot as plt
from os import path

current_dir = path.dirname(__file__)


def draw_p2_2():
    """
    图2.2，2024 年 4 月 27 日 15 时 WRF D03 嵌套区域内 300m 单层反射率
    """
    ds = Dataset(path.join(current_dir, "../wrfout/d03/wrfout_d01_2024-04-27_15_00_00"))
    dbz = getvar(ds, "dbz")
    z = getvar(ds, "z", msl=False, units="m")

    dbz_300 = interplevel(dbz, z, 300.0)

    lats, lons = latlon_coords(dbz_300)
    cart_proj = get_cartopy(dbz_300)
    map = Map(
        dbz_300,
        prj=cart_proj,
        location_color="red",
    ).common()

    ctp = map.ax.contourf(
        to_np(lons),
        to_np(lats),
        to_np(dbz_300),
        vmin=0,
        vmax=65,
        # add_labels=False,
        levels=radar_levels,
        transform=ccrs.PlateCarree(),
        cmap=radar_cmap,
        extend="both",
    )
    map.fig.colorbar(
        ctp,
        location="bottom",
        label="Reflectivity [dBZ]",
    )
    map.draw_tornado_location()
    map.ax.legend(loc="lower right")
    map.title("WRF 2024-04-27 15:00:00 离地 300m 反射率 (dBZ)", fontsize=20)
    # map.fig.savefig("./images/wrf/wrf_dbz.svg", dpi=300)


def draw_p4_11():
    ds = Dataset(path.join(current_dir, "../wrfout/d04/wrfout_d01_2024-04-27_15_00_00"))
    # ds = Dataset("./mmt/广东白云区龙卷_WRF模拟数据/d03/wrfout_d01_2024-04-27_07_00_00")
    z = getvar(ds, "z")
    avo = getvar(ds, "avo")
    avo_500 = interplevel(avo, z, 1000.0)
    lats, lons = latlon_coords(avo_500)
    cart_proj = get_cartopy(avo_500)
    map = Map(
        avo_500,
        prj=cart_proj,
        location_color="red",
    ).common()

    avo_500_filtered = gaussian_filter(avo_500, sigma=5)

    ctp = map.ax.contourf(
        to_np(lons),
        to_np(lats),
        to_np(avo_500_filtered),
        extend="max",
        levels=np.arange(800, 1200, 100),
        transform=ccrs.PlateCarree(),
        linewidths=1.5,
    )
    map.fig.colorbar(
        ctp, ax=map.ax, location="bottom", label="绝对涡度 [$10^{-5}\\rm s^{-1}$]"
    )
    map.draw_tornado_location()
    map.title("WRF 2024-04-27 15:00:00 海拔 1km 绝对涡度", fontsize=20)
    map.scale_bar(5, location=(0.1, 0.95))
    tlat, tlon = 23.238, 113.75
    sc = map.ax.scatter(
        [tlon],
        [tlat],
        marker="*",
        # color=self.location_color,
        s=[100],
        # markersize=12,
        transform=ccrs.Geodetic(),
        label="垂直剖面路径中点",
        alpha=0.75,
        zorder=10,
    )
    # latf = 0.05
    latf = 0.025
    # lonf = latf / 3 * 7
    lonf = latf * 12
    # Set the start point and end point for the cross section
    start_point = CoordPair(lat=tlat - latf, lon=tlon - lonf)
    end_point = CoordPair(lat=tlat + latf, lon=tlon + lonf)
    map.ax.plot(
        [start_point.lon, end_point.lon],
        [start_point.lat, end_point.lat],
        color="green",
        marker="o",
        transform=ccrs.PlateCarree(),
        zorder=3,
        label="垂直剖面路径",
    )
    map.ax.legend(loc="lower right")
    # map.fig.savefig("./images/wrf/wrf_vort.svg")


def draw_p4_12():
    """
    图4.12 2024 年 4 月 27 日 15 时海拔 1km 单层反射率图与垂直剖面图
    """
    # Open the NetCDF file
    ncfile = Dataset(
        path.join(current_dir, "../wrfout/d04/wrfout_d01_2024-04-27_15_00_00")
    )

    # Get the WRF variables
    slp = getvar(ncfile, "slp")
    # ctt = getvar(ncfile, "mdbz")
    z = getvar(ncfile, "z")
    dbz = getvar(ncfile, "dbz")
    Z = 10 ** (dbz / 10.0)
    wspd = getvar(ncfile, "wspd_wdir", units="m/s")[0, :]
    ctt = interplevel(dbz, z, 1000)

    latf = 0.025
    # lonf = latf / 3 * 7
    lonf = latf * 12
    # Set the start point and end point for the cross section
    tlat, tlon = 23.238, 113.75
    start_point = CoordPair(lat=tlat - latf, lon=tlon - lonf)
    end_point = CoordPair(lat=tlat + latf, lon=tlon + lonf)

    # Compute the vertical cross-section interpolation.  Also, include the
    # lat/lon points along the cross-section in the metadata by setting latlon
    # to True.
    z_cross = vertcross(
        Z,
        z,
        wrfin=ncfile,
        start_point=start_point,
        end_point=end_point,
        latlon=True,
        meta=True,
    )
    wspd_cross = vertcross(
        wspd,
        z,
        wrfin=ncfile,
        start_point=start_point,
        end_point=end_point,
        latlon=True,
        meta=True,
    )
    dbz_cross = 10.0 * np.log10(z_cross)

    # Get the lat/lon points
    lats, lons = latlon_coords(slp)

    # Get the cartopy projection object
    cart_proj = get_cartopy(slp)

    # Create a figure that will have 3 subplots
    fig = plt.figure(figsize=(12, 12))
    ax_ctt = fig.add_subplot(1, 2, 1, projection=cart_proj)
    ax_wspd = fig.add_subplot(2, 2, 2)
    ax_dbz = fig.add_subplot(2, 2, 4)

    # Create the filled cloud top temperature contours
    # contour_levels = [-80.0, -70.0, -60, -50, -40, -30, -20, -10, 0, 10]
    ctt_contours = ax_ctt.contourf(
        to_np(lons),
        to_np(lats),
        to_np(ctt),
        # contour_levels,
        cmap=radar_cmap,
        transform=ccrs.PlateCarree(),
        extend="both",
        zorder=2,
        levels=radar_levels,
    )

    ax_ctt.plot(
        [start_point.lon, end_point.lon],
        [start_point.lat, end_point.lat],
        color="yellow",
        marker="o",
        transform=ccrs.PlateCarree(),
        zorder=3,
    )

    ax_ctt.scatter(
        [tlon],
        [tlat],
        color="red",
        marker="o",
        s=50,
        zorder=3,
        transform=ccrs.PlateCarree(),
    )

    # Create the color bar for cloud top temperature
    cb_ctt = fig.colorbar(
        ctt_contours,
        ax=ax_ctt,
        shrink=0.60,
        location="bottom",
        label="Reflectivity (dBZ)",
    )
    cb_ctt.ax.tick_params(labelsize=12)
    ax_ctt.gridlines(color="white", linestyle="dotted")

    # Make the contour plot for wind speed
    wspd_contours = ax_wspd.contourf(
        to_np(wspd_cross), cmap=radar_cmap, levels=radar_levels
    )
    # Add the color bar
    cb_wspd = fig.colorbar(wspd_contours, ax=ax_wspd)
    cb_wspd.ax.tick_params(labelsize=10)

    # Make the contour plot for dbz
    # levels = [5 + 5 * n for n in range(15)]
    dbz_contours = ax_dbz.contourf(
        to_np(dbz_cross), cmap=radar_cmap, levels=radar_levels, extend="both"
    )
    cb_dbz = fig.colorbar(dbz_contours, ax=ax_dbz)
    cb_dbz.ax.tick_params(labelsize=10)

    # Set the x-ticks to use latitude and longitude labels
    coord_pairs = to_np(dbz_cross.coords["xy_loc"])
    x_ticks = np.arange(coord_pairs.shape[0])
    x_labels = [pair.latlon_str() for pair in to_np(coord_pairs)]
    ax_wspd.set_xticks(x_ticks[::20])
    ax_wspd.set_xticklabels([], rotation=45)
    ax_dbz.set_xticks(x_ticks[::40])
    ax_dbz.set_xticklabels(x_labels[::40], rotation=90, fontsize=10)

    # Set the y-ticks to be height
    vert_vals = to_np(dbz_cross.coords["vertical"])
    v_ticks = np.arange(vert_vals.shape[0])
    ax_wspd.set_yticks(v_ticks[::20])
    ax_wspd.set_yticklabels(vert_vals[::20], fontsize=10)
    ax_dbz.set_yticks(v_ticks[::20])
    ax_dbz.set_yticklabels(vert_vals[::20], fontsize=10)

    # Set the x-axis and  y-axis labels
    ax_dbz.set_xlabel("纬度, 经度", fontsize=12)
    ax_wspd.set_ylabel("海拔高度 (m)", fontsize=12)
    ax_dbz.set_ylabel("海拔高度 (m)", fontsize=12)

    # Add a title
    ax_ctt.set_title("海拔1km反射率 (dBZ)", {"fontsize": 16})
    ax_wspd.set_title("垂直剖面风速 (m/s)", {"fontsize": 16})
    ax_dbz.set_title("垂直剖面反射率 (dBZ)", {"fontsize": 16})
    # plt.savefig(
    #     "./images/wrf/wrf_cross_section.svg",
    #     # dpi=300,
    # )
