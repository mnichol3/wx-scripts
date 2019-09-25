from os.path import join, isdir, isfile
from os import walk, listdir
from datetime import datetime, timedelta
import pandas as pd
import re
import numpy as np
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt

############ Imports for geodesic point buffer funcs #########
import pyproj
from shapely.ops import transform, polygonize
from shapely.geometry import Point, LineString
from functools import partial
##############################################################

from glm_utils import read_file_glm_egf
from glmflash import GLMFlash


def pp_dirs(base_path):
    for day_subdir in listdir(base_path):
        curr_subdir = join(base_path, day_subdir)
        print(day_subdir)

        for hour_subdir in listdir(curr_subdir):
            curr_sub_subdir = join(curr_subdir, hour_subdir)
            print('  |-- {}'.format(hour_subdir))

            for f in listdir(curr_sub_subdir):
                if (isfile(join(curr_sub_subdir, f))):
                    print('  |    |-- {}'.format(f))
            print('  |')
        print('\n')



def get_files_for_date_time(base_path, date_time):
    """
    Get the GLM files for a given date & time

    Parameters
    ----------
    base_path : str
        Path to the local parent GLM file directory
    date_time : str
        Date and time of the desired GLM files.
        Format: YYYY-MM-DD HH:MM:SS
    """
    fnames = []
    scantime_re = re.compile(r'_s(\d{11})')

    # date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    date_time = datetime.strptime(date_time[:-3], '%Y-%m-%d %H:%M')

    # Parse the subdirectory path for the desired date & time of the GLM file
    subdir_path = join(base_path, str(date_time.timetuple().tm_yday), str(date_time.hour).zfill(2))

    file_count = 0
    for f in listdir(subdir_path):

        # Iterate through the files in the date & hour subdirectory tree and
        # attempt to match the starting scan date & time in the file name
        match = re.search(scantime_re, f)
        if (match):

            # If the scan date & time in the file name is matched, create
            # a datetime object from it to compare to our desired datetime obj
            f_scantime = datetime.strptime(match.group(1), '%Y%j%H%M')
            if ((f_scantime == date_time) and isfile(join(subdir_path, f))):
                fnames.append(join(subdir_path, f))

                # Since we're looking for the GLM files for a given hour & minute,
                # and GLM publishes at most 3 files a minute, once we find our 3
                # files we can break the loop and save some execution time
                file_count += 1
                if (file_count >= 3):
                    break
    return fnames



def process_flashes(glm_fnames, center_coords, radius):
    """
    Parameters
    -----------
    glm_fnames : list of str
        List of absolute paths (including file names) for the set of GLM files
        to be opened & processed
    center_coords : tuple of floats
        Coordinates of the best track center for the time corresponding to the
        GLM files. Format: (lat, lon)
    radius : int
        Desired radius of the geodesic point buffer (in km)

    """
    flashes = {}
    flashes_ne = []
    flashes_nw = []
    flashes_sw = []
    flashes_se = []


    range_buffer = geodesic_point_buffer(center_coords[0], center_coords[1], 450)

    nsew_pts = get_quadrant_coords(buff_obj=range_buffer)

    quadrants = get_quadrants(range_buffer, nsew_pts)

    for f in glm_fnames:
        curr_obj = read_file_glm_egf(f, product='f')

        for idx, curr_x in enumerate(curr_obj.data['x']):
            curr_pt = Point(curr_x, curr_obj.data['y'][idx])
            if (quadrants['ne'].contains(curr_pt)):
                flashes_ne.append(GLMFlash(curr_obj.scan_date, curr_obj.scan_time,
                                           curr_x, curr_obj.data['y'][idx],
                                           curr_obj.data['data']['area'][idx],
                                           curr_obj.data['data']['energy'][idx],
                                           center_coords))
            elif (quadrants['nw'].contains(curr_pt)):
                flashes_nw.append(GLMFlash(curr_obj.scan_date, curr_obj.scan_time,
                                           curr_x, curr_obj.data['y'][idx],
                                           curr_obj.data['data']['area'][idx],
                                           curr_obj.data['data']['energy'][idx],
                                           center_coords))
            elif (quadrants['sw'].contains(curr_pt)):
                flashes_sw.append(GLMFlash(curr_obj.scan_date, curr_obj.scan_time,
                                           curr_x, curr_obj.data['y'][idx],
                                           curr_obj.data['data']['area'][idx],
                                           curr_obj.data['data']['energy'][idx],
                                           center_coords))
            elif (quadrants['se'].contains(curr_pt)):
                flashes_se.append(GLMFlash(curr_obj.scan_date, curr_obj.scan_time,
                                           curr_x, curr_obj.data['y'][idx],
                                           curr_obj.data['data']['area'][idx],
                                           curr_obj.data['data']['energy'][idx],
                                           center_coords))
    flashes['ne'] = flashes_ne
    flashes['nw'] = flashes_nw
    flashes['sw'] = flashes_sw
    flashes['se'] = flashes_se

    return flashes



def geodesic_point_buffer(lat, lon, km):
    """
    Creates a circle on on the earth's surface, centered at (lat, lon) with
    radius of km

    Parameters
    ------------
    lat : float
        Latitude coordinate of the circle's center in decimal degrees
    lon : float
        Longitude coordinate of the circle's center in decimal degrees
    km : int
        Radius of the circle, in km


    Returns
    ------------
    ring : LinearRing object
        LinearRing object containing the coordinates of the circle's edge.

        To access the coordinates:
            lats = [float(x[1]) for x in ring.coords[:]]
            lons = [float(x[0]) for x in ring.coords[:]]

            for idx, lat in enumerate(lats):
                print('lat: {0:.3f}, lon: {1:.3f}'.format(lat, lons[idx]))


    Dependencies
    -------------
    > pyproj
    > functools.partial
    > shapely.geometry.Point
    > shapely.ops.transform
    """

    proj_wgs84 = pyproj.Proj(init='epsg:4326')

    # Azimuthal equidistant projection
    aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
    project = partial(
        pyproj.transform,
        pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
        proj_wgs84)
    buf = Point(0, 0).buffer(km * 1000)  # distance in metres

    ring = transform(project, buf).exterior

    return ring



def get_quadrant_coords(buff_obj=None, coords=None, pprint=False):
    """
    Finds the max lon, max lat, min lon, & min lat coords in order to divide a
    geodesic_point_buffer into NE, NW, SE, & SW quadrants. Though both arguments
    are optional, one must be given

    Parameters
    ----------
    buff_obj : LinearRing object, optional
        LinearRing object returned by geodesic_point_buffer()
    coords : tuple of (lats, lons), optional
        Tuple of coordinates representing a geodesic point buffer
    pprint : Bool, optional
        If True, the dictionary & keys will be printed. Default: False

    Returns
    -------
    coord_dict : Dictionary of {str: (float, float)}
        Dictionary containing the coordinates of the northern-, southern- eastern-,
        and western-most coordinates.
        Keys: ['n', 'e', 's', 'w']
    """
    if (buff_obj):
        # Extract the coordinates from the LinearRing object
        lats = [float(x[1]) for x in buff_obj.coords[:]]
        lons = [float(x[0]) for x in buff_obj.coords[:]]
    elif (coord_list):
        # Extract the coordinate lists from the coords tuple
        lats = coords[0]
        lons = coords[1]
    else:
        raise ValueError("Both 'buff_obj' and 'coords' arguments cannot be None")

    coord_dict = {}

    n_idx = lats.index(max(lats))
    s_idx = lats.index(min(lats))

    e_idx = lons.index(max(lons))
    w_idx = lons.index(min(lons))

    coord_dict['n'] = (lats[n_idx], lons[n_idx])
    coord_dict['s'] = (lats[s_idx], lons[s_idx])
    coord_dict['e'] = (lats[e_idx], lons[e_idx])
    coord_dict['w'] = (lats[w_idx], lons[w_idx])

    if (pprint):
        for key, val in coord_dict.items():
            print('{}: {:.3f}, {:.3f}'.format(key, val[0], val[1]))

    return coord_dict



def get_quadrants(range_buffer, nsew_pts):
    """
    Split a geodesic point buffer into 4 quadrants and return them as
    a dictionary of polygons
    """
    quad_dict = {}
    quarters = []

    # Create lines to bisect the circular point buffer with
    horiz_bisect_line = LineString([Point(nsew_pts['w'][1] - 1, nsew_pts['w'][0]),
                                    Point(nsew_pts['e'][1] + 1, nsew_pts['e'][0])])

    verti_bisect_line = LineString([Point(nsew_pts['s'][1], nsew_pts['s'][0] - 1),
                                    Point(nsew_pts['n'][1], nsew_pts['n'][0] + 1)])

    # Bisect the cilcular polygon, yielding two halves
    halves = horiz_bisect_line.union(LineString(list(range_buffer.coords)))
    halves = polygonize(halves)

    # Bisect each of the halves created above, creating 4 quadrants
    for half in halves:
        quarter = verti_bisect_line.union(LineString(list(half.exterior.coords)))
        quarter = polygonize(quarter)
        quarters.append(quarter)

    quadrants = []
    for geom in quarters:
        for g in geom:
            quadrants.append(g)

    sort_1 = sorted(quadrants, key = lambda q: q.centroid.x)
    west_pts = sort_1[:2]
    east_pts = sort_1[2:]

    sort_west = sorted(west_pts, key = lambda p: p.centroid.y)
    sort_east = sorted(east_pts, key = lambda p: p.centroid.y)

    quad_dict['sw'] = sort_west[0]
    quad_dict['nw'] = sort_west[1]

    quad_dict['se'] = sort_east[0]
    quad_dict['ne'] = sort_east[1]

    return quad_dict



def total_flashes_by_hour(flash_fnames, write=False, outpath=None, pp=False):
    """
    Total the amount of flashes per hour for each quadrant

    Parameters
    -----------
    flash_names : dict of str
        Dictionary where each key is a quadrant and the value is the respective
        filtered flash file

        Keys: 'ne', 'nw', 'sw', 'se'
    write : Bool, optional
        If True, write the resulting dataframe to a file specified by 'outpath'
        Default value is False
    outpath : str, optional
        Path, including the filename, to save the dataframe to. Must be given if
        'write' is True. Default value is None
    pp : Bool, optional
        If True, pretty print the DataFrame. Default value is False

    Returns
    --------
    flash_count_df : Pandas DataFrame
        DataFrame containing total flash amounts for each hour in each quadrant.
        Columns: 'date_time', 'ne', 'nw', 'sw', 'se'
            date_time format: YYYY-MM-DD-HH
    """
    flash_counts = {'ne': {},
                    'nw': {},
                    'sw': {},
                    'se': {}}

    t_0 = datetime.strptime('2019-08-24 12:00', '%Y-%m-%d %H:%M')

    # Change ending hour from 00:00 to 01:00 because of how range() works
    t_f = datetime.strptime('2019-09-09 01:00', '%Y-%m-%d %H:%M')

    date_range = [t_0 + timedelta(seconds=x*3600) for x in range(int((t_f - t_0).total_seconds() / 3600))]

    # Set each datetime value in each quadrant to 0
    for dt in date_range:
        curr_dt = datetime.strftime(dt, '%Y-%m-%d-%H')
        for quad, val in flash_counts.items():
            flash_counts[quad][curr_dt] = 0

    for quad, fname in flash_fnames.items():
        print('Processing {}'.format(quad.upper()))

        with open(fname, 'r') as fh:

            # Skip first line in the file which contains data column names
            next(fh)

            for line in fh:
                curr_dt = line.split(',')[0]
                curr_dt = datetime.strptime(curr_dt, '%m-%d-%Y %H:%M')
                curr_dt_str = datetime.strftime(curr_dt, '%Y-%m-%d-%H')

                flash_counts[quad][curr_dt_str] += 1


    # for key, val in flash_counts['ne'].items():
    #     print('{}z --> {}'.format(key, val))

    flash_count_df = pd.DataFrame.from_dict(flash_counts, orient='columns').reset_index()
    flash_count_df.columns = ['date_time', 'ne', 'nw', 'sw', 'se']

    if ((write) and (outpath is not None)):
        print('     Writing DataFrame to File...')
        flash_count_df.to_csv(outpath, sep=',', header=True, index=False)

    if (pp):
        import time
        print('{}  {}  {}  {}  {}  {}'.format('\nidx', '  date_time  ', ' ne ', ' nw ', ' sw ', ' se '))
        print('{}  {}  {}  {}  {}  {}'.format('-'*3, '-'*13, '-'*4, '-'*4, '-'*4, '-'*4))

        for index, row in flash_count_df.iterrows():
            print('{}  {}  {}  {}  {}  {}'.format(str(index).ljust(3, ' '),
                                         row['date_time'], str(row['ne']).ljust(4, ' '),
                                         str(row['nw']).ljust(4, ' '),
                                         str(row['sw']).ljust(4, ' '),
                                         str(row['se']).ljust(4, ' ')))
            time.sleep(0.5)

    return flash_count_df



def plot_flashes_vs_intensity(flash_count_df, best_track_df):
    """

    Parameters
    ----------
    flash_count_df : str or Pandas DataFrame
        Either:
            - Absolute path of the file containing flash count data to be read
              into a DataFrame
              ### or ###
            - DataFrame containing flash count data
    best_track_df : str or Pandas DataFrame
        Either:
            - Absolute path of the file containing interpolated Best Track data
              to be read into a DataFrame
              ### or ###
            - DataFrame containing Best Track data
    """
    x_tick_labels = []
    x_ticks = []
    # Validate flash_count_df arg
    if (isinstance(flash_count_df, str)):
        flash_count_df = pd.read_csv(flash_count_df, sep=',', header=0)
    elif (not isinstance(flash_count_df, pd.DataFrame)):
        raise TypeError(("'flash_count_df' arg must be an instance of str or Pandas "
                         "DataFrame, got {}".format(type(flash_count_df))))

    # Validate best_track_dfs arg
    if (isinstance(best_track_df, str)):
        best_track_df = pd.read_csv(best_track_df, sep=',', header=0)
    elif (not isinstance(best_track_df, pd.DataFrame)):
        raise TypeError(("'best_track_df' arg must be an instance of str or Pandas "
                        "DataFrame, got {}".format(type(best_track_df))))

    # Make sure the two DataFrames have the same length (i.e., the same number of data points)
    if (len(best_track_df.index) != len(flash_count_df.index)):
        raise ValueError(("'best_track_df' and 'flash_count_df' must have same length\n"
                          "Len best_track_df: {}, Len flash_count_df: {}".format(
                                    len(best_track_df.index), len(flash_count_df.index))))


    # Get a list of date_time strings for the x-tick labels
    for index, row in flash_count_df.iterrows():
        if (index % 12 == 0):
            x_ticks.append(index)
            x_tick_labels.append(row['date_time'][5:] + 'z')

    # Create a figure
    fig, ax1 = plt.subplots(figsize = (8, 8))

    ax1.set_xlabel('Date & Time')
    ax1.set_ylabel('GLM Flashes (1/hour)')
    ax1.plot(flash_count_df.index, flash_count_df['ne'], color='red')
    ax1.plot(flash_count_df.index, flash_count_df['nw'], color='green')
    ax1.plot(flash_count_df.index, flash_count_df['sw'], color='blue')
    ax1.plot(flash_count_df.index, flash_count_df['se'], color='orange')
    plt.xticks(x_ticks, x_tick_labels, rotation=45, ha='right')
    plt.legend(('NE Quadrant', 'NW Quadrant', 'SW Quadrant', 'SE Quadrant'), loc='upper right')

    # Create a twin x axis to plot intensity on
    ax2 = ax1.twinx()
    ax2_color = 'fuchsia'
    ax2.set_ylabel('Mean Sea Level Pressure (mb)', color=ax2_color)
    ax2.plot(best_track_df.index, best_track_df['mslp'], color=ax2_color)
    ax2.tick_params(axis='y', labelcolor=ax2_color)
    plt.yticks(np.arange(900, 1020, 10))
    plt.title('Hurricane Dorian GLM-Observed FLash Count & Mean Sea Level Pressure vs. Time')

    plt.show()
