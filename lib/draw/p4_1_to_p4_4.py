"""
图 4.1 至 4.4，ERA5 大尺度形势图
"""

from ..map import Map
from ..data import geopotential_data, surface_data


def draw_p4_1():
    """
    图4.1，500hPa 大尺度形势图
    """
    title = "2024-04-27 13:00:00 CST 500hPa"
    map = (
        Map(geopotential_data, location_color="blue")
        .common()
        .plot("2024-04-27T05:00:00", "500", sigmaT=5, sigma=5)
        .title(title, fontsize=20)
    )
    # map.fig.savefig(f"images/{title}.svg")


def draw_p4_2():
    """
    图4.2，700hPa 大尺度形势图
    """
    title = "2024-04-27 13:00:00 CST 700hPa"
    map = (
        Map(geopotential_data, location_color="blue")
        .common()
        .plot("2024-04-27T05:00:00", "700", sigmaT=5, sigma=5)
        .title(title, fontsize=20)
    )
    # map.fig.savefig(f"images/{title}.svg")


def draw_p4_3():
    """
    图4.3，850hPa 大尺度形势图
    """
    title = "2024-04-27 13:00:00 CST 850hPa"
    map = (
        Map(geopotential_data, location_color="blue")
        .common()
        .plot("2024-04-27T05:00:00", "850", sigmaT=5, sigma=5)
        .title(title, fontsize=20)
    )
    # map.fig.savefig(f"images/{title}.svg")


def draw_p4_4():
    """
    图4.4，海平面大尺度形势图
    """
    title = "2024-04-27 13:00:00 CST 海平面"
    map = (
        Map(surface_data, location_color="red")
        .common()
        .plot("2024-04-27T05:00:00", sigma=5)
        .title(title, fontsize=20)
    )
    # map.fig.savefig(f"images/{title}.svg")
