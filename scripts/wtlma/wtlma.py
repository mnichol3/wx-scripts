"""
Author: Matt Nicholson

This file contains functions to read and analyze data files from the West Texas
LMA

Examples:

base_path = '/media/mnichol3/pmeyers1/MattNicholson/wtlma'
abs_path = join(base_path2, 'LYLOUT_190521_232000_0600.dat')
df = parse_file(abs_path)

get_files_day(base_path, '05-20-2019-21')

get_files_in_range(base_path, '5-20-2019-21:15', '5-21-2019-22:15', write=True)

"""
import pandas as pd
import numpy as np
from os.path import join, isdir, isfile
from os import listdir
import re
from datetime import datetime, timedelta
from math import sin, cos, sqrt, atan2, radians, degrees

from localwtlmafile import LocalWtlmaFile




def parse_file(abs_path, sub_t=None):
    """
    Opens and reads a WTLMA data file into a LocalWtlmaFile object

    Parameters
    ----------
    abs_path : str
        Absolute path, including filename, of the file to open


    Returns
    -------
    new_file_obj : LocalWtlmaFile object
    """
    center_lat_re = re.compile(r'\s(\d{2}\.\d{5,10})')
    center_lon_re = re.compile(r'\s(\D\d{3}\.\d{5,10})')
    center_alt_re = re.compile(r'\s(\d{1,3}.{1,3})$')   # can also be used as the range re
    coord_center = None
    max_diameter = None

    #abs_path = join(BASE_PATH, fname)

    with open(abs_path) as f:
        head = [next(f).rstrip() for x in range(46)]    # rstrip() removes trailing \n

    dt = datetime.strptime(head[5][17:], '%m/%d/%y %H:%M:%S')
    start_time = dt.strftime('%Y%m%d-%H%M')

    match1 = center_lat_re.search(head[8])
    if (match1):
        match2 = center_lon_re.search(head[8])
        if (match2):
            match3 = center_alt_re.search(head[8])
            if (match3):
                coord_center = (match1.group(1), match2.group(1), match3.group(1))

    match = center_alt_re.search(head[9])
    if (match):
        max_diameter = match.group(1)


    active_stations = head[12].rsplit(' ', 1)[-1]
    col_names = ['time', 'lat', 'lon', 'alt', 'r chi2', 'P', 'mask']
    data_df = pd.read_csv(abs_path, sep=r'\s{1,7}', names=col_names, skiprows=49, engine='python')

    # Convert event times from seconds of day to HH:MM:SS
    data_df['time'] = data_df['time'].apply(_sec_to_datetime_str)

    new_file_obj = LocalWtlmaFile(abs_path, start_time, coord_center, max_diameter, active_stations)

    if (sub_t):
        if (len(sub_t) != 5):
            raise ValueError('Invalid time subset argument')
        else:
            subs_df = data_df.loc[lambda data_df: ((data_df['time'] == sub_t) & (data_df['r chi2'] <= 1))]
            new_file_obj._set_data(subs_df)
            new_file_obj.start_time = new_file_obj.start_time.split('-')[0] + '-' + sub_t[:2] + sub_t[3:]
    else:
        new_file_obj._set_data(data_df)

    return new_file_obj



def get_avail_months(base_path, year):
    """
    Gets the months for which WTLMA data is stored locally

    Parameters
    ----------
    base_path : str
        Path to the parent WTLMA file directory
    year : str
        Year to query

    Returns
    -------
    list of str
        List of strings representing the months for which data is available
    """
    year = _year_formatter(year)

    abs_path = join(base_path, year)

    return [dir for dir in listdir(abs_path) if isdir(join(abs_path, dir))]



def get_avail_days(base_path, year, month):
    """
    Gets the days of a specified month & year that local WTLMA data is available

    Parameters
    ----------
    base_path : str
        Path to the parent WTLMA file directory
    year : str
        Year to query
    month : str
        Month to query, zero padded

    Returns
    -------
    list of str
        List of strings representing the days for which local WTLMA data is available
        for the given month & year
    """
    year = _year_formatter(year)
    month = _month_formatter(month)

    abs_path = join(base_path, year, month)

    return [dir for dir in listdir(abs_path) if isdir(join(abs_path, dir))]



def get_avail_hours(base_path, year, month, day):
    """
    Gets the hours for which data is available for the given year, month, and day

    Parameters
    ----------
    base_path : str
        Path to the parent WTLMA file directory
    year : str
        Year to query
    month : str
        Month to query, zero padded
    day : str
        Day to query, zero padded

    Returns
    -------
    list of str
        List of strings representing the hours for which local WTLMA data is
        available for the given year, month, and day
    """
    hours = []
    year = _year_formatter(year)
    month = _month_formatter(month)
    day = _day_formatter(day)

    abs_path = join(base_path, year, month, day)

    files = [f for f in listdir(abs_path) if isfile(join(abs_path, f))]
    for f in files:
        curr = f[14:16]
        if (curr not in hours and _is_number(curr)):
            hours.append(curr)

    hours = sorted(hours)

    return hours



def get_files_day(base_path, date):
    """
    Returns a list of local WTLMA filenames for the given date. If an hour is
    included in the date, only data files corresponding to that hour will be returned

    Parameters
    ----------
    base_path : str
        Path to the parent WTLMA file directory
    date : str
        Date of the desired data files.
        Format: MM-DD-YYYY or MM-DD-YYYY-HH

    Returns
    -------
    files : list of str
        List of local WTLMA filenames corresponding to the given date
    """
    hour = None

    if (not isinstance(date, datetime)):
        if (len(date) <= 10):
            date = datetime.strptime(date, '%m-%d-%Y')
        elif (len(date) > 10):
            date = datetime.strptime(date, '%m-%d-%Y-%H')
            hour = date.hour

    year = _year_formatter(date.year)
    month = _month_formatter(date.month)
    day = _day_formatter(date.day)

    abs_path = join(base_path, year, month, day)

    if (hour):
        dt_str = date.strftime('%y%m%d_%H')
        time_re = re.compile(r'LYLOUT_' + dt_str)
        files = [f for f in listdir(abs_path) if isfile(join(abs_path, f)) and f[-4:]=='.dat' and time_re.match(f)]
    else:
        files = [f for f in listdir(abs_path) if isfile(join(abs_path, f)) and f[-4:]=='.dat']

    return files



def get_files_in_range(base_path, start, end, write=False):
    """
    Returns a list of local WTLMA filenames for a given timespan. If write is True,
    the list of filenames will be written to a text file and saved to the local parent
    WTLMA directory

    Parameters
    ----------
    base_path : str
        Path to the parent WTLMA file directory
    start : str
        Start date & time
        Format: MM-DD-YYYY-HH:MM
    end : str
        End date & time
        Format: MM-DD-YYYY-HH:MM
    write : bool, optional
        If True, filenames get written to text file

    Returns
    -------
    result : list of str
        List of WTLMA filenames for the timespan defined by start & end
    """
    result = []

    start_dt = datetime.strptime(start, '%m-%d-%Y-%H:%M')
    end_dt = datetime.strptime(end, '%m-%d-%Y-%H:%M')

    for dt in _datetime_range(start_dt, end_dt):
        time = dt.strftime('%m-%d-%Y-%H')
        files = get_files_day(base_path, time)
        curr_fname = _build_fname(dt)
        if (curr_fname in files and curr_fname not in result):
            result.append(curr_fname)
    if (write):
        f_start = start_dt.strftime('%y%m%d-%H%M')
        f_end = end_dt.strftime('%y%m%d-%H%M')
        f_out = 'fnames_' + f_start + '_' + f_end + '.txt'
        abs_path = join(base_path, f_out)
        with open(abs_path, 'w') as f:
            for item in result:
                f.write("%s\n" % item)
    return result



def filter_by_dist(lma_df, dist, start_point, end_point, num_pts):
    """
    Filters the WTLMA dataframe to only include events that are within a certain
    distance of the line that defines the MRMS cross-section

    Parameters
    ----------
    lma_dt : Pandas DataFrame
        DataFrame containing the WTLMA data.
        Columns: 'time', 'lat', 'lon', 'alt', 'r chi2', 'P', 'mask'
    dist: int
        Distance threshold
    start_point : tuple of floats
        Coordinates of the point defining the beginning of the cross-section.
        Format: (lat, lon)
    end_point : tuple of floats
        Coordinates of the point defining the end of the cross-section.
        Format: (lat, lon)
    num_pts : int
        Number of geographic coordinate pairs to calculate between start_point &
        end_point

    Returns
    -------
    subs_df : Pandas DataFrame
        DataFrame containing the filtered WTLMA events
    coords : list of tuples
        List of coordinates of filtered WTLMA events (?)
        Format: (lat, lon)
    """
    if (not isinstance(dist, int)):
        raise TypeError('dist must be of type int')

    s_lat = start_point[0]
    s_lon = start_point[1]
    e_lat = end_point[0]
    e_lon = end_point[1]

    idxs = []
    coords = []
    alts = lma_df['alt'].tolist()
    xsect_az = int(calc_bearing(start_point, end_point))

    for pt1 in calc_geod_pts(start_point, end_point, num_pts=num_pts):
        for idx, pt2 in enumerate(list(zip(lma_df['lat'].tolist(), lma_df['lon'].tolist()))):
            # reverse the order of pt1 since the function returns the coordinates
            # as (lon, lat) and calc_dist wants (lat, lon)
            curr_az = int(calc_bearing((pt1[1], pt1[0]), pt2))
            if ((calc_dist((pt1[1], pt1[0]), pt2, units='m') <= dist) and (idx not in idxs) and (alts[idx] < 19000)):
                idxs.append(idx)
                coords.append([pt1[1], pt1[0]])

    # Remove repeat indexes from list
    # MUCH faster to use a set than another conditional inside the nested loops
    #idxs = list(set(idxs))
    subs_df = lma_df.iloc[idxs]

    return subs_df, coords



def calc_dist(point1, point2, units='km'):
    """
    Calculates the distance between two geographic coordinates in either km,
    the default, or in meters

    Parameters
    ----------
    point1 : tuple of floats
        First point
        Format: (lat, lon)
    point2 : tuple of floats
        Second point
        Format: (lat, lon)
    units : str, optional
        If units = m, the distance will be returned in meters instead of kilometers
    """
    R = 6373.0  # Approx. radius of Earth, in km

    lat1 = radians(point1[0])
    lon1 = radians(point1[1])
    lat2 = radians(point2[0])
    lon2 = radians(point2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    if (units == 'm'):
        distance = distance * 1000

    return distance



def calc_geod_pts(point1, point2, num_pts):
    """
    Calculates a number of points, num_pts, along a line defined by point1 & point2

    Parameters
    ----------
    point1 : tuple of floats
        First geographic coordinate pair
        Format: (lat, lon)
    point2 : tuple of floats
        Second geographic coordinate pair
        Format: (lat, lon)
    num_pts : int
        Number of coordinate pairs to calculate

    Returns
    -------
    Yields a tuple of floats
    Format: (lon, lat)
    """
    geod = Geod("+ellps=WGS84")
    points = geod.npts(lon1=point1[1], lat1=point1[0], lon2=point2[1],
                   lat2=point2[0], npts=num_pts)

    for pt in points:
        yield pt



def calc_bearing(point1, point2):
    """
    Calculates the bearing between two points

    https://gist.github.com/jeromer/2005586

    Parameters
    ----------
    point1 : tuple of floats
        Format: (lat, lon)
    point2 : tuple of floats
        Format: (lat, lon)

    Returns
    -------
    bearing : float
    """

    lat1 = radians(point1[0])
    lat2 = radians(point2[0])

    diffLong = radians(point2[1] - point1[1])

    x = sin(diffLong) * cos(lat2)
    y = math.cos(lat1) * sin(lat2) - (sin(lat1)
            * cos(lat2) * cos(diffLong))

    initial_bearing = atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = degrees(initial_bearing)
    bearing = (initial_bearing + 360) % 360
    return bearing



def bearing_diff(bearing1, bearing2):
    diff = abs(bearing1 - bearing2)
    if (diff > 360):
        diff = abs(360 - diff)
    if (diff > 180):
        diff = abs(360 - diff)
    return diff



def _year_formatter(year):
    if (isinstance(year, int)):
        return '{}'.format(year)
    elif (isinstance(month, str)):
        return '{}'.format(year)
    else:
        raise TypeError('Year must be of type int or str')



def _month_formatter(month):
    if (isinstance(month, int)):
        return '{:02}'.format(month)
    elif (isinstance(month, str)):
        return '{}'.format(month).zfill(2)
    else:
        raise TypeError('Month must be of type int or str')



def _day_formatter(day):
    if (isinstance(day, int)):
        return '{:02}'.format(day)
    elif (isinstance(day, str)):
        return '{}'.format(day).zfill(2)
    else:
        raise TypeError('Day must be of type int or str')



def _is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False



def _datetime_range(start, end):

    diff = (end + timedelta(minutes = 1)) - start

    for x in range(int(diff.total_seconds() / 60)):
        yield start + timedelta(minutes = x)



def _build_fname(date_time):
    date_time = date_time.replace(minute=_round_down(date_time.minute, 10))
    dt_str = date_time.strftime('%y%m%d_%H%M')
    fname = 'LYLOUT_' + dt_str + '00_0600.dat'
    return fname



def _parse_abs_path(base_path, fname):
    year = '20' + fname[7:9]
    month = fname[9:11]
    day = fname[11:13]
    path = join(base_path, year, month, day, fname)
    return path



def _round_down(num, divisor):
    """
    Ex:
    in : _round_down(19,10)
    out: 10
    """
    return num - (num % divisor)



def _sec_to_datetime_str(secs):
    td = timedelta(seconds=int(secs))
    d = {'days': td.days}
    d['hours'], rem = divmod(td.seconds, 3600)
    d['mins'], d['secs'] = divmod(rem, 60)

    for key, val in d.items():
        d[key] = '{0:02d}'.format(val)

    return d['hours'] + ':' + d['mins'] #+ ':' + d['secs']
