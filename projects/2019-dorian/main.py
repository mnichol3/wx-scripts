from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import sys
import os

from nhc_gis_track import track_csv_to_df, pp_df
from geo_utils import get_nrst_grid
from proj_utils import scan_to_geod, geod_to_scan
import glmfedfile

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



def cum_grid_10min(btcf, f_list_path, time_str):
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

    # Read the list of FED filenames, get a list of GLMFEDFile objects
    fed_objs = glmfedfile.read_file(fed_fnames)








def main():
    ################## !!! REMOVE !!! ##################
    from sys import exit
    ####################################################

    track_path_1min = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/initial_best_track_interp_1min.txt'
    track_path_60min = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/initial_best_track_interp_60min.txt'
    track_path_10min = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/initial_best_track_interp_10min.txt'

    glm_gridded_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded/nc'
    f_list_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded/file_lists'

    ############################################################################
    ########## Process the FED files for the lifespan of the storm #############
    ############################################################################
    cum_grid = init_cum_grid()

    track_df = track_csv_to_df(track_path_10min)

    for index, row in track_df.iterrows():
        fed_fnames = []
        cum_grid_10min = np.zeros((400, 400), dtype=int)

        # Best Track Center Fix geodetic lat & lon coords
        btcf_geod = (row['lat'], row['lon'])

        # Determine the scanning angle coordinates of the ABI Fixed Grid cell
        # that the btcf lat & lon coords fall into
        nrst_scan_dict = get_nrst_grid(btcf_geod[0], btcf_geod[1], fed_obj)
        btcf_scan = (nrst_scan_dict['y_idx'], nrst_scan_dict['x_idx'])
        print(btcf_scan)
        print(geod_to_scan(btcf_geod[0], btcf_geod[1]))
        exit(0)

        # Format the time string to match the file_list filename format
        curr_time = index.replace(':', '-').replace(' ', '_')

        cum_grid_10mins(btcf, f_list_path, time_str)


        break

    ############################################################################
    ############################################################################
    ############################################################################




if __name__ == '__main__':
    main()
