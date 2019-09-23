from datetime import datetime
import numpy as np
import pandas as pd

from nhc_gis_track import track_csv_to_df, pp_df
from dorian_sort_lightning import geodesic_point_buffer, get_quadrant_coords, get_files_for_date_time, process_flashes
from glm_utils import read_file_glm_egf
from localglmfile import LocalGLMFile



def main():
    track_path = '/media/mnichol3/tsb1/data/storms/2019-dorian/initial_best_track_interp_1min.txt'

    # Load the best track 1-min interpolation dataframe
    # Col names: date-time (index), storm_num, lat, lon, mslp, wind, ss
    # track_df = track_csv_to_df(track_path)

    center_coords = (26.8, -78.4)
    glm_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/aws'
    glm_fnames = get_files_for_date_time(glm_path, '2019-09-02 23:48:00')

    flashes = process_flashes(glm_fnames, center_coords, 450)

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





if __name__ == '__main__':
    main()
