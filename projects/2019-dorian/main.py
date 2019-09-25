from datetime import datetime
import numpy as np
import pandas as pd
import sys

from nhc_gis_track import track_csv_to_df, pp_df
from dorian_sort_lightning import geodesic_point_buffer, get_quadrant_coords, get_files_for_date_time, process_flashes, total_flashes_by_hour
from glm_utils import read_file_glm_egf
from localglmfile import LocalGLMFile



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




def main():
    track_path_1min = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/initial_best_track_interp_1min.txt'

    fname_flashes_ne = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/flash_stats/flashes_ne.txt'
    fname_flashes_nw = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/flash_stats/flashes_nw.txt'
    fname_flashes_sw = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/flash_stats/flashes_sw.txt'
    fname_flashes_se = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/flash_stats/flashes_se.txt'

    fname_hourly_totals = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/flash_stats/hourly_totals.txt'

    glm_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/aws'

    flash_paths = {'ne': fname_flashes_ne,
                   'nw': fname_flashes_nw,
                   'sw': fname_flashes_sw,
                   'se': fname_flashes_se}

    # run_process_flashes(track_path_1min, glm_path, flash_paths)
    # total_flashes_by_hour(flash_paths, write=True, outpath=fname_hourly_totals)
    total_flashes_by_hour(flash_paths, pp=True)



if __name__ == '__main__':
    main()
