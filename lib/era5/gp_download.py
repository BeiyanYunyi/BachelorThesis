import cdsapi
from os import path

dataset = "reanalysis-era5-pressure-levels"
request = {
    "product_type": ["reanalysis"],
    "variable": [
        "divergence",
        "geopotential",
        "potential_vorticity",
        "relative_humidity",
        "specific_humidity",
        "temperature",
        "u_component_of_wind",
        "v_component_of_wind",
        "vertical_velocity",
        "vorticity",
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
    "pressure_level": ["500", "700", "850", "925"],
    "data_format": "netcdf",
    "download_format": "unarchived",
    "area": [60, 60, 10, 140],
}


def download_geopotential_data():
    """
    下载各等压面大尺度数据
    """
    current_dir = path.dirname(__file__)
    download_path = path.join(current_dir, "../geopotential.nc")
    client = cdsapi.Client()
    client.retrieve(dataset, request, download_path)
