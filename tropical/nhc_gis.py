"""
Author: Matt Nicholson

This file contains functions to process GIS data provided by the National
Hurricane Center

Notes
-----
* Record data structure: Record(geometry, attritubes)

    Ex:
    Record(POINT (-54.8 51.6), {'STORMNAME': 'DORIAN', 'DTG': 2019090900, 'YEAR': 2019,
                                'MONTH': '09', 'DAY': 9, 'HHMM': '0000', 'MSLP': 980,
                                'BASIN': 'al', 'STORMNUM': 5, 'STORMTYPE': 'EX',
                                'INTENSITY': 50, 'SS': 0, 'LAT': 51, 'LON': -54}, <fields>)

    record.geometry: POINT (-54.8 51.6)
    record.attritubes: {'STORMNAME': 'DORIAN', 'DTG': 2019090900, 'YEAR': 2019,
                                'MONTH': '09', 'DAY': 9, 'HHMM': '0000', 'MSLP': 980,
                                'BASIN': 'al', 'STORMNUM': 5, 'STORMTYPE': 'EX',
                                'INTENSITY': 50, 'SS': 0, 'LAT': 51, 'LON': -54}

    record.attributes.keys : ['STORMNAME', 'DTG', 'YEAR', 'MONTH', 'DAY', 'HHMM',
                              'MSLP', 'BASIN', 'STORMNUM', 'STORMTYPE', 'INTENSITY',
                              'SS', 'LAT', 'LON']

"""
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from os.path import join
import numpy as np
import datetime
import pandas as pd
from os.path import isfile

from sys import exit



def get_besttrack_meta(shp_path):
    """
    Get metadata from the Best Track shapefile

    Parameters
    ----------
    shp_path : str
        Absolute path, including the filename, of the NHC best track shapefile
        to open and read

    Returns
    -------
    meta : dict
        Dictionary containing storm metadata
        Keys:
            ['first_dt', 'last_dt', 'storm_name', 'storm_basin',
             'storm_num', 'max_ss', 'max_intensity', 'num_records']
    """
    meta = {}

    shp_reader = shpreader.Reader(shp_path)
    first_rec = next(shp_reader.records())

    # Get the date & time of the first record
    first_dt = '{}{}{}-{}'.format(first_rec.attributes['MONTH'], first_rec.attributes['DAY'],
                                  first_rec.attributes['YEAR'], first_rec.attributes['HHMM'])

    first_dt = datetime.datetime.strptime(first_dt, "%m%d%Y-%H%M")
    first_dt = datetime.datetime.strftime(first_dt, "%m%d%Y-%H:%M")

    max_ss = 0
    max_wind = 0
    num_records = 0

    for rec in shp_reader.records():
        num_records += 1
        storm_name = rec.attributes['STORMNAME']
        storm_basin = rec.attributes['BASIN']
        storm_num = rec.attributes['STORMNUM']

        # Update maximum Saffir-Simpson rating if necessary
        curr_ss = rec.attributes['SS']
        if (curr_ss > max_ss):
            max_ss = curr_ss

        # Update maximum storm intensity if necessary
        curr_wind = rec.attributes['INTENSITY']
        if (curr_wind > max_wind):
            max_wind = curr_wind

        last_dt = '{}{}{}-{}'.format(rec.attributes['MONTH'], rec.attributes['DAY'],
                                     rec.attributes['YEAR'], rec.attributes['HHMM'])

    last_dt = datetime.datetime.strptime(last_dt, "%m%d%Y-%H%M")
    last_dt = datetime.datetime.strftime(last_dt, "%m%d%Y-%H:%M")

    meta['year'] = rec.attributes['YEAR']
    meta['first_dt'] = first_dt
    meta['last_dt'] = last_dt
    meta['storm_name'] = storm_name
    meta['storm_basin'] = storm_basin
    meta['storm_num'] = str(storm_num).zfill(2)
    meta['max_ss'] = max_ss
    meta['max_wind'] = max_wind
    meta['num_records'] = num_records

    return meta



def plot_track(shp_path, storm_name, year, extent=None, show=True, save=False, outpath=None):
    """

    extent: [ymin, ymax, xmin, xmax] aka [min_lat, max_lat, min_lon, max_lon]
    """

    z_ord = {'base': 0,
             'land': 1,
             'states': 2,
             'track': 3,
             'top': 10
             }

    crs_plt = ccrs.PlateCarree()

    if (extent):
        plt_extent = [extent[2], extent[3], extent[0], extent[1]]
    else:
        # x0, x1, y0, y1
        plt_extent = [-180, 0, 0, 90]

    shp_reader = shpreader.Reader(shp_path)
    track_pts = list(shp_reader.geometries())
    lons = [pt.x for pt in track_pts]
    lats = [pt.y for pt in track_pts]

    land_50m = cfeature.NaturalEarthFeature('physical', 'land', '50m', facecolor='none')
    states_50m = cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces',
                                              scale='50m', facecolor='none')
    countries_50m = cfeature.NaturalEarthFeature(category='cultural', name='admin_0_countries',
                                                 scale='50m', facecolor='none')

    fig = plt.figure(figsize=(12, 8))

    ax = fig.add_subplot(111, projection=ccrs.Mercator())

    # Set axis background color to black
    ax.imshow(
        np.tile(
            np.array(
                [[[0, 0, 0]]], dtype=np.uint8),
            [2, 2, 1]),
        origin='upper', transform=crs_plt, extent=[-180, 180, -180, 180],
        zorder=z_ord['base']
    )

    ax.add_feature(land_50m, linewidth=.8, edgecolor='gray', zorder=z_ord['land'])
    ax.add_feature(countries_50m, linewidth=.8, edgecolor='gray', zorder=z_ord['land'])
    ax.add_feature(states_50m, linewidth=.8, edgecolor='gray', zorder=z_ord['states'])

    ax.plot(lons, lats, color='red', marker='o',
            transform=crs_plt, zorder=z_ord['track'])

    ax.set_extent(plt_extent, crs=crs_plt) # [x0, x1, y0, y1]

    plt.title('NHC Best Track {}-{}'.format(year, storm_name), loc='right', fontsize=12)

    plt.gca().set_aspect('equal', adjustable='box')

    # Try to cut down on whitespace surrounding the actual plot
    plt.subplots_adjust(left=0, bottom=0.05, right=1, top=0.95, wspace=0, hspace=0)

    if (save):
        if (outpath is not None):
            fname = 'BestTrackPlot.png'
            path = join(outpath, fname)
            plt.savefig(path, dpi=600)
        else:
            raise ValueError('Error: Outpath cannot be None')
    if (show):
        plt.show()
    plt.close('all')




def to_file(shp_path, outpath):
    """
    Read the shapefile into Pandas DataFrame and write it to csv file

    Parameters
    ----------
    shp_path : str
        Absolute path, including the filename, of the best track shapefile to open
        & read
    outpath : str
        Absolute path, including the filename, of the csv/txt file to write
        the best track data to

    Returns
    -------
    outpath : str
        Absolute path, including the filename, of the csv/txt file to write
        the best track data to
    """
    col_names = ['date-time', 'name', 'storm_num', 'basin', 'lat',
                 'lon', 'mslp', 'storm_type', 'wind', 'ss']
    data = []

    shp_reader = shpreader.Reader(shp_path)

    track_pts = list(shp_reader.geometries())
    lons = [pt.x for pt in track_pts]
    lats = [pt.y for pt in track_pts]

    for rec in shp_reader.records():
        dt = '{}{}{}-{}'.format(rec.attributes['MONTH'], rec.attributes['DAY'],
                                rec.attributes['YEAR'], rec.attributes['HHMM'])
        lon = rec.geometry.x
        lat = rec.geometry.y
        name = rec.attributes['STORMNAME']
        storm_num = rec.attributes['STORMNUM']
        basin = rec.attributes['BASIN']
        mslp = rec.attributes['MSLP']
        storm_type = rec.attributes['STORMTYPE']
        wind = rec.attributes['INTENSITY']
        ss = rec.attributes['SS']

        curr_dict = {'date-time': dt,
                    'name': name,
                    'storm_num': storm_num,
                    'basin': basin,
                    'lon': lon,
                    'lat': lat,
                    'storm_type': storm_type,
                    'mslp': mslp,
                    'wind': wind,
                    'ss': ss
                    }

        data.append(curr_dict)

    df = pd.DataFrame(data, columns=col_names)

    df.to_csv(outpath, sep=',', header=col_names, index=False)



def csv_to_df(abs_path):
    """
    Read a best track csv into a Pandas DataFrame

    Parameters
    ----------
    abs_path : str
        Absolute path, including the filename, of the csv/txt file to read

    Returns
    -------
    df : Pandas DataFrame
        DataFrame containing the best track data
        Column names: ['date-time', 'name', 'storm_num', 'basin', 'lat',
                       'lon', 'mslp', 'storm_type', 'wind', 'ss']
    """
    if (isfile(abs_path)):
        df = pd.read_csv(abs_path, sep=',', header=0)
        return df
    else:
        raise FileNotFoundError('File not found: {}'.format(abs_path))



def pp_meta(meta_dict):
    """
    Pretty print func for meta dict
    """
    # Determine the length of the longest key
    keys = list(meta_dict.keys())
    max_len = len(max(keys, key=len))

    for key, val in meta_dict.items():
        # Print the key with appended spaces to the end to make it the same
        # length as the longest key
        print('{} --> {}'.format(key.ljust(max_len), val))




shp_path = '/media/mnichol3/tsb1/data/storms/2019-dorian/al052019_initial_best_track/AL052019_pts.shp'

# meta = get_besttrack_meta(shp_path)
# pp_meta(meta)

# txt_out = '/media/mnichol3/tsb1/data/storms/2019-dorian/initial_best_track.txt'
# to_file(shp_path, txt_out)
# # print(csv_to_df(txt_out))

# extent = [5.935, 40.031, -88.626, -40.285]
# plot_track(shp_path, meta['storm_name'], meta['year'], extent=extent)
