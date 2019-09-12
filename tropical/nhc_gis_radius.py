"""
Author: Matt Nicholson

This file contains functions to process hurricane wind radius data provided in the
National Hurricane Center Best Track GIS data package

Notes
-----
Record:
    Record(MULTIPOLYGON((())), {attributes})

    Attribute keys:
        ['RADII', 'STORMID', 'BASIN', 'STORMNUM', 'ADVNUM', 'SYNOPTIME',
         'TIMEZONE', 'NE', 'SE', 'SW', 'NW']

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


class NHCRadius(object):
    """
    Object to represent an NHC best track radius shapefile record
    """
    def __init__(self, date, time, storm_id, radius, ne, se, sw, nw, poly):
        super(NHCRadius, self).__init__()
        self.date = date
        self.time = time
        self.storm_id = storm_id
        self.radius = radius
        self.ne = ne
        self.se = se
        self.sw = sw
        self.nw = nw
        self.poly = poly



    def __repr__(self):
        return '<NHCRadius object - {} {}-{}z-{}>'.format(self.storm_id, self.date,
                self.time, self.radius)



def ingest_gen(shp_path):
    """
    Creates a generator for NHCRadius objects created from a shapefile

    Parameters
    ----------
    shp_path : str
        Absolute path, including the filename, of the shapefile to open & read

    Return
    ------
    Yields a NHCRadius object
    """
    shp_reader = shpreader.Reader(shp_path)

    for rec in shp_reader.records():
        curr_dt = datetime.datetime.strptime(rec.attributes['SYNOPTIME'], "%Y%m%d%H")
        curr_date = datetime.datetime.strftime(curr_dt, "%m-%d-%Y")
        curr_time = datetime.datetime.strftime(curr_dt, "%H:%M")
        cur_id = rec.attributes['STORMID']
        curr_rad = rec.attributes['RADII']
        curr_ne = rec.attributes['NE']
        curr_se = rec.attributes['SE']
        curr_sw = rec.attributes['SW']
        curr_nw = rec.attributes['NW']

        curr_obj = NHCRadius(curr_date, curr_time, cur_id, curr_rad, curr_ne,
                             curr_se, curr_sw, curr_nw, rec.geometry)

        yield curr_obj



def ingest_list(shp_path):
    """
    Creates & returns a list of NHCRadius objects created from a shapefile

    Parameters
    ----------
    shp_path : str
        Absolute path, including the filename, of the shapefile to open & read

    Return
    ------
    radii : list of NHCRadius objects
    """
    radii = []

    shp_reader = shpreader.Reader(shp_path)

    for rec in shp_reader.records():
        curr_dt = datetime.datetime.strptime(rec.attributes['SYNOPTIME'], "%Y%m%d%H")
        curr_date = datetime.datetime.strftime(curr_dt, "%m-%d-%Y")
        curr_time = datetime.datetime.strftime(curr_dt, "%H:%M")
        cur_id = rec.attributes['STORMID']
        curr_rad = rec.attributes['RADII']
        curr_ne = rec.attributes['NE']
        curr_se = rec.attributes['SE']
        curr_sw = rec.attributes['SW']
        curr_nw = rec.attributes['NW']

        curr_obj = NHCRadius(curr_date, curr_time, cur_id, curr_rad, curr_ne,
                             curr_se, curr_sw, curr_nw, rec.geometry)

        radii.append(curr_obj)

    return radii



def get_rec_df(shp_path, write=False, outpath=None):
    """
    Get a pandas dataframe containing shapefile record information

    Parameters
    ----------
    shp_path : str
        Absolute path, including the filename, of the shapefile to open & read
    """
    col_names = ['date-time', 'storm_id', 'radii', 'ne', 'se', 'sw', 'nw']
    data = []

    shp_reader = shpreader.Reader(shp_path)

    for rec in shp_reader.records():
        curr_dt = datetime.datetime.strptime(rec.attributes['SYNOPTIME'], "%Y%m%d%H")
        curr_dt = datetime.datetime.strftime(curr_dt, "%m-%d-%Y-%H%M")
        cur_id = rec.attributes['STORMID']
        curr_rad = rec.attributes['RADII']
        curr_ne = rec.attributes['NE']
        curr_se = rec.attributes['SE']
        curr_sw = rec.attributes['SW']
        curr_nw = rec.attributes['NW']

        curr_dict = {'date-time': curr_dt,
                    'storm_id': cur_id,
                    'radii': curr_rad,
                    'ne': curr_ne,
                    'se': curr_se,
                    'sw': curr_sw,
                    'nw': curr_nw
                    }

        data.append(curr_dict)

    df = pd.DataFrame(data, columns=col_names)
    df = df.set_index('date-time')

    if (write):
        if (outpath):
            df.to_csv(outpath, sep=',', header=col_names)
        else:
            raise ValueError("'outpath' parameter cannot be None")
    return df



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
             'storm_num', 'max_rads', 'rec_count_by_radii', 'num_records']
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
    timesteps = []

    for rec in shp_reader.records():
        curr_dt = rec.attributes['SYNOPTIME']
        timesteps.append(curr_dt)

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

    num_records = 0
    for key, val in rec_count_by_radii.items():
        num_records += val

    num_timesteps = len(list(set(timesteps)))

    meta['first_dt'] = first_dt
    meta['last_dt'] = last_dt
    meta['storm_id'] = storm_id
    meta['storm_basin'] = storm_basin
    meta['storm_num'] = str(storm_num).zfill(2)
    meta['max_rads'] = max_rads
    meta['rec_count_by_radii'] = rec_count_by_radii
    meta['num_records'] = num_records
    meta['num_timesteps'] = num_timesteps

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

    ################# Test/Debug #################
    # for rec in ingest_gen(shp_path):
    #     print(rec)
    #
    #
    # radii = ingest_list(shp_path)
    # for rec in radii:
    #     print(rec)

    # df = get_rec_df(shp_path)
    # print(df)



if __name__ == '__main__':
    main()
