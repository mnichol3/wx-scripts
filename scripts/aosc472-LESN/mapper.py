"""
01 Mar 2019
Author: Matt Nicholson
"""

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature, ShapelyFeature
from cartopy.io.shapereader import Reader
import numpy as np
import matplotlib.cm as cm
import xarray as xr
from scipy.interpolate import interp2d
from matplotlib import colors
import warnings
import asos_parse as ap

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

DATA_PATH = '/home/mnichol3/Coding/wx-scripts/aosc472-LESN/data/'

def make_map(fname, coords):
    """
    Plots a geographic map of the area defined by the list of coordinates taken
    as a parameter

    Parameters
    ----------
    coords : list of floats
        List of coordinates to define the map area
        Format: [min_lon, min_lat, max_lon, max_lat]
    """
    us_states_fname = '/home/mnichol3/Coding/wx-scripts/aosc472-LESN/data/s_11au16/s_11au16.shp'
    us_counties_fname = '/home/mnichol3/Coding/wx-scripts/aosc472-LESN/data/c_02ap19/c_02ap19.shp'
    can_provs_fname = '/home/mnichol3/Coding/wx-scripts/aosc472-LESN/data/province/province.shp'
    station_lons = []
    station_lats = []
    color_list = ['#b3e6ff','#66ccff','#1ab2ff','#0099e6','#0077b3','#c2f0c2',
                  '#98e698','#6fdc6f','#32cd32','#2db92d','#ffd699','#ffc266',
                  '#ffad33','#ff9900','#cc7a00','#ff8080','#ff4d4d','#ff1a1a',
                  '#e60000','#b30000','#ffb3ff','#ff80ff','#ff4dff','#ff00ff',
                  '#cc00cc']

    min_lon = coords[0]
    min_lat = coords[1]
    max_lon = coords[2]
    max_lat = coords[3]

    splits = fname.split('_')
    local_fname = splits[2] + '_' + splits[3][:-3]

    data_fname = DATA_PATH + fname

    ds = xr.open_dataset(data_fname)

    lats = ds.lat.data
    lons = ds.lon.data


    start_date = ds['Data'].start_date
    stop_date = ds['Data'].stop_date

    data = ds['Data'].data
    data = data * 39.370  # Sketchy way to convert m to in
    data[data == 0.0] = np.nan

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())

    #ax = plt.axes([0, 0, 1, 1], projection=ccrs.Mercator(), anchor='C')
    ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

    us_states = ShapelyFeature(Reader(us_states_fname).geometries(),
                                crs=ccrs.PlateCarree())
    us_counties = ShapelyFeature(Reader(us_counties_fname).geometries(),
                                crs=ccrs.PlateCarree())
    can_provs = ShapelyFeature(Reader(can_provs_fname).geometries(),
                                crs=ccrs.PlateCarree())

    ax.background_patch.set_facecolor('#4d9eb3') # #829b99

    # make a color map of fixed colors

    color_list = [colors.to_rgba(rgb) for rgb in color_list]

    cmap = colors.ListedColormap(color_list)
    clevs = np.arange(1, 25, 1)
    norm = colors.BoundaryNorm(clevs, cmap.N)

    ax.add_feature(us_states, facecolor='#808080', edgecolor='black', linewidth=0.75)
    ax.add_feature(can_provs, facecolor='#808080', edgecolor='black', linewidth=0.75)
    ax.add_feature(us_counties, facecolor='None', edgecolor='black', linewidth=0.25,
                    zorder=13)

    #snow_map = ax.pcolormesh(lons, lats, data, cmap=cm.Blues, transform=ccrs.PlateCarree())
    snow_contours = ax.contourf(lons, lats, data, clevs, cmap=cmap, norm=norm, transform=ccrs.PlateCarree(),
                                zorder=9)

    asos = ap.read_data(ap.ASOS_DATA_PATH)
    station_dict = ap.get_asos_stations(asos)

    stations = station_dict.keys()

    for key, val in station_dict.items():
        station_lons.append(val[0])
        station_lats.append(val[1])

    ax.scatter(station_lons, station_lats, color='black', transform=ccrs.PlateCarree(), zorder=10)

    for i, name in enumerate(stations):
        #ax.annotate(name, (station_lons[i], station_lats[i]), transform=ccrs.PlateCarree(), zorder = 9)
        ax.text(station_lons[i], station_lats[i]+ 0.05, name, horizontalalignment='left',
                color='black', transform=ccrs.PlateCarree(), zorder = 11)

    cbar = plt.colorbar(snow_contours, norm=norm, extend='both')
    cbar.ax.set_ylabel('inches', rotation=90)

    plt.title('Snow Accumulation from ' + start_date + ' to ' + stop_date)
    plt.tight_layout()
    plt.show()

    img_path = '/home/mnichol3/Coding/wx-scripts/aosc472-LESN/images/'

    fig.savefig(img_path + local_fname + '.png')



def main():
    coords = [-79.415, 42.437, -74.095, 44.885] # NY

    six_hr_fnames = ['sfav2_CONUS_6h_2018010200.nc',
                     'sfav2_CONUS_6h_2018010206.nc',
                     'sfav2_CONUS_6h_2018010212.nc',
                     'sfav2_CONUS_6h_2018010218.nc',
                     'sfav2_CONUS_6h_2018010300.nc',
                     'sfav2_CONUS_6h_2018010306.nc',
                     'sfav2_CONUS_6h_2018010312.nc',
                     'sfav2_CONUS_6h_2018010318.nc']

    tot_fnames = ['sfav2_CONUS_24h_2018010312.nc',
                  'sfav2_CONUS_48h_2018010312.nc',
                  'sfav2_CONUS_48h_2018010400.nc']


    for x in tot_fnames:
        make_map(x, coords)

    for x in six_hr_fnames:
        make_map(x, coords)


if (__name__ == "__main__"):
    main()
