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

base_url = 'https://www.nohrsc.noaa.gov/snowfall/data/'


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



def main():
    parser = create_arg_parser()
    args = parser.parse_args()




if __name__ == '__main__':
    main()
