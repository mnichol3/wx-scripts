"""
15 Dec 2019
Author: Matt Nicholson

This file holds functions to download National Snowfall analysis files from
the National Weather Service National Operational Hydrologic Remote Sensing
Center (NOHRSC)
"""
from datetime import datetime
from os.path import join, isdir
from os import mkdir, getcwd
import argparse


def create_arg_parser():
    """
    Create & return a command line argument parser

    Parameters
    ----------
    None

    Return
    ------
    parser : argparse ArgumentParser obj

    Arguments
        -d, --date (str)
            Date to fetch files for. Format: YYYY-MM-DD-HH
        -p, --period (int)
            Accumulation period, i.e. 6-hr, 24-hr, 48-hr, 72-hr, season.
            Valid args:
                6 : 6-hr accumulation
                24 : 24-hr accumulation
                48 : 48-hr accumulation
                72 : 72-hr accumulation
                99 : Season-total accumulation
        -t, --type (str, optional)
            Type of data file to download. Default is 'nc'
            Valid args:
                'nc' : NetCDF file
                'tiff' : GeoTIFF
                'grib' : GRIB2 file
        -o, --out_path (str, optional)
            Directory to save the downloaded data file to. Default is current
            working directory

    """

    parse_desc = """A script to download National Snowfall analysis files from
    the National Weather Service National Operational Hydrologic Remote Sensing
    Center (NOHRSC)
    """
    curr_pwd = getcwd()

    parser = argparse.ArgumentParser(description=parse_desc)

    parser.add_argument('-d', '--date', metavar='date', required=True,
                        dest='date', action='store', type=str, default=None,
                        help='Date of snowfall analysis')

    parser.add_argument('-p', '--period', metavar='period', required=True,
                        dest='period', action='store', type=int, default=None,
                        help=('Period of snowfall accumulation (6: 6-hr, 24: 24-hr, '
                              '48: 48-hr, 72: 72-hr, 99: Season total)'))

    parser.add_argument('-t', '--type', metavar='f_type', required=False,
                        dest='f_type', action='store', type=str, default='nc',
                        help="Type of file to download ('nc': NetCDF, 'tiff': GeoTIFF, 'grib': GRIB2)"")

    parser.add_argument('-o', '--out_path', metavar='out_path', required=False,
                        dest='date', action='store', type=str, default=curr_pwd
                        help='Directory to download the snowfall analysis file to')

    return parser



def parse_date(date_arg):
    """
    Format the given date in order to create the analysis file download path

    Parameters
    ----------
    date_arg : str
        Format: 'YYYY-MM-DD'

    Return
    -------
    Tuple of str
        The first string contains the year & month, the second contains the
        year, month, day, & hour
    """
    hour_adj = -1
    valid_times = [0, 6, 12, 18]

    date_in = datetime.strptime(date_arg, '%Y-%m-%d-%H')

    # If the given hour is not one of the 4 synoptic times, find the closest previos
    # synoptic time
    if (date_in.hour not in valid_times):
        hour_adj = max([i for i in valid_times if date_in.hour > i])

    # First chunk, consisting of year and month in format YYYYMM
    chunk1 = datetime.strf('%Y%m', date_in)

    # Second chunk, format: YYYYMMDDHH
    if (hour_adj == -1):
        chunk2 = datetime.strf('%Y%m%d%H', date_in)
    else:
        chunk2 = datetime.strf('%Y%m%d', date_in)
        chunk2 = '{}{}'.format(chunk2, hour_adj)

    return (chunk1, chunk2)



def parse_url(cmd_args):
    """
    Parse the snowfall analysis file url

    Parameters
    ----------
    cmd_args : argparse obj

    Return
    ------
    url : str

    Example url:
        https://www.nohrsc.noaa.gov/snowfall/data/201912/sfav2_CONUS_6h_2019121518.nc
        https://www.nohrsc.noaa.gov/snowfall/data/201912/sfav2_CONUS_2019093012_to_2019121512.png
    """
    base_url = 'https://www.nohrsc.noaa.gov/snowfall/data/'

    date_chunk1, date_chunk2 = parse_date(cmd_args.date)



def parse_fname(cmd_args):
    """
    Parse the snowfall analysis file url

    Parameters
    ----------
    cmd_args : argparse obj

    Return
    -------
    f_name : str

    Ex fname:
        sfav2_CONUS_6h_2019121518.nc

    Ex seasonal accumulation fname:
        sfav2_CONUS_2018093012_to_2018121512.nc
    """
    season_start = '093012'     # Start month, day, & hour for seasonal accum

    f_bases = {'season': 'sfav2_CONUS_{}_to_{}',
               'hour':   'sfav2_CONUS_{}h_' }

    date_in = adjust_date(cmd_args)

    # Seasonal accumulation file
    if (cmd_args.period == 99):
        if (not check_ftype(cmd_args)):
            print('{} not valid for seasonal accumulation period. Downloading as NetCDF'.format(cmd_args.f_type))
            f_type = 'nc'
        else:
            f_type = cmd_args.f_type

        # If we are in the new year of the winter season (i.e., Jan 2020 of the
        # 2019-2020 winter season), adjust the start year defining the winter season
        if (date_in.month < 9):
            start_yr = date_in.year - 1
        else:
            start_yr = date_in.year

        date_start = '{}{}'.format(dt_in.year, season_start)

        if (dt_in.hour < 12):
            dt_in = dt_in.replace(day=dt_in.day - 1)

        dt_in = dt_in.replace(hour=12)

        else:

        date_end =
        f_name_base = f_bases['season']
        f_name_base = f_name_base.format()
        f_name = ''
    else:
        f_name_base = f_bases['hour']
        f_name = f_name_base.format(cmd_args.period)
        f_name  = f_name + in_date



def adjust_date(cmd_args):
    """
    Adjust the input date & time, if necessary

    Parameters
    ----------
    cmd_args : parseargs obj

    Return
    -------
    date_in : datetime object
    """
    valid_times_6 = [0, 6, 12, 18]
    valid_times_24 = [0, 12]

    date_in = datetime.strptime(cmd_args.date, '%Y-%m-%d-%H')

    if (cmd_args.period == 99):
        """
        Seasonal accumulation
        Set the ending hour to 12z and decrement the day, if necessary
        """
        if (date_in.hour < 12):
            date_in = date_in.replace(day = date_in.day - 1)
        date_in = date_in.replace(hour = 12)
    elif (cmd_args.period == 6):
        """
        6-hr accumulation
        Set the hour to the previous synoptic time if necessary
        """
        if (date_in.hour not in valid_times_6):
            new_hr = max([i for i in valid_times_6 if date_in.hour > i])
            date_in = date_in.replace(hour = new_hr)
    else:
        if (date_in.hour not in valid_times_24):
            new_hr = max([i for i in valid_times_24 if date_in.hour > i])
            date_in = date_in.replace(hour = new_hr)

    return date_in



def check_ftype(cmd_args):
    """
    Check that the file type & accumulation period combination is valid
    """
    if (cmd_args.period == 99 and cmd_args.f_type == 'grib'):
        return False
    else:
        return True




def main():
    parser = create_arg_parser()
    args = parser.parse_args()




if __name__ == '__main__':
    main()
