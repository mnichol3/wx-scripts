"""
3 June 2019
Author: Matt Nicholson

Adapted from Jason Hemedinger's example
"""
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pyart
from os.path import join
import sys

DATA_PATH = '/media/mnichol3/pmeyers1/MattNicholson/nexrad'

# Read in the gridded file, create GridMapDisplay object
fname = 'KAMA20190523_210747_V06.nc'
fpath = join(DATA_PATH, fname)

radar = pyart.io.read(fpath)
display = pyart.graph.GridMapDisplay(radar)

# Setting projection, figure size, and panel sizes.
projection = ccrs.PlateCarree()

fig = plt.figure(figsize=[15,7])

map_panel_axes = [0.05, 0.05, .4, .80]
x_cut_panel_axes = [0.55, 0.10, .4, .25]
y_cut_panel_axes = [0.55, 0.50, .4, .25]

# Set parameters.
level = 1
vmin = -8
vmax = 64
lat = 35.615
lon = -101.378

# Panel 1: PPI plot of the second tilt.
ax1 = fig.add_axes(map_panel_axes, projection=projection)
display.plot_grid('reflectivity', 1, vmin=vmin, vmax=vmax,
                  projection=projection,
                  cmap='pyart_HomeyerRainbow')
display.plot_crosshairs(lon=lon, lat=lat)

# Panel 2: longitude slice
ax2 = fig.add_axes(x_cut_panel_axes)
display.plot_longitude_slice('reflectivity', lon=lon, lat=lat,
                             vmin=vmin, vmax=vmax,
                             cmap='pyart_HomeyerRainbow')

ax2.set_ylim([0, 15])
ax2.set_xlim([-50, 50])

#Panel 3: latitud slice
ax3 = fig.add_axes(y_cut_panel_axes)
display.plot_latitude_slice('reflectivity', lon=lon, lat=lat,
                           vmin=vmin, vmax=vmax,
                        cmap='pyart_HomeyerRainbow')
ax3.set_ylim([0, 15])
ax3.set_xlim([-50, 50])

plt.show()
