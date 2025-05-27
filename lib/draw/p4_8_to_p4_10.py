"""
图 4.8-4.10，T-lnP 图的绘制
"""

from metpy.units import units
from pint import Quantity
import metpy.calc as mpcalc
import numpy as np
import matplotlib.pyplot as plt
from metpy.plots import SkewT, Hodograph


def draw(
    T: Quantity,
    p: Quantity,
    Td: Quantity,
    u: Quantity,
    v: Quantity,
    z: Quantity,
    title: str,
    save_path: str,
):
    """
    从预处理好的数据中绘制 T-lnP 图和风矢图，附带一系列诊断量

    :param T: 温度数据，单位为摄氏度
    :param p: 气压数据，单位为百帕
    :param Td: 露点温度数据，单位为摄氏度
    :param u: U 分量风速数据，单位为米每秒
    :param v: V 分量风速数据，单位为米每秒
    :param z: 高度数据，单位为米
    :param title: 图表标题
    :param save_path: 保存图表的路径
    """
    plt.rcParams["font.family"] = ["Heiti TC", "sans-serif"]

    # STEP 1: CREATE THE SKEW-T OBJECT AND MODIFY IT TO CREATE A
    # NICE, CLEAN PLOT
    # Create a new figure. The dimensions here give a good aspect ratio
    fig = plt.figure(figsize=(18, 12))
    skew = SkewT(fig, rotation=45, rect=(0.08, 0.08, 0.47, 0.87))

    # add the Metpy logo
    # add_metpy_logo(fig, 105, 85, size='small')

    # Change to adjust data limits and give it a semblance of what we want
    skew.ax.set_adjustable("datalim")
    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlim(-20, 30)

    # Set some better labels than the default to increase readability
    skew.ax.set_xlabel(f"温度 ({T.units:~P})", weight="bold", fontsize=20)
    skew.ax.set_ylabel(f"气压 ({p.units:~P})", weight="bold", fontsize=20)
    skew.ax.xaxis.set_tick_params(labelsize=20)
    skew.ax.yaxis.set_tick_params(labelsize=20)

    # Set the facecolor of the skew-t object and the figure to white
    fig.set_facecolor("#ffffff")
    skew.ax.set_facecolor("#ffffff")

    # Here we can use some basic math and Python functionality to make a cool
    # shaded isotherm pattern.
    x1 = np.linspace(-100, 40, 8)
    x2 = np.linspace(-90, 50, 8)
    y = [1100, 50]
    for i in range(0, 8):
        skew.shade_area(y=y, x1=x1[i], x2=x2[i], color="gray", alpha=0.02, zorder=1)

    # STEP 2: PLOT DATA ON THE SKEW-T. TAKE A COUPLE EXTRA STEPS TO
    # INCREASE READABILITY
    # Plot the data using normal plotting functions, in this case using
    # log scaling in Y, as dictated by the typical meteorological plot
    # Set the linewidth to 4 for increased readability.
    # We will also add the 'label' keyword argument for our legend.
    skew.plot(p, T, "r", lw=4, label="气温")
    skew.plot(p, Td, "g", lw=4, label="露点温度")

    # Again we can use some simple Python math functionality to 'resample'
    # the wind barbs for a cleaner output with increased readability.
    # Something like this would work.
    interval = np.logspace(2, 3, 40) * units.hPa
    idx = mpcalc.resample_nn_1d(p, interval)
    skew.plot_barbs(
        pressure=p[idx],
        u=u[idx],
        v=v[idx],
        barb_increments=dict(half=2, full=4, flag=20),
        sizes={"emptybarb": 0},
    )

    # Add the relevant special lines native to the Skew-T Log-P diagram &
    # provide basic adjustments to linewidth and alpha to increase readability
    # first, we add a matplotlib axvline to highlight the 0-degree isotherm
    skew.ax.axvline(0 * units.degC, linestyle="--", color="blue", alpha=0.3)
    skew.plot_dry_adiabats(lw=1, alpha=0.3)
    skew.plot_moist_adiabats(lw=1, alpha=0.3)
    skew.plot_mixing_lines(lw=1, alpha=0.3)

    # Calculate LCL height and plot as a black dot. Because `p`'s first value is
    # ~1000 mb and its last value is ~250 mb, the `0` index is selected for
    # `p`, `T`, and `Td` to lift the parcel from the surface. If `p` was inverted,
    # i.e. start from a low value, 250 mb, to a high value, 1000 mb, the `-1` index
    # should be selected.
    lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
    skew.plot(lcl_pressure, lcl_temperature, "ko", markerfacecolor="black", label="LCL")
    # Calculate full parcel profile and add to plot as black line
    prof = mpcalc.parcel_profile(p, T[0], Td[0]).to("degC")
    skew.plot(p, prof, "k", linewidth=2, label="状态曲线")

    # Shade areas of CAPE and CIN
    skew.shade_cin(p, T, prof, Td, alpha=0.2, label="CIN")
    skew.shade_cape(p, T, prof, alpha=0.2, label="CAPE")

    # STEP 3: CREATE THE HODOGRAPH INSET. TAKE A FEW EXTRA STEPS TO
    # INCREASE READABILITY
    # Create a hodograph object: first we need to add an axis
    # then we can create the Metpy Hodograph
    hodo_ax = plt.axes((0.48, 0.45, 0.5, 0.5))
    h = Hodograph(hodo_ax, component_range=80.0)

    # Add two separate grid increments for a cooler look. This also
    # helps to increase readability
    h.add_grid(increment=20, ls="-", lw=1.5, alpha=0.5)
    h.add_grid(increment=10, ls="--", lw=1, alpha=0.2)

    # The next few steps makes for a clean hodograph inset, removing the
    # tick marks, tick labels, and axis labels
    h.ax.set_box_aspect(1)
    h.ax.set_yticklabels([])
    h.ax.set_xticklabels([])
    h.ax.set_xticks([])
    h.ax.set_yticks([])
    h.ax.set_xlabel(" ")
    h.ax.set_ylabel(" ")

    # Here we can add a simple Python for loop that adds tick marks
    # to the inside of the hodograph plot to increase readability!
    plt.xticks(np.arange(0, 0, 1))
    plt.yticks(np.arange(0, 0, 1), fontsize=20)
    for i in range(10, 120, 10):
        h.ax.annotate(
            str(i),
            (i, 0),
            xytext=(0, 2),
            textcoords="offset pixels",
            clip_on=True,
            fontsize=20,
            weight="bold",
            alpha=0.3,
            zorder=0,
        )
    for i in range(10, 120, 10):
        h.ax.annotate(
            str(i),
            (0, i),
            xytext=(0, 2),
            textcoords="offset pixels",
            clip_on=True,
            fontsize=20,
            weight="bold",
            alpha=0.3,
            zorder=0,
        )

    # plot the hodograph itself, using plot_colormapped, colored
    # by height
    # filter z to below 12km
    filtered_z = z[z < 12000 * units.m]
    lenz = len(filtered_z)
    filtered_u = u[:lenz]
    filtered_v = v[:lenz]
    h.plot_colormapped(filtered_u, filtered_v, c=filtered_z, label="0-12km 风矢连线")
    # compute Bunkers storm motion so we can plot it on the hodograph!
    RM, LM, MW = mpcalc.bunkers_storm_motion(p, u, v, z)
    h.ax.text(
        (RM[0].m + 0.5),
        (RM[1].m - 0.5),
        "RM",
        weight="bold",
        ha="left",
        fontsize=13,
        alpha=0.6,
    )
    h.ax.text(
        (LM[0].m + 0.5),
        (LM[1].m - 0.5),
        "LM",
        weight="bold",
        ha="left",
        fontsize=13,
        alpha=0.6,
    )
    h.ax.text(
        (MW[0].m + 0.5),
        (MW[1].m - 0.5),
        "MW",
        weight="bold",
        ha="left",
        fontsize=13,
        alpha=0.6,
    )
    h.ax.arrow(
        0,
        0,
        RM[0].m - 0.3,
        RM[1].m - 0.3,
        linewidth=2,
        color="black",
        alpha=0.2,
        label="Bunkers 右偏向量",
        length_includes_head=True,
        head_width=2,
    )

    # STEP 4: ADD A FEW EXTRA ELEMENTS TO REALLY MAKE A NEAT PLOT
    # First we want to actually add values of data to the plot for easy viewing
    # To do this, let's first add a simple rectangle using Matplotlib's 'patches'
    # functionality to add some simple layout for plotting calculated parameters
    #                                  xloc   yloc   xsize  ysize
    fig.patches.extend(
        [
            plt.Rectangle(
                (0.563, 0.08),
                0.334,
                0.34,
                edgecolor="black",
                facecolor="white",
                linewidth=1,
                alpha=1,
                transform=fig.transFigure,
                figure=fig,
            )
        ]
    )

    # Now let's take a moment to calculate some simple severe-weather parameters using
    # metpy's calculations
    # Here are some classic severe parameters!
    kindex = mpcalc.k_index(p, T, Td)
    total_totals = mpcalc.total_totals_index(p, T, Td)

    # mixed layer parcel properties!
    ml_t, ml_td = mpcalc.mixed_layer(p, T, Td, depth=50 * units.hPa)
    ml_p, _, _ = mpcalc.mixed_parcel(p, T, Td, depth=50 * units.hPa)
    mlcape, mlcin = mpcalc.mixed_layer_cape_cin(p, T, prof, depth=50 * units.hPa)

    # most unstable parcel properties!
    mu_p, mu_t, mu_td, _ = mpcalc.most_unstable_parcel(p, T, Td, depth=50 * units.hPa)
    mucape, mucin = mpcalc.most_unstable_cape_cin(p, T, Td, depth=50 * units.hPa)

    # Estimate height of LCL in meters from hydrostatic thickness (for sig_tor)
    new_p = np.append(p[p > lcl_pressure], lcl_pressure)
    new_t = np.append(T[p > lcl_pressure], lcl_temperature)
    lcl_height = mpcalc.thickness_hydrostatic(new_p, new_t)

    # Compute Surface-based CAPE
    sbcape, sbcin = mpcalc.surface_based_cape_cin(p, T, Td)
    # Compute SRH
    (u_storm, v_storm), *_ = mpcalc.bunkers_storm_motion(p, u, v, z)
    *_, total_helicity1 = mpcalc.storm_relative_helicity(
        z, u, v, depth=1 * units.km, storm_u=u_storm, storm_v=v_storm
    )
    *_, total_helicity3 = mpcalc.storm_relative_helicity(
        z, u, v, depth=3 * units.km, storm_u=u_storm, storm_v=v_storm
    )
    *_, total_helicity6 = mpcalc.storm_relative_helicity(
        z, u, v, depth=6 * units.km, storm_u=u_storm, storm_v=v_storm
    )

    # Copmute Bulk Shear components and then magnitude
    ubshr1, vbshr1 = mpcalc.bulk_shear(p, u, v, height=z, depth=1 * units.km)
    bshear1 = mpcalc.wind_speed(ubshr1, vbshr1)
    ubshr3, vbshr3 = mpcalc.bulk_shear(p, u, v, height=z, depth=3 * units.km)
    bshear3 = mpcalc.wind_speed(ubshr3, vbshr3)
    ubshr6, vbshr6 = mpcalc.bulk_shear(p, u, v, height=z, depth=6 * units.km)
    bshear6 = mpcalc.wind_speed(ubshr6, vbshr6)

    # Use all computed pieces to calculate the Significant Tornado parameter
    sig_tor = mpcalc.significant_tornado(
        sbcape, lcl_height, total_helicity3, bshear3
    ).to_base_units()

    # Perform the calculation of supercell composite if an effective layer exists
    super_comp = mpcalc.supercell_composite(mucape, total_helicity3, bshear3)

    # There is a lot we can do with this data operationally, so let's plot some of
    # these values right on the plot, in the box we made
    # First lets plot some thermodynamic parameters
    plt.figtext(
        0.58, 0.37, "SBCAPE: ", weight="bold", fontsize=15, color="black", ha="left"
    )
    plt.figtext(
        0.71,
        0.37,
        f"{sbcape:.0f~P}",
        weight="bold",
        fontsize=15,
        color="orangered",
        ha="right",
    )
    plt.figtext(
        0.58, 0.34, "SBCIN: ", weight="bold", fontsize=15, color="black", ha="left"
    )
    plt.figtext(
        0.71,
        0.34,
        f"{sbcin:.0f~P}",
        weight="bold",
        fontsize=15,
        color="lightblue",
        ha="right",
    )
    plt.figtext(
        0.58, 0.29, "MLCAPE: ", weight="bold", fontsize=15, color="black", ha="left"
    )
    plt.figtext(
        0.71,
        0.29,
        f"{mlcape:.0f~P}",
        weight="bold",
        fontsize=15,
        color="orangered",
        ha="right",
    )
    plt.figtext(
        0.58, 0.26, "MLCIN: ", weight="bold", fontsize=15, color="black", ha="left"
    )
    plt.figtext(
        0.71,
        0.26,
        f"{mlcin:.0f~P}",
        weight="bold",
        fontsize=15,
        color="lightblue",
        ha="right",
    )
    plt.figtext(
        0.58, 0.21, "MUCAPE: ", weight="bold", fontsize=15, color="black", ha="left"
    )
    plt.figtext(
        0.71,
        0.21,
        f"{mucape:.0f~P}",
        weight="bold",
        fontsize=15,
        color="orangered",
        ha="right",
    )
    plt.figtext(
        0.58, 0.18, "MUCIN: ", weight="bold", fontsize=15, color="black", ha="left"
    )
    plt.figtext(
        0.71,
        0.18,
        f"{mucin:.0f~P}",
        weight="bold",
        fontsize=15,
        color="lightblue",
        ha="right",
    )
    plt.figtext(
        0.58, 0.13, "TT-INDEX: ", weight="bold", fontsize=15, color="black", ha="left"
    )
    plt.figtext(
        0.71,
        0.13,
        f"{total_totals:.0f~P}",
        weight="bold",
        fontsize=15,
        color="orangered",
        ha="right",
    )
    plt.figtext(
        0.58, 0.10, "K-INDEX: ", weight="bold", fontsize=15, color="black", ha="left"
    )
    plt.figtext(
        0.71,
        0.10,
        f"{kindex:.0f~P}",
        weight="bold",
        fontsize=15,
        color="orangered",
        ha="right",
    )

    # now some kinematic parameters
    plt.figtext(
        0.73, 0.37, "0-1km SRH: ", weight="bold", fontsize=15, color="black", ha="left"
    )
    plt.figtext(
        0.88,
        0.37,
        f"{total_helicity1:.0f~P}",
        weight="bold",
        fontsize=15,
        color="navy",
        ha="right",
    )
    plt.figtext(
        0.73,
        0.34,
        "0-1km SHEAR: ",
        weight="bold",
        fontsize=15,
        color="black",
        ha="left",
    )
    plt.figtext(
        0.88,
        0.34,
        f"{bshear1:.0f~P}",
        weight="bold",
        fontsize=15,
        color="blue",
        ha="right",
    )
    plt.figtext(
        0.73, 0.29, "0-3km SRH: ", weight="bold", fontsize=15, color="black", ha="left"
    )
    plt.figtext(
        0.88,
        0.29,
        f"{total_helicity3:.0f~P}",
        weight="bold",
        fontsize=15,
        color="navy",
        ha="right",
    )
    plt.figtext(
        0.73,
        0.26,
        "0-3km SHEAR: ",
        weight="bold",
        fontsize=15,
        color="black",
        ha="left",
    )
    plt.figtext(
        0.88,
        0.26,
        f"{bshear3:.0f~P}",
        weight="bold",
        fontsize=15,
        color="blue",
        ha="right",
    )
    plt.figtext(
        0.73, 0.21, "0-6km SRH: ", weight="bold", fontsize=15, color="black", ha="left"
    )
    plt.figtext(
        0.88,
        0.21,
        f"{total_helicity6:.0f~P}",
        weight="bold",
        fontsize=15,
        color="navy",
        ha="right",
    )
    plt.figtext(
        0.73,
        0.18,
        "0-6km SHEAR: ",
        weight="bold",
        fontsize=15,
        color="black",
        ha="left",
    )
    plt.figtext(
        0.88,
        0.18,
        f"{bshear6:.0f~P}",
        weight="bold",
        fontsize=15,
        color="blue",
        ha="right",
    )
    plt.figtext(
        0.73,
        0.13,
        "SIG TORNADO: ",
        weight="bold",
        fontsize=15,
        color="black",
        ha="left",
    )
    plt.figtext(
        0.88,
        0.13,
        f"{sig_tor[0]:.0f~P}",
        weight="bold",
        fontsize=15,
        color="orangered",
        ha="right",
    )
    plt.figtext(
        0.73,
        0.10,
        "SUPERCELL COMP: ",
        weight="bold",
        fontsize=15,
        color="black",
        ha="left",
    )
    plt.figtext(
        0.88,
        0.10,
        f"{super_comp[0]:.0f~P}",
        weight="bold",
        fontsize=15,
        color="orangered",
        ha="right",
    )

    # Add legends to the skew and hodo
    skewleg = skew.ax.legend(loc="upper left", fontsize=20)
    hodoleg = h.ax.legend(loc="upper left", fontsize=20)

    # add a quick plot title, this could be automated by
    # declaring a station and datetime variable when using
    # realtime observation data from Siphon.
    plt.figtext(
        0.45,
        0.97,
        title,
        # "59280 清远 | 2024-04-27 08:00 CST 单站探空数据",
        # "59287 广州 | 2024-04-27 15:00 CST 单站模式探空数据",
        # "龙卷发生地 | 2024-04-27 15:00 CST WRF 模拟数据",
        weight="bold",
        fontsize=30,
        ha="center",
    )
    # plt.savefig(save_path)
    # plt.savefig("images/2024-04-27 08:00:00 CST 清远单站探空数据.svg")
    # plt.savefig("images/2024-04-27 15:00:00 CST 广州单站探空数据.svg")
    # plt.savefig("images/2024-04-27 15:00:00 CST WRF 模拟数据.svg")


from os import path

current_dir = path.dirname(__file__)


def nmc_preprocess() -> (
    tuple[Quantity, Quantity, Quantity, Quantity, Quantity, Quantity]
):
    """
    MICAPS 探空资料读取与预处理
    """
    data_path = path.join(current_dir, "../UPPER_AIR")
    if not path.exists(data_path):
        raise Exception(
            "未找到 NMC 单站探空数据，请先下载并解压缩到 lib/UPPER_AIR 目录下\n"
            + "该数据并不公开提供获取，且作者受协议限制，无法提供"
        )
    from nmc_met_io.read_micaps import read_micaps_5
    import pandas as pd

    data: pd.DataFrame = read_micaps_5(path.join(data_path, "TLOGP/20240427080000.000"))
    # select ID=59280
    df = data[data["ID"] == "59280"][data["height"] < 1200]

    p = df["pressure"].values * units.hPa
    z = df["height"].values * units.m * 10
    T = df["temperature"].values * units.degC
    Td = df["dewpoint"].values * units.degC
    wind_speed = df["wind_speed"].values * units.meter_per_second
    wind_dir = df["wind_angle"].values * units.degrees
    u, v = mpcalc.wind_components(wind_speed, wind_dir)
    return T, p, Td, u, v, z


def era5_preprocess() -> (
    tuple[Quantity, Quantity, Quantity, Quantity, Quantity, Quantity]
):
    """
    ERA5 再分析资料读取与预处理
    """
    from ..data import single_station_data

    df = single_station_data.sel(
        latitude=23.1,
        longitude=113.45,
        valid_time="2024-04-27T07:00:00",
    )
    Td = mpcalc.dewpoint_from_specific_humidity(
        df["pressure_level"].values * units.hPa,
        None,
        df["q"].values,
    )
    p = df["pressure_level"].values * units.hPa
    z = df["z"].values / 9.81 * units.m
    T = (df["t"].values - 273.15) * units.degC
    u = df["u"].values * units.meter_per_second
    v = df["v"].values * units.meter_per_second
    return T, p, Td, u, v, z


def wrf_preprocess() -> (
    tuple[Quantity, Quantity, Quantity, Quantity, Quantity, Quantity]
):
    """
    WRF 模式输出数据读取与预处理
    """
    data_path = path.join(current_dir, "../wrfout/d03/wrfout_d01_2024-04-27_07_00_00")
    if not path.exists(data_path):
        raise Exception(
            "未找到 WRF 输出数据，请放置在 lib/wrfout 目录下，类似 "
            + "lib/wrfout/d03/wrfout_d01_2024-04-27_07_00_00"
        )
    from netCDF4 import Dataset
    from wrf import getvar

    tlat, tlon = 23.336291695619014, 113.4180102524545
    wlon = 113.482
    wlat = 23.21

    ds = Dataset(data_path)
    dataz = getvar(ds, "z")
    distance = np.sqrt((dataz.XLONG - tlon) ** 2 + (dataz.XLAT - tlat) ** 2)
    j, i = np.unravel_index(np.argmin(distance.values), distance.shape)

    # # 获取对应的数据值
    z = dataz[:, j, i].values * units.m
    T = getvar(ds, "temp", units="degC")[:, j, i].values * units.degC
    Td = getvar(ds, "td", units="degC")[:, j, i].values * units.degC
    p = getvar(ds, "p", units="hPa")[:, j, i].values * units.hPa
    wspd, wdir = getvar(ds, "wspd_wdir", units="m/s")[:, :, j, i]
    u, v = mpcalc.wind_components(wspd * units.mps, wdir * units.degrees)
    return T, p, Td, u, v, z


def draw_p4_8():
    """
    图4.8，2024 年 4 月 27 日 08 时清远站（编号 59280，23.72°N，113.08°E）实测探空数据 T-lnP 图与风矢图
    """
    T, p, Td, u, v, z = nmc_preprocess()
    draw(
        T=T,
        p=p,
        Td=Td,
        u=u,
        v=v,
        z=z,
        title="59280 清远 | 2024-04-27 08:00 CST 单站探空数据",
        save_path="images/2024-04-27 08:00:00 CST 清远单站探空数据.svg",
    )


def draw_p4_9():
    """
    图4.9，2024 年 4 月 27 日 15 时再分析资料广州站邻近格点数据 T-lnP 图与风矢图
    """
    T, p, Td, u, v, z = era5_preprocess()
    draw(
        T=T,
        p=p,
        Td=Td,
        u=u,
        v=v,
        z=z,
        title="59287 广州 | 2024-04-27 15:00 CST 单站模式探空数据",
        save_path="images/2024-04-27 08:00:00 CST 清远单站探空数据.svg",
    )


def draw_p4_10():
    """
    图4.10，2024 年 4 月 27 日 15 时龙卷发生地 WRF 模式邻近格点数据 T-lnP 图与风矢图
    """
    T, p, Td, u, v, z = wrf_preprocess()
    draw(
        T=T,
        p=p,
        Td=Td,
        u=u,
        v=v,
        z=z,
        title="龙卷发生地 | 2024-04-27 15:00 CST WRF 模拟数据",
        save_path="images/2024-04-27 15:00:00 CST WRF 模拟数据.svg",
    )
