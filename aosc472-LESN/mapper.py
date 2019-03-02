"""
01 Mar 2019
Author: Matt Nicholson
"""

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature
import sys


def make_map(coords):
    """
    Plots a geographic map of the area defined by the list of coordinates taken
    as a parameter

    Parameters
    ----------
    coords : list of floats
        List of coordinates to define the map area
        Format: [min_lon, min_lat, max_lon, max_lat]
    """

    min_lon = coords[0]
    min_lat = coords[1]
    max_lon = coords[2]
    max_lat = coords[3]

    ax = plt.axes([0, 0, 1, 1], projection=ccrs.Mercator())
    ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

    states = NaturalEarthFeature(
                            category='cultural',
                            scale='10m',
                            facecolor='black',
                            name='admin_1_states_provinces_shp')

    land = NaturalEarthFeature('physical', 'land', '50m', facecolor='black')

    ocean = NaturalEarthFeature('physical', 'ocean', '50m', facecolor='black')

    # (x0, x1, y0, y1)
    #ax.set_extent((min_lon, max_lon, min_lat, max_lat), crs=ccrs.PlateCarree())
    #ax.set_extent((-81.913, -73.16, 41.161, 44.79), crs=ccrs.Geodetic())
    ax.add_feature(land, linewidth=.8, edgecolor='gray', zorder = 1)
    ax.add_feature(states, linewidth=.8, edgecolor='gray', zorder = 2)
    ax.add_feature(ocean, linewidth=.8, edgecolor='gray', zorder = 0)
    #plt.scatter(-77.93, 43.128, marker="+", color="r", transform=ccrs.PlateCarree())

    plt.title('Le map')

    plt.show()



def main():
    coords = [-81.913, 41.161, -73.16, 44.79]
    make_map(coords)

if (__name__ == "__main__"):
    main()
