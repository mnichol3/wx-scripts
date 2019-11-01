from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import sys
import os
import re

from nhc_gis_track import track_csv_to_df, pp_df
from geo_utils import get_nrst_grid
from proj_utils import scan_to_geod, geod_to_scan
import glmfedfile
import cumgrid_10min

def pp_flashes(flashes):
    print('######################### NE Flashes #########################')
    for flash in flashes['ne']:
        print(flash)
        print('     Flash Area:     {}'.format(flash.area))
        print('     Flash Energy:   {}'.format(flash.energy))
        print('     Radial Dist:    {}'.format(flash.radial_dist))

    print('\n######################### NW Flashes #########################')
    for flash in flashes['nw']:
        print(flash)
        print('     Flash Area:     {}'.format(flash.area))
        print('     Flash Energy:   {}'.format(flash.energy))
        print('     Radial Dist:    {}'.format(flash.radial_dist))

    print('\n######################### SE Flashes #########################')
    for flash in flashes['se']:
        print(flash)
        print('     Flash Area:     {}'.format(flash.area))
        print('     Flash Energy:   {}'.format(flash.energy))
        print('     Radial Dist:    {}'.format(flash.radial_dist))


    print('\n######################### SW Flashes #########################')
    for flash in flashes['sw']:
        print(flash)
        print('     Flash Area:     {}'.format(flash.area))
        print('     Flash Energy:   {}'.format(flash.energy))
        print('     Radial Dist:    {}'.format(flash.radial_dist))



def run_process_flashes(track_path, glm_path, flash_out_paths):
    flashes_ne = []
    flashes_nw = []
    flashes_sw = []
    flashes_se = []

    # Load the best track 1-min interpolation dataframe
    # Col names: date-time (index), storm_num, lat, lon, mslp, wind, ss
    track_df = track_csv_to_df(track_path)

    # Iterate over the interpolated best track center coordinates
    for index, row in track_df.iterrows():
        print('Processing: {}'.format(index))

        # Lat & lon are type <class 'numpy.float64'>
        curr_dt = index
        curr_lat = row['lat']
        curr_lon = row['lon']

        glm_fnames = get_files_for_date_time(glm_path, curr_dt)

        flashes = process_flashes(glm_fnames, (curr_lat, curr_lon), 450)

        flashes_ne += flashes['ne']
        flashes_nw += flashes['nw']
        flashes_sw += flashes['sw']
        flashes_se += flashes['se']

        del flashes

    # When finished processing every time step, write the arrays of accumulated
    # flash objects to their own respective files in a format that can be read
    # into a Pandas Dataframe
    print('Writing NE flashes to file')
    with open(flash_out_paths['ne'], 'w') as fh_ne:
        fh_ne.write('date_time,x,y,area,energy,radial_dist\n')

        for flash in flashes_ne:
            fh_ne.write("{} {},{},{},{},{},{}\n".format(flash.date, flash.time,
                                                        flash.x, flash.y, flash.area,
                                                        flash.energy, flash.radial_dist))

    print('Writing NW flashes to file')
    with open(flash_out_paths['nw'], 'w') as fh_nw:
        fh_nw.write('date_time,x,y,area,energy,radial_dist\n')

        for flash in flashes_nw:
            fh_nw.write("{} {},{},{},{},{},{}\n".format(flash.date, flash.time,
                                                        flash.x, flash.y, flash.area,
                                                        flash.energy, flash.radial_dist))

    print('Writing SW flashes to file')
    with open(flash_out_paths['sw'], 'w') as fh_sw:
        fh_sw.write('date_time,x,y,area,energy,radial_dist\n')

        for flash in flashes_sw:
            fh_sw.write("{} {},{},{},{},{},{}\n".format(flash.date, flash.time,
                                                        flash.x, flash.y, flash.area,
                                                        flash.energy, flash.radial_dist))

    print('Writing SE flashes to file')
    with open(flash_out_paths['se'], 'w') as fh_se:
        fh_se.write('date_time,x,y,area,energy,radial_dist\n')

        for flash in flashes_se:
            fh_se.write("{} {},{},{},{},{},{}\n".format(flash.date, flash.time,
                                                        flash.x, flash.y, flash.area,
                                                        flash.energy, flash.radial_dist))



def valid_domain(btcf):
    """
    Ensure the BTCF is within the CONUS ABI Fixed Grid domain
    """
    min_lon = -113.0802
    max_lon = -52.9821
    min_lat = 15.1406
    max_lat = 51.3628

    return ((btcf[0] >= min_lat) and (btcf[0] <= max_lat) and (btcf[1] >= min_lon) and (btcf[1] <= max_lon))


def parse_fed_path(glm_gridded_path, fnames):
    """
    Create the absolute path to an FED file given the path to the parent
    directory and the FED filename(s)
    """
    fname_re = r'IXTR9\d_KNES_(\d{2})\d{4}_\w+\.(\d{8})\d+.nc'
    path_list = []

    if (not isinstance(fnames, list)):
        fnames = [fnames]

    for f in fnames:
        subdir = ''
        match = re.search(fname_re, f)
        if (match):
            real_day = match.group(1)
            subdir = match.group(2)

            # handle case where the two day strs in the filename mismatch at 2359z
            if (real_day != subdir[-2:]):
                subdir = subdir[:-2] + real_day

            abs_path = os.path.join(glm_gridded_path, subdir, f)
            path_list.append(abs_path)
    return path_list



def init_cum_grid():
    """
    Initialize the 400x400 grid to cumulate FED data on

    Parameters
    ----------
    None

    Returns
    -------
    cum_grid : numpy ndarray of int
        400 x 400 array containing zeros
    """
    cum_grid = np.zeros((400, 400), dtype=int)

    return cum_grid



def get_cum_grid_10min(btcf, f_list_path, time_str, glm_gridded_path):
    """
    btcf: (lat, lon)
    time_str : YYYY-MM-DD_HH-MM-SS
    """
    cum_grid = init_cum_grid()

    curr_f_list_path = os.path.join(f_list_path, time_str)
    curr_f_list_path = curr_f_list_path + '.txt'

    # Read the FED filenames from the file list for the given interpolated best track time
    with open(curr_f_list_path) as f:
        fed_fnames = f.read().splitlines()

    if (len(fed_fnames) != 0):
        f_abs_paths = parse_fed_path(glm_gridded_path, fed_fnames)
        # Read the list of FED filenames, get a list of GLMFEDFile objects
        fed_objs = glmfedfile.read_file(f_abs_paths)

        # Use the first FED object in the list to get the indices of the ABI Fixed Grid
        # cell that the btcf coordinates are located in
        grid_dict = get_nrst_grid(btcf[0], btcf[1], fed_objs[0])

        y_span = (grid_dict['y_idx'] - 200, grid_dict['y_idx'] + 200)
        x_span = (grid_dict['x_idx'] - 200, grid_dict['x_idx'] + 200)

        for obj in fed_objs:
            btcf_grid = obj.flash_extent_density[y_span[0] : y_span[1], x_span[0] : x_span[1]]

            # Will throw value error if btcf_grid.shape != (400, 400)
            # e.i., btcf_grid's domain falls outside of the CONUS ABI Fixed Grid domain
            cum_grid = np.add(cum_grid, btcf_grid)

        ref_grid_x = obj.x[x_span[0] : x_span[1]]
        ref_grid_y = obj.y[y_span[0] : y_span[1]]

        cum_grid_obj = cumgrid_10min.CumGrid_10min(time_str, btcf, cum_grid, ref_grid_x, ref_grid_y)

        return cum_grid_obj
    else:
        return -1



def main():
    ################## !!! REMOVE !!! ##################
    from sys import exit
    ####################################################

    track_path_10min = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/initial_best_track_interp_10min.txt'

    glm_gridded_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded/nc'
    f_list_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded/file_lists'

    cum_grid_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded/cum_grids'
    ref_grid_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded/ref_grids'

    ############################################################################
    ########## Process the FED files for the lifespan of the storm #############
    ############################################################################
    cum_grid_3hr = init_cum_grid()

    track_df = track_csv_to_df(track_path_10min)

    cum_grid_datetimes = []
    step_count = 0
    for index, row in track_df.iterrows():

        # Best Track Center Fix geodetic lat & lon coords
        btcf_geod = (row['lat'], row['lon'])

        # Format the time string to match the file_list filename format
        curr_time = index.replace(':', '-').replace(' ', '_')
        cum_grid_datetimes.append(curr_time)

        if (valid_domain(btcf_geod)):

            try:
                # Get 10-min cumulated FED object for the best track time step
                cum_grid_10min = get_cum_grid_10min(btcf_geod, f_list_path, curr_time, glm_gridded_path)

            except ValueError:
                pass
            else:
                if (not isinstance(cum_grid_10min, int)):
                    # cum_grid_datetimes.append(curr_time)

                    # If the 10-min cumulated grid was succesfully constructed, add
                    # it to the 3-hr cumulation grid
                    cum_grid_3hr = np.add(cum_grid_3hr, cum_grid_10min.cum_grid)

                    # Write ref grid to file
                    ref_grid_fname = cum_grid_10min.ref_datetime + '.txt'

                    ref_grid_zip = np.asarray([cum_grid_10min.ref_grid_y, cum_grid_10min.ref_grid_x])

                    np.savetxt(os.path.join(ref_grid_path, ref_grid_fname), ref_grid_zip)
                else:
                    print('Empty grid returned for {}'.format(curr_time))

        else:
            print(
                    ('BTCF ({0:.4f}, {1:.4f}) is not within the CONUS ABI Fixed'
                     ' Grid domain. Timestep: {2}'.format(btcf_geod[0], btcf_geod[1], index))
                 )

        step_count += 1

        if (step_count == 18):
            # Write cum_grid_3hr to file
            # Fname format: YYYY-MM-DD_HH-MM-SS'T'YYYY-MM-DD_HH-MM-SS
            # ex: 2019-08-24_12-00-00T2019-08-24_15-00-00.txt
            cum_grid_fname = '{}T{}.txt'.format(cum_grid_datetimes[0], cum_grid_datetimes[-1])

            # np.savetxt(os.path.join(cum_grid_path, cum_grid_fname), cum_grid_3hr)
            np.savetxt(os.path.join(cum_grid_path, cum_grid_fname), cum_grid_3hr, fmt='%1u')

            # Zero out the cum_grid_3hr
            cum_grid_3hr = init_cum_grid()
            cum_grid_datetimes = []
            step_count = 0

        ### !!! REMOVE !!! ###
        # if (step_count == 10):
        #     print(cum_grid_datetimes)
        #     exit(0)
        ######################


    ############################################################################
    ############################################################################
    ############################################################################




if __name__ == '__main__':
    main()
