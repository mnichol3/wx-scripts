"""
Author: Matt Nicholson

This file contains functions to process hurricane wind radius data provided in the
National Hurricane Center Best Track GIS data package

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
import time

from sys import exit



################################################################################
################################ I/O Functions #################################
################################################################################



def get_radius_meta(shp_path):
    """
    Get metadata from the radii Best Track shapefile

    Parameters
    ----------
    shp_path : str
        Absolute path, including the filename, of the NHC radii best track shapefile
        to open and read

    Returns
    -------
    meta : dict
        Dictionary containing storm metadata
        Keys:
            ['first_dt', 'last_dt', 'storm_id, 'storm_basin',
             'storm_num', num_records', 'num_timesteps']
    """
    meta = {}

    shp_reader = shpreader.Reader(shp_path)

    # Get the date & time of the first record
    first_rec = next(shp_reader.records()).attributes

    first_dt = datetime.datetime.strptime(first_rec['SYNOPTIME'], "%Y%m%d%H")
    first_dt = datetime.datetime.strftime(first_dt, "%m-%d-%Y-%H:%Mz")

    storm_basin = first_rec['BASIN']
    storm_id = first_rec['STORMID']
    storm_num = first_rec['STORMNUM']

    max_rads = {
            34: {'radius': 0, 'time': ''},
            50: {'radius': 0, 'time': ''},
            64: {'radius': 0, 'time': ''}
    }

    rec_count_by_radii = {34: 0, 50: 0, 64: 0}

    for rec in shp_reader.records():
        curr_dt = rec.attributes['SYNOPTIME']


        # Update maximum Saffir-Simpson rating if necessary
        curr_rad = rec.attributes['RADII']
        ne_rad = rec.attributes['NE']
        se_rad = rec.attributes['SE']
        sw_rad = rec.attributes['SW']
        nw_rad = rec.attributes['NW']

        for sector in [ne_rad, se_rad, sw_rad, nw_rad]:
            if (sector > max_rads[curr_rad]['radius']):
                max_rads[curr_rad]['radius'] = sector
                max_rads[curr_rad]['time'] = curr_dt

        rec_count_by_radii[curr_rad] += 1

    last_dt = datetime.datetime.strptime(curr_dt, "%Y%m%d%H")
    last_dt = datetime.datetime.strftime(last_dt, "%m-%d-%Y-%H:%Mz")

    # Format the datetime strings for the maximum radii
    for key, val in max_rads.items():
        curr_dt = max_rads[key]['time']
        curr_dt = datetime.datetime.strptime(curr_dt, "%Y%m%d%H")
        curr_dt = datetime.datetime.strftime(curr_dt, "%m-%d-%Y-%H:%Mz")
        max_rads[key]['time'] = curr_dt

    meta['first_dt'] = first_dt
    meta['last_dt'] = last_dt
    meta['storm_id'] = storm_id
    meta['storm_basin'] = storm_basin
    meta['storm_num'] = str(storm_num).zfill(2)
    meta['max_rads'] = max_rads
    meta['rec_count_by_radii'] = rec_count_by_radii

    return meta



def pp_meta(meta_dict):
    """
    Pretty print func for meta dict
    """
    # Determine the length of the longest key
    keys = list(meta_dict.keys())
    a_keys = [x for x in keys if type(meta_dict[x]) != dict]
    max_len = len(max(a_keys, key=len))

    for key, val in meta_dict.items():
        # Print the key with appended spaces to the end to make it the same
        # length as the longest key
        if (type(val) != dict):
            print('{} --> {}'.format(key.ljust(max_len), val))
        else:
            print(key)
            if (key == 'max_rads'):
                for sub_key, sub_val in val.items():
                    print('\t{}kts --> {} nm at {}'.format(str(sub_key).ljust(3),
                          sub_val['radius'], sub_val['time']))
            else:
                for sub_key, sub_val in val.items():
                    print('\t{}kts --> {}'.format(str(sub_key).ljust(3), sub_val))



def main():
    # Definitions and whatnot
    shp_path = '/media/mnichol3/tsb1/data/storms/2019-dorian/al052019_initial_best_track/AL052019_radii.shp'

    meta = get_radius_meta(shp_path)
    pp_meta(meta)



if __name__ == '__main__':
    main()
