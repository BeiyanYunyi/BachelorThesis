"""
图 4.5-4.7，一些诊断量图和中分析图的绘制
"""

from typing import Literal
from lib import Map, surface_data, geopotential_data
import numpy as np
import cartopy.crs as ccrs
from matplotlib import patheffects
from scipy.ndimage import gaussian_filter
from metpy.calc import dewpoint_from_specific_humidity, divergence
from metpy.units import units


def draw_p4_5a():
    """
    图4.5a，整层水汽通量图
    """
    map = Map(
        surface_data,
        prj=ccrs.PlateCarree(),
    )
    map.common()
    pl = map.data.sel(
        valid_time="2024-04-27T05:00:00",
    )
    viw = (pl["viwve"] ** 2 + pl["viwvn"] ** 2) ** 0.5
    viw.plot.contourf(
        levels=np.arange(0, 801, 100),
        vmax=800,
        cmap="Greens",
        cbar_kwargs={
            "location": "bottom",
            "label": "水汽通量 [$\mathrm{kg \cdot m^{-1}\cdot s^{-1}}$]",
        },
    )
    plb = pl.sel(
        longitude=slice(None, None, 15),
        latitude=slice(None, None, 15),
    )
    quiver = plb.plot.quiver(
        "longitude",
        "latitude",
        "viwve",
        "viwvn",
        scale=5000,
        color="black",
        width=0.002,
        headlength=4,
        add_guide=False,
    )
    qk = map.ax.quiverkey(
        quiver,
        0.8,
        -0.1,
        100,
        "$ 100 \mathrm{kg \cdot m^{-1}\cdot s^{-1}}$",
        labelpos="E",
        edgecolor="red",
        fontproperties={"size": 12},
    )
    map.gridlines()
    title = "2024-04-27 13:00:00 CST 整层水汽通量"
    map.title(title, fontsize=20)
    # map.fig.savefig(f"images/{title}.svg")


def draw_p4_5b():
    """
    图4.5b，整层水汽通量散度图
    """
    map = Map(
        surface_data,
        prj=ccrs.PlateCarree(),
    )
    map.common()
    pl = map.data.sel(
        valid_time="2024-04-27T05:00:00",
    )
    viw_div = divergence(pl["viwve"], pl["viwvn"])
    viw_div.plot.contourf(
        levels=12,
        cmap="PiYG",
        cbar_kwargs={
            "location": "bottom",
            "label": "水汽通量散度 [$\mathrm{kg \cdot m^{-2}\cdot s^{-1}}$]",
        },
    )
    map.gridlines()
    title = "2024-04-27 13:00:00 CST 整层水汽通量散度"
    map.title(title, fontsize=20)
    # map.fig.savefig(f"images/{title}.svg")


def draw_p4_6():
    """
    图4.6，华南地区整层 CAPE 形势
    """
    map = Map(surface_data).common()
    map.data["cape"].sel(
        valid_time="2024-04-27T05:00:00",
        longitude=np.arange(105, 121, 0.25),
        latitude=np.arange(20, 28, 0.25),
    ).plot.contourf(
        extend="max",
        levels=np.arange(1000, 5101, 250),
        cmap="YlOrBr",
        cbar_kwargs={"location": "bottom", "label": "CAPE"},
        vmin=1000,
        # vmax=100,
        add_labels=False,
        ax=map.ax,
        transform=ccrs.PlateCarree(),
        # add_colorbar=False,)
    )
    map.draw_tornado_location()
    map.ax.legend(loc="lower right")
    title = "2024-04-27 13:00:00 CST CAPE"
    map.title(title, fontsize=20)
    # map.fig.savefig(f"images/{title}.svg")


def draw_p4_7l1():
    """
    图4.7，华南地区中分析图，第一层

    该图的绘制过程最复杂，需要多层图片相叠加，并进行一系列手动绘图

    本函数绘制 500hPa 干区与 925hPa 湿区
    """
    map = Map(
        geopotential_data.sel(
            valid_time="2024-04-27T05:00:00",
            longitude=np.arange(105, 121, 0.25),
            latitude=np.arange(20, 28, 0.25),
        ),
        prj=ccrs.LambertConformal(central_longitude=112, central_latitude=35),
        location_color="red",
    ).common()
    data925 = map.data.sel(pressure_level="925")
    t925 = data925["t"]
    td925 = dewpoint_from_specific_humidity(
        925 * units.hPa, specific_humidity=data925["q"]
    )
    t_td925 = t925 * units.K - td925
    data500 = map.data.sel(pressure_level="500")
    t500 = data500["t"]
    td500 = dewpoint_from_specific_humidity(
        500 * units.hPa, specific_humidity=data500["q"]
    )
    t_td500 = t500 * units.K - td500

    t_td925.values = gaussian_filter(t_td925.values, 2)
    ct = t_td925.plot.contour(
        extend="max",
        levels=[5],
        colors="green",
        vmax=5,
        add_labels=False,
        ax=map.ax,
        transform=ccrs.PlateCarree(),
    )
    ct.set(
        path_effects=[patheffects.withTickedStroke(angle=-90, length=0.5, spacing=20)]
    )
    map.ax.clabel(ct)
    t_td500.values = gaussian_filter(t_td500.values, 2)
    ct = t_td500.plot.contour(
        extend="max",
        levels=[15],
        colors="gold",
        vmax=15,
        add_labels=False,
        ax=map.ax,
        transform=ccrs.PlateCarree(),
        # add_colorbar=False,))
    )
    ct.set(
        path_effects=[patheffects.withTickedStroke(angle=90, length=0.5, spacing=20)]
    )
    map.ax.clabel(ct)
    map.draw_tornado_location(add_legend=True)
    title = "2024-04-27 13:00:00 CST 中分析图"
    map.title(title, fontsize=20)
    # map.fig.savefig(f"images/{title}.svg")


def draw_p4_7l2(h: Literal["925", "850", "700", "500"]):
    """
    图4.7，华南地区中分析图，第二层

    该图的绘制过程最复杂，需要多层图片相叠加，并进行一系列手动绘图

    本函数绘制 925hPa、850hPa、700hPa 与 500hPa 的等压线与风场，随后在 Figma 中相叠加
    """

    map = Map(
        geopotential_data.sel(
            valid_time="2024-04-27T05:00:00",
            longitude=np.arange(105, 121, 0.25),
            latitude=np.arange(20, 28, 0.25),
        ),
        prj=ccrs.LambertConformal(central_longitude=112, central_latitude=35),
        location_color="red",
    ).common()
    map.ax.set_extent([105, 121, 20, 28])
    datab = map.data.sel(pressure_level=h)
    z = datab["z"]
    z.values = gaussian_filter(z.values, 2)
    ct = z.plot.contour(
        levels=np.arange(0, 1000, 4),
        linewidths=1.5,
        transform=ccrs.PlateCarree(),
        colors="black",
        ax=map.ax,
    )
    map.ax.clabel(ct, inline=True, fontsize=10, fmt="%1.0f")
    datab = map.data.sel(pressure_level=h)
    map.ax.streamplot(
        x=datab.longitude.values,
        y=datab.latitude.values,
        u=datab.u.values,
        v=datab.v.values,
        transform=ccrs.PlateCarree(),
    )

    map.draw_tornado_location(add_legend=True)

    map.title(h, fontsize=20)
    # map.fig.savefig(f"images/levels/{h}.svg")
