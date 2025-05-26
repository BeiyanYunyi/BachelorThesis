"""
该模块提供了ERA5数据的下载功能。它包括以下函数：
- `download_single_level_data`: 下载单层数据
- `download_geopotential_data`: 下载各等压面大尺度数据
- `download_single_station_data`: 下载单站数据

在使用这些函数之前，请确保已安装`cdsapi`库，并正确[配置了CDS API密钥](https://cds.climate.copernicus.eu/how-to-api)。
"""

from .single_level_download import download_single_level_data
from .gp_download import download_geopotential_data
from .single_station_download import download_single_station_data
