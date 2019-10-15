"""
3 June 2019
Author: Matt Nicholson

Attempts to convert a NEXRAD file to netCDF. Seems to miss some important fields
"""
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pyart
from os.path import join
import sys

DATA_PATH = '/media/mnichol3/pmeyers1/MattNicholson/nexrad'

# Read in the gridded file, create GridMapDisplay object
fname = 'KAMA_SDUS54_N0RAMA_201905232102'
fpath = join(DATA_PATH, fname)

radar = pyart.io.read(fpath)

fout = fpath + '.nc'

pyart.io.write_cfradial(fout, radar, format='NETCDF4')
