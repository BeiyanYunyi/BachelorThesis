import cdsapi
from os import path

dataset = "reanalysis-era5-pressure-levels"
request = {
    "product_type": ["reanalysis"],
    "variable": [
        "geopotential",
        "relative_humidity",
        "specific_humidity",
        "temperature",
        "u_component_of_wind",
        "v_component_of_wind",
    ],
    "year": ["2024"],
    "month": ["04"],
    "day": ["26", "27", "28"],
    "time": ["00:00", "04:00", "05:00", "06:00", "07:00", "08:00", "12:00"],
    "pressure_level": [
        "1",
        "2",
        "3",
        "5",
        "7",
        "10",
        "20",
        "30",
        "50",
        "70",
        "100",
        "125",
        "150",
        "175",
        "200",
        "225",
        "250",
        "300",
        "350",
        "400",
        "450",
        "500",
        "550",
        "600",
        "650",
        "700",
        "750",
        "775",
        "800",
        "825",
        "850",
        "875",
        "900",
        "925",
        "950",
        "975",
        "1000",
    ],
    "data_format": "netcdf",
    "download_format": "unarchived",
    "area": [23.4, 113.2, 23.1, 113.5],
}


def download_single_station_data():
    """
    下载单站（小范围）各等压面数据
    """
    current_dir = path.dirname(__file__)
    download_path = path.join(current_dir, "../single_station.nc")
    client = cdsapi.Client()
    client.retrieve(dataset, request, download_path)
