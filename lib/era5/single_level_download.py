import cdsapi
from os import path

dataset = "reanalysis-era5-single-levels"
request = {
    "product_type": ["reanalysis"],
    "variable": [
        "vertical_integral_of_divergence_of_cloud_frozen_water_flux",
        "vertical_integral_of_divergence_of_cloud_liquid_water_flux",
        "convective_available_potential_energy",
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "2m_dewpoint_temperature",
        "2m_temperature",
        "surface_pressure",
        "total_precipitation",
        "mean_sea_level_pressure",
        "total_cloud_cover",
        "vertical_integral_of_eastward_water_vapour_flux",
        "vertical_integral_of_northward_water_vapour_flux",
        "vertical_integral_of_temperature",
    ],
    "year": ["2024"],
    "month": ["04"],
    "day": ["26", "27", "28"],
    "time": [
        "00:00",
        "01:00",
        "02:00",
        "03:00",
        "04:00",
        "05:00",
        "06:00",
        "07:00",
        "08:00",
        "09:00",
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00",
        "19:00",
        "20:00",
        "21:00",
        "22:00",
        "23:00",
    ],
    "data_format": "netcdf",
    "download_format": "zip",
    "area": [50, 70, 10, 140],
}


def download_single_level_data():
    """
    下载ERA5单层数据
    """
    client = cdsapi.Client()
    current_dir = path.dirname(__file__)
    download_path = path.join(current_dir, "../surface.zip")
    client.retrieve(dataset, request, download_path)
