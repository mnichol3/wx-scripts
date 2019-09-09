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

    meta['first_dt'] = first_dt
    meta['last_dt'] = last_dt
    meta['storm_name'] = storm_name
    meta['storm_basin'] = storm_basin
    meta['storm_num'] = str(storm_num).zfill(2)
    meta['max_ss'] = max_ss
    meta['max_wind'] = max_wind
    meta['num_records'] = num_records

    return meta



def plot_track(shp_path, outpath, extent=None, save=False, show=True):
    state_path = '/media/mnichol3/tsb1/data/gis/nws_s_11au16/s_11au16.shp'
    z_ord = {'track': 2, 'map': 1, 'base': 0}
    plt_extent = [extent[2], extent[3], extent[0], extent[1]]

    shp_reader = shpreader.Reader(shp_path)
    track_recs = list(shp_reader.records())
    track_pts_geo = list(shp_reader.geometries())
    track_pts = cfeature.ShapelyFeature(track_pts_geo, crs_plt)

    states = shpreader.Reader(state_path)
    states = list(states.geometries())
    states = cfeature.ShapelyFeature(states, crs_plt)

    crs_plt = ccrs.PlateCarree()

    fig = plt.figure(figsize=(12, 8))

    ax = fig.add_subplot(111, projection=ccrs.Mercator())

    # Set axis background color to black
    ax.imshow(
        np.tile(
            np.array(
                [[[0, 0, 0]]], dtype=np.uint8),
            [2, 2, 1]),
        origin='upper', transform=crs_plt, extent=[-180, 180, -180, 180]
    )

    ax.add_feature(states, linewidth=.8, facecolor='black',
                   edgecolor='gray', zorder=z_ord['map'])

    # ax.add_feature(track_pts, linewidth=.8, facecolor='none', edgecolor='yellow', zorder=z_ord['wwa'])

    plt.title('NHC Best Track - {} {}'.format(year, storm_name),
              loc='right',
              fontsize=12)

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
meta = get_besttrack_meta(shp_path)
pp_meta(meta)
