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



def track_shp_to_df(shp_path, outpath=None, write=False):
    """
    Read the shapefile into Pandas DataFrame and write it to csv file if desired

    Parameters
    ----------
    shp_path : str
        Absolute path, including the filename, of the best track shapefile to open
        & read
    outpath : str, optional
        Absolute path, including the filename, of the csv/txt file to write
        the best track data to. Required if writing to file
    write: bool, optional
        If True, the dataframe will be written to a file specified by the
        'outpath' parameter. Default: False

    Returns
    -------
    df : Pandas Dataframe

    """
    col_names = ['date-time', 'name', 'storm_num', 'basin', 'lat',
                 'lon', 'mslp', 'storm_type', 'wind', 'ss']
    data = []

    shp_reader = shpreader.Reader(shp_path)

    track_pts = list(shp_reader.geometries())
    lons = [pt.x for pt in track_pts]
    lats = [pt.y for pt in track_pts]

    for rec in shp_reader.records():
        dt = '{}-{}-{}-{}'.format(
                                str(rec.attributes['MONTH']).zfill(2),
                                str(rec.attributes['DAY']).zfill(2),
                                rec.attributes['YEAR'],
                                rec.attributes['HHMM']
                                )
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
    df = df.set_index('date-time')

    if (write):
        if (outpath):
            df.to_csv(outpath, sep=',', header=col_names)
    return df



def track_csv_to_df(abs_path):
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

        or

        col_names = ['date-time', 'storm_num', 'lat', 'lon', 'mslp', 'wind', 'ss']
        if reading an interpolated data file
    """
    if (isfile(abs_path)):
        df = pd.read_csv(abs_path, sep=',', header=0, index_col='date-time')
        return df
    else:
        raise FileNotFoundError('File not found: {}'.format(abs_path))



def track_df_to_csv(df, outpath):
    """
    Write a DataFrame to csv file

    Parameters
    ----------
    df : Pandas DataFrame
        DataFrame to write to file
    outpath : str
        Absolute path, including filename, to write the csv to
    """
    if (df.shape[1] == 6):
        col_names = ['storm_num', 'lat', 'lon', 'mslp', 'wind', 'ss']
    else:
        col_names = ['name', 'storm_num', 'basin', 'lat',
                     'lon', 'mslp', 'storm_type', 'wind', 'ss']

    df.to_csv(outpath, sep=',', header=col_names, index=True, index_label='date-time')



def pp_df(df):
    from time import sleep

    for index, row in df.iterrows():
        # ['storm_num', 'lat', 'lon', 'mslp', 'wind', 'ss']
        print('{0}   {1:.3f}   {2:.3f}   {3:.3f}   {4:.3f}'.format(index,
                row['lat'], row['lon'], row['mslp'], row['wind']))
        sleep(0.1)


################################################################################
############################# Plotting Functions ###############################
################################################################################


def interp_track_df(df, freq):
    """
    Interpolate the dataframe to 1-minute

    Parameters
    ----------
    df : Pandas Dataframe
        Dataframe to interpolate
    freq : str
        Frequency used to calculate the time series used to create new data points.
        Based on pandas timeseries offset aliases.

        Valid frequency aliases:
            'H'        --> Hourly
            'T', 'min' --> minutely
            'S',       --> secondly
            'L', 'ms'  --> Milliseconds
            'D',       --> calendar day
            'W'        --> weekly

        Ex: '1T' or 'T' --> 1 minute
            '10T'       --> 10 minutes
            '1H' or 'H' --> 1 hour
            '2D'        --> 2 calendar days

    Returns
    -------
    df : Pandas Dataframe
        Dataframe containing interpolated data.
        Column names: ['storm_num', 'lat', 'lon', 'mslp', 'wind', 'ss']
    """
    valid_freqs = ['H', 'T', 'min', 'S', 'L', 'ms', 'D', 'W']

    # Validate the frequency string
    if (len(freq) > 1):
        # If there is a number attached to the frequency alias
        key = freq[1]
        val = freq[0]

        try:
            val = int(val)
        except ValueError:
            raise ValueError('Invalid frequency argument')

    # Validate the frequency alias. Works regardless of if a leading number
    # is attached or not
    if (not freq[-1] in valid_freqs):
        raise ValueError('Invalid frequency argument')


    start_dt = df.index[0]
    start_dt = datetime.datetime.strptime(start_dt, '%m-%d-%Y-%H%M')

    end_dt = df.index[-1]
    end_dt = datetime.datetime.strptime(end_dt, '%m-%d-%Y-%H%M')

    # Convert the index type from str to pandas timestamp
    df.index = pd.to_datetime(df.index, format='%m-%d-%Y-%H%M')

    # Calculate the times between start & end that we want to interpolate
    # data for
    interp_times = pd.date_range(start=start_dt, end=end_dt, freq=freq)

    # Resample the dataframe for 1-min
    # Resampling removes 'name', 'basin', & 'storm_type' columns
    # Resulting columns are: date-time (index), ['storm_num', 'lat', 'lon',
    #                                            'mslp', 'wind', 'ss']
    df = df.resample(freq).sum()

    # Set 0 values after the first row to NaN to prepare for interpolation
    df[df.iloc[1:] == 0] = np.NaN

    df = df.interpolate(method='time', limit_direction='forward')

    return df



def main():
    # Definitions and whatnot
    shp_path = '/media/mnichol3/tsb1/data/storms/2019-dorian/al052019_initial_best_track/AL052019_radii.shp'
    # txt_out_raw = '/media/mnichol3/tsb1/data/storms/2019-dorian/initial_best_track.txt'
    # txt_out_10min = '/media/mnichol3/tsb1/data/storms/2019-dorian/initial_best_track_interp_10min.txt'
    # txt_out_1min = '/media/mnichol3/tsb1/data/storms/2019-dorian/initial_best_track_interp_1min.txt'

    interp_dict = {'10T': '/media/mnichol3/tsb1/data/storms/2019-dorian/initial_best_track_interp_10min.txt',
                   'T': '/media/mnichol3/tsb1/data/storms/2019-dorian/initial_best_track_interp_1min.txt'}

    ############################################################################
    ############################################################################

    interp_freq = '1T'  # 1-minute interpolation
    # interp_freq = '10T'  # 10-minute interpolation
    write = False
    prnt = False
    pp = True

    meta = get_radius_meta(shp_path)
    pp_meta(meta)

    # df = track_shp_to_df(shp_path)
    # df = interp_df(df, interp_freq)
    #
    # if (prnt):
    #     print(df)
    #
    # if (write):
    #     df_to_csv(df, interp_dict[interp_freq])
    #
    # if (pp):
    #     pp_df(df)
    #
    # print('')

    ############################################################################
    ####################### Plotting Defs & Func Calls #########################
    ############################################################################
    # extent = [5.935, 40.031, -88.626, -40.285]
    # plot_track(shp_path, meta['storm_name'], meta['year'], extent=extent)
    # plot_track_from_df(df, meta['storm_name'], meta['year'], extent=extent, show=True, save=False, outpath=None)



if __name__ == '__main__':
    main()
