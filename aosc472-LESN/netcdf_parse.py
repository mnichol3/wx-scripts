"""
02 Mar 2019
Author: Matt Nicholson
"""
from netCDF4 import Dataset
import pandas as pd
import xarray as xr
import numpy as np

def parse_data(fname, coords):
    """
    NWS NOHRSC dataset

    Variables:
        lat
        lat_bounds
        lon
        lon_bounds
        crs
        Data
    """

    min_lon = coords[0]
    min_lat = coords[1]
    max_lon = coords[2]
    max_lat = coords[3]


    fh = Dataset(fname, mode='r')

    start_date = fh.variables['Data'].start_date
    end_date = fh.variables['Data'].stop_date

    lats = fh.variables['lat']
    lons = fh.variables['lon']
    data = fh.variables['Data']

    return (lons, lats, data)
    #--------------------------------------




"""
def main():
    fname = '/home/mnichol3/Coding/wx-scripts/aosc472-LESN/data/sfav2_CONUS_6h_2018010306.nc'
    coords = [-81.913, 41.161, -73.16, 44.79]
    parse_data(fname, coords)

if (__name__ == "__main__"):
    main()
"""
