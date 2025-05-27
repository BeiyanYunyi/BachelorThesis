from cartopy.io import shapereader
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cartopy.feature as cfeature
from cartopy.mpl.geoaxes import GeoAxes
import matplotlib
from os import path
from scipy.ndimage import gaussian_filter

import numpy as np
from xarray import Dataset

current_dir = path.dirname(__file__)


class Map:
    """
    “图”类，封装了一些常用的地图绘制方法。需传入若干参数来初始化。
    """

    data: Dataset
    ax: GeoAxes

    def __init__(
        self,
        data: Dataset,
        figsize=(10, 10),
        prj=ccrs.LambertConformal(central_longitude=105, central_latitude=35),
        location_color="yellow",
    ):
        """
        初始化地图对象。

        :param data: xarray Dataset，包含需要绘制的数据
        :param figsize: 图形大小，默认为(10, 10)
        :param prj: 投影方式，默认为 Lambert Conformal 投影，需要时可改 ccrs.PlateCarree() 等
        :param location_color: 龙卷发生地标记颜色，默认为黄色
        """
        self.location_color = location_color
        self.fig, self.ax = plt.subplots(
            figsize=figsize,
            subplot_kw={"projection": prj},
            layout="constrained",
        )
        self.proj = prj
        self.data = data
        if hasattr(data, "variables") and data.variables.keys().__contains__("msl"):
            self.is_surface = True
        else:
            self.is_surface = False

    def gridlines(self):
        """
        绘制经纬度网格线和经纬度标签。
        """
        gl = self.ax.gridlines(
            crs=ccrs.PlateCarree(),
            linestyle="--",
            draw_labels=True,
            xlocs=np.arange(30, 151, 10),
            ylocs=np.arange(0, 91, 10),
            x_inline=False,
            y_inline=False,
        )
        gl.xlabel_style = {
            "size": 15,
        }
        gl.ylabel_style = {
            "size": 15,
        }

        return self

    def barb_legend(self):
        """
        绘制风矢图例。实际上画的是一个黑色的竖线，代表风速2m/s。
        """
        import matplotlib.lines as mlines

        sc = self.draw_tornado_location()
        legend_entry = mlines.Line2D(
            [],
            [],
            color="black",
            marker="|",
            markersize=10,
            linestyle="None",
            label="风速 2m/s",
        )
        self.ax.legend(handles=[legend_entry, sc], loc="lower right")
        return self

    def title(self, title: str, **fontdict: dict):
        """
        设置地图标题。

        :param title: 标题文本
        :param fontdict: 字体字典，可包含字体大小、颜色等属性

        ## Example:
        ```python
        map_instance.title("广州龙卷风", fontsize=20)
        ```
        """
        self.ax.set_title(title, **fontdict)
        return self

    def common(self):
        """
        绘制常用的地图元素，包括海岸线、省界、广州市和白云区的边界。
        """
        self.draw_coastlines().draw_province().draw_guangzhou_city().draw_baiyun_district()
        return self

    def plot(
        self,
        time: str,
        h: str | None = None,
        sigma: int | None = 1,
        sigmaT: int | None = 1,
    ):
        """
        绘制常规天气图。若初始化时传入的是单层数据，则绘制海平面气压图。
        若传入的是多层数据，则绘制等压面图，此时需要在第三个参数中传入想绘制的气压层。

        :param time: 时间字符串，格式为 "YYYY-MM-DDTHH:MM:ss"，例如 `"2024-04-27T05:00:00"`
        :param h: 气压层高度，单位 `hPa`。绘制海平面天气图时不需要传入，例如 `"850"`
        :param sigma: 高度场或压力场平滑参数，默认为 1。用于平滑数据，单位为像素。
        :param sigmaT: 温度场平滑参数，默认为 1。用于平滑温度数据，单位为像素。
        """
        if self.is_surface:
            if h != None:  # Throw error
                raise ValueError("Surface data does not have height")
            return self.plot_sf(time, sigma)
        else:
            if h == None:
                raise ValueError("Geopotential data requires height")
            return self.plot_gp(time, h, sigma, sigmaT)

    def plot_sf(self, time: str, sigma=5):
        """
        绘制海平面天气图。绘制的内容包括海平面气压等高线和 10m 风场。
        """
        data = self.data.sel(valid_time=time)
        mslp = data["msl"]
        mslp.values = gaussian_filter(mslp.values, sigma)
        ctp = mslp.plot.contour(
            extend="max",
            levels=np.arange(960, 1041, 2.5),
            # cbar_kwargs={"location": "bottom", "label": "Surface Pressure [hPa]"},
            # vmin=0,
            # vmax=100,
            add_labels=False,
            ax=self.ax,
            transform=ccrs.PlateCarree(),
            linewidths=1.5,
            colors="black",
            # add_colorbar=False,
        )
        self.ax.clabel(ctp, inline=True, fontsize=10, fmt="%2.1f")
        # sp = data.plot.streamplot(
        #     x="longitude",
        #     y="latitude",
        #     u="u10",
        #     v="v10",
        #     ax=self.ax,
        #     transform=ccrs.PlateCarree(),
        #     # color="k",
        #     # density=2,
        # )
        datab = data.sel(
            longitude=slice(None, None, 20),
            latitude=slice(None, None, 20),
        )
        self.ax.barbs(
            x=datab.longitude.values,
            y=datab.latitude.values,
            u=datab.u10.values,
            v=datab.v10.values,
            transform=ccrs.PlateCarree(),
            barb_increments=dict(half=2, full=4, flag=20),
            sizes={"emptybarb": 0},
        )
        self.gridlines().barb_legend()
        self.ax.add_feature(cfeature.OCEAN, linewidth=1.5, color="lightblue")
        self.ax.add_feature(cfeature.LAND)
        return self

    def plot_gp(self, time: str, h: str, sigma=1, sigmaT=1):
        """
        绘制等压面天气图。绘制的内容包括等压面高度场、温度场和风速场。
        """
        data = self.data.sel(valid_time=time, pressure_level=h)
        data["wind_speed"] = np.sqrt(data["u"] ** 2 + data["v"] ** 2)
        data["wind_speed"].plot.contourf(
            extend="max",
            levels=np.arange(15, 31, 3) if h == "500" else np.arange(6, 24, 3),
            cbar_kwargs={"location": "bottom", "label": "风速 [m/s]"},
            vmin=15,
            cmap="YlOrBr",
            # vmax=100,
            add_labels=False,
            ax=self.ax,
            transform=ccrs.PlateCarree(),
            # add_colorbar=False
        )
        datab = data.sel(
            longitude=slice(None, None, 15),
            latitude=slice(None, None, 15),
        )
        self.ax.barbs(
            x=datab.longitude.values,
            y=datab.latitude.values,
            u=datab.u.values,
            v=datab.v.values,
            transform=ccrs.PlateCarree(),
            barb_increments=dict(half=2, full=4, flag=20),
            sizes={"emptybarb": 0},
        )
        gpz = data["z"]
        gpz.values = gaussian_filter(gpz.values, sigma)
        ct = gpz.plot.contour(
            levels=np.arange(0, 1000, 4),
            linewidths=1.5,
            transform=ccrs.PlateCarree(),
            colors="black",
        )
        self.ax.clabel(ct, inline=True, fontsize=10, fmt="%1.0f")
        celciusT = data["t"] - 273
        celciusT.values = gaussian_filter(celciusT.values, sigmaT)
        ctt = celciusT.plot.contour(
            levels=np.arange(-40, 41, 4),
            transform=ccrs.PlateCarree(),
            colors="red",
            linestyles="solid",
        )
        self.ax.clabel(ctt, inline=True, fontsize=10)
        self.gridlines().barb_legend()
        return self

    def draw_china(self):
        """
        绘制中国地图的边界。使用了中国行政区划的 shapefile 数据。
        """
        cn_shape_path = path.join(
            current_dir, "ChinaAdminDivisonSHP/1. Country/country.shp"
        )
        cn_reader = shapereader.Reader(cn_shape_path)
        for record in cn_reader.records():
            self.ax.add_geometries(
                [record.geometry],
                ccrs.PlateCarree(),
                facecolor="none",
                edgecolor="black",
                # linewidths=0.5,
            )
        return self

    def draw_coastlines(self):
        """
        绘制海岸线。使用 Cartopy 的内置海岸线特征。
        这将添加黑色的海岸线到地图上。
        """
        self.ax.add_feature(cfeature.COASTLINE, edgecolor="black")

        return self

    def draw_province(self):
        """
        绘制中国的省级行政区划边界。使用了中国行政区划的 shapefile 数据。
        目前仅绘制广东、香港和澳门。
        """
        provinces = [
            "广东省",
            "香港特别行政区",
            "澳门特别行政区",
        ]
        # pr_shape_path = "./ChinaAdminDivisonSHP/2. Province/province.shp"
        pr_shape_path = path.join(
            current_dir, "ChinaAdminDivisonSHP/2. Province/province.shp"
        )
        pr_reader = shapereader.Reader(pr_shape_path)
        for record in pr_reader.records():
            if record.attributes["pr_name"] in provinces:
                self.ax.add_geometries(
                    [record.geometry],
                    ccrs.PlateCarree(),
                    facecolor="none",
                    edgecolor="black",
                )
        return self

    def draw_guangzhou_city(self):
        """
        绘制广州市的边界。使用了中国行政区划的 shapefile 数据。
        """
        ct_shape_path = path.join(current_dir, "ChinaAdminDivisonSHP/3. City/city.shp")
        ct_reader = shapereader.Reader(ct_shape_path)
        for record in ct_reader.records():
            if record.attributes["ct_name"] == "广州市":
                self.ax.add_geometries(
                    [record.geometry],
                    ccrs.PlateCarree(),
                    facecolor="none",
                    edgecolor="black",
                )
        return self

    def draw_baiyun_district(self):
        """
        绘制广州市白云区的边界。使用了中国行政区划的 shapefile 数据。
        """
        dt_shape_path = path.join(
            current_dir, "ChinaAdminDivisonSHP/4. District/district.shp"
        )
        dt_reader = shapereader.Reader(dt_shape_path)
        for record in dt_reader.records():
            if (
                record.attributes["ct_name"]
                == "广州市"  # To avoid confusion with other cities
                and record.attributes["dt_name"] == "白云区"
            ):
                self.ax.add_geometries(
                    [record.geometry],
                    ccrs.PlateCarree(),
                    facecolor="none",
                    edgecolor="black",
                )
        return self

    def draw_tornado_location(self, add_legend=False):
        """
        绘制龙卷发生地的标记。使用 Cartopy 的 scatter 方法在地图上添加一个星形标记。

        :param add_legend: 是否添加图例，默认为 False
        """
        tlat, tlon = 23.336291695619014, 113.4180102524545
        sc = self.ax.scatter(
            [tlon],
            [tlat],
            marker="*",
            color=self.location_color,
            s=[100],
            # markersize=12,
            transform=ccrs.Geodetic(),
            label="龙卷发生地",
            alpha=0.75,
            zorder=10,
        )
        if add_legend:
            self.ax.legend(loc="lower right")
        return sc

    def utm_from_lon(self, lon):
        """
        utm_from_lon - UTM zone for a longitude

         Not right for some polar regions (Norway, Svalbard, Antartica)

         :param float lon: longitude
         :return: UTM zone number
         :rtype: int
        """
        from math import floor

        return floor((lon + 180) / 6) + 1

    def scale_bar(
        self,
        length,
        location=(0.5, 0.05),
        linewidth=3,
        units="km",
        m_per_unit=1000,
    ):
        """
        绘制比例尺图例
        """
        from matplotlib import patheffects

        ax = self.ax
        proj = self.proj
        # find lat/lon center to find best UTM zone
        x0, x1, y0, y1 = ax.get_extent(proj.as_geodetic())
        # Projection in metres
        utm = ccrs.UTM(self.utm_from_lon((x0 + x1) / 2))
        # Get the extent of the plotted area in coordinates in metres
        x0, x1, y0, y1 = ax.get_extent(utm)
        # Turn the specified scalebar location into coordinates in metres
        sbcx, sbcy = x0 + (x1 - x0) * location[0], y0 + (y1 - y0) * location[1]
        # Generate the x coordinate for the ends of the scalebar
        bar_xs = [sbcx - length * m_per_unit / 2, sbcx + length * m_per_unit / 2]
        # buffer for scalebar
        buffer = [patheffects.withStroke(linewidth=5, foreground="w")]
        # Plot the scalebar with buffer
        ax.plot(
            bar_xs,
            [sbcy, sbcy],
            transform=utm,
            color="k",
            linewidth=linewidth,
            path_effects=buffer,
        )
        # buffer for text
        buffer = [patheffects.withStroke(linewidth=3, foreground="w")]
        # Plot the scalebar label
        t0 = ax.text(
            sbcx,
            sbcy,
            str(length) + " " + units,
            transform=utm,
            horizontalalignment="center",
            verticalalignment="bottom",
            path_effects=buffer,
            zorder=2,
        )
        left = x0 + (x1 - x0) * 0.05
        # Plot the N arrow
        t1 = ax.text(
            left,
            sbcy,
            "\u25b2\nN",
            transform=utm,
            horizontalalignment="center",
            verticalalignment="bottom",
            path_effects=buffer,
            zorder=2,
        )
        # Plot the scalebar without buffer, in case covered by text buffer
        ax.plot(
            bar_xs,
            [sbcy, sbcy],
            transform=utm,
            color="k",
            linewidth=linewidth,
            zorder=3,
        )
