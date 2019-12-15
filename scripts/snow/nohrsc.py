"""
15 Dec 2019
Author: Matt Nicholson

This file holds functions to download National Snowfall analysis files from
the National Weather Service National Operational Hydrologic Remote Sensing
Center (NOHRSC)
"""
from datetime import datetime
from os.path import join, isdir
from os import makedirs, getcwd, listdir, remove
import argparse
import wget



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
                        help="Type of file to download ('nc': NetCDF, 'tif': GeoTIFF)")

    parser.add_argument('-o', '--out_path', metavar='out_path', required=False,
                        dest='out_path', action='store', type=str, default=curr_pwd,
                        help='Directory to download the snowfall analysis file to')

    parser.add_argument('-f', '--ftree', required=False, dest='file_tree',
                        action='store_true', default=False,
                        help='If True, save files to out_path/snowfall/date/files')

    return parser



def parse_url(cmd_args, f_name=None):
    """
    Parse the snowfall analysis file url

    Parameters
    ----------
    cmd_args : argparse.Namespace obj
        Parsed command line arguments
    f_name : str, optional
        Target filename. Can be passed to save another call to parse_fname

    Return
    ------
    url : str

    Example url:
        https://www.nohrsc.noaa.gov/snowfall/data/201912/sfav2_CONUS_6h_2019121518.nc
        https://www.nohrsc.noaa.gov/snowfall/data/201912/sfav2_CONUS_2019093012_to_2019121512.png
    """
    base_url = 'https://www.nohrsc.noaa.gov/snowfall/data'

    path_date = _get_path_date(cmd_args)

    if (not f_name):
        f_name = parse_fname(cmd_args)

    url = '{}/{}/{}'.format(base_url, path_date, f_name)

    return url



def parse_fname(cmd_args):
    """
    Parse the snowfall analysis file url

    Parameters
    ----------
    cmd_args : argparse.Namespace obj
        Parsed command line arguments

    Return
    -------
    f_name : str

    Ex fname:
        sfav2_CONUS_6h_2019121518.nc

    Ex seasonal accumulation fname:
        sfav2_CONUS_2018093012_to_2018121512.nc
    """

    # Seasonal accumulation file
    if (cmd_args.period == 99):
        f_name = _parse_fname_season(cmd_args)
    else:
        f_name = _parse_fname_hour(cmd_args)

    return f_name



def adjust_date(cmd_args):
    """
    Adjust the input date & time, if necessary

    Parameters
    ----------
    cmd_args : argparse.Namespace obj
        Parsed command line arguments

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



def download(cmd_args):
    """
    Download a snow analysis file from NOHRSC

    Parameters
    ----------
    cmd_args : argparse.Namespace obj
        Parsed command line arguments

    Return
    ------
    f_path : str
        Absolute path of the downloaded file
    """
    target_fname = parse_fname(cmd_args)
    out_path = _validate_outpath(cmd_args)
    out_path = join(out_path, target_fname)
    print('\nDownloading {} to {}'.format(target_fname, out_path))

    target_url = parse_url(cmd_args, f_name = target_fname)

    wget.download(target_url, out_path)



################################################################################
############################### Helper Functions ###############################
################################################################################


def check_ftype(cmd_args):
    """
    Check that the file type & accumulation period combination is valid
    """
    if (cmd_args.period == 99 and cmd_args.f_type == 'grib'):
        return False
    else:
        return True



def _get_path_date(cmd_args, delim=None):
    date_in = datetime.strptime(cmd_args.date, '%Y-%m-%d-%H')
    if (delim is not None):
        if (not isinstance(delim, str)):
            raise ValueError('Delimiter argument must be of type str')
        pattern = '%Y{}%m'.format(delim)
    else:
        pattern = '%Y%m'
    path_date = date_in.strftime(pattern)
    return path_date



def _parse_fname_season(cmd_args):
    """
    Parse the filename for a seasonal-accumulation file

    Ex seasonal accumulation fname: sfav2_CONUS_2018093012_to_2018121512.nc
    """
    f_name_base = 'sfav2_CONUS_{}_to_{}'
    season_start = '093012'     # Start month, day, & hour for seasonal accum

    date_in = adjust_date(cmd_args)

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

    date_start = '{}{}'.format(start_yr, season_start)
    date_end = datetime.strftime(date_in, '%Y%m%d%H')

    f_name = f_name_base.format(date_start, date_end)

    f_name = '{}.{}'.format(f_name, f_type)

    return f_name



def _parse_fname_hour(cmd_args):
    """
    Parse the filename for a 6-, 24-, 48-, or 72-hour accumulation file

    Ex fname: sfav2_CONUS_6h_2019121518.nc
    """
    f_name_base = 'sfav2_CONUS_{}h_{}'

    date_in = adjust_date(cmd_args)
    valid_date = date_in.strftime('%Y%m%d%H')

    f_name = f_name_base.format(cmd_args.period, valid_date)

    f_name = '{}.{}'.format(f_name, cmd_args.f_type)

    return f_name



def _validate_outpath(cmd_args):
    if (cmd_args.file_tree):
        dir_date = _get_path_date(cmd_args, delim='-')
        dirs = join(cmd_args.out_path, 'snowfall', dir_date)
    else:
        dirs = cmd_args.out_path
    if (not isdir(dirs)):
        makedirs(dirs)
    return dirs



def main():

    # Create a parser instance
    parser = create_arg_parser()

    # Parse the command line argmuments. Returns an argparse.Namespace obj
    args = parser.parse_args()

    download(args)




if __name__ == '__main__':
    main()
