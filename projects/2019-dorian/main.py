from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import sys
import os
import re
import glob

from nhc_gis_track import track_csv_to_df, pp_df
from dorian_sort_lightning import process_flashes, total_flashes_by_hour, plot_flashes_vs_intensity
from glm_utils import read_file_glm_egf
from localglmfile import LocalGLMFile

from dorian_sort_lightning import geodesic_point_buffer, get_quadrant_coords

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



def get_fed_files(base_path):
    from localflashextentfile import LocalFlashExtentFile
    ############################################################################
    #### Get the names of the Flash Extent NetCDF files produced by glmtools ###
    ############################################################################
    total_f_count = 0
    for subdir in os.listdir(base_path):
        curr_dir = os.path.join(base_path, subdir)
        for hr in os.listdir(curr_dir):
            curr_hr = os.path.join(curr_dir, hr)
            abs_path = '{}/{}'.format(curr_hr, '*_flash_extent.nc')

            for file in glob.glob(abs_path):
                curr_FE_file = LocalFlashExtentFile(file)
                print(curr_FE_file)
                total_f_count += 1

    print('--- {} total GLM FE files present ---'.format(total_f_count))



def check_data_coverage(base_path):
    total_f_count = 0
    for subdir in os.listdir(base_path):
        curr_dir = os.path.join(base_path, subdir)
        for hr in os.listdir(curr_dir):
            curr_hr = os.path.join(curr_dir, hr)
            abs_path = '{}/{}'.format(curr_hr, '*_flash_extent.nc')
            f_count = 0
            for file in glob.glob(abs_path):
                f_count += 1
                total_f_count += 1

            short_dir = curr_hr.split('/', 9)[-1]
            if (f_count != 60):
                bad_msg = '!!! {} is bad, {}/60 FE files present (missing {})'
                bad_msg = bad_msg.format(short_dir, f_count, 60 - f_count)
                print(bad_msg)
            else:
                # print('    {} is ok, {}/60 FE files present'.format(short_dir, f_count))
                print('    {} is ok'.format(short_dir))
    print('--- {} total GLM FE files present ---'.format(total_f_count))



def get_fed_files(parent_dir, fix_datetime):
    """
    Not pretty, not efficient, but works

    Get the FED files for a given datetime

    datetime format: 2019-08-24 12:00:00

    IXTR98_KNES_262350_123161.2019082623.nc
    """
    fed_fnames = []
    out_dir = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded/file_lists'

    mid_dt = datetime.strptime(fix_datetime, "%Y-%m-%d %H:%M:%S")
    curr_dt = mid_dt - timedelta(seconds=240)    # 4 mins before curr_dt
    max_dt = mid_dt + timedelta(seconds=300)     # 5 mins after curr_dt

    subdir = datetime.strftime(curr_dt, "%Y%m%d")
    abs_path = os.path.join(parent_dir, subdir)

    fname_re = r'(IXTR9\d_KNES_{}_\w+\.{}.nc)' # Might need \ in front of .
    # fname_re = r'(IXTR9\d_KNES_\d{6}_\w+\.\d{10}.nc)'
    fname_re = fname_re.format(datetime.strftime(curr_dt, "%d%H%M"), datetime.strftime(curr_dt, "%Y%m%d%H"))
    # When the Best Track fix time is 00:00, we'll need files from directories
    # representing two different days
    if (mid_dt.strftime('%H:%M') == '00:00'):
        subdir = datetime.strftime(curr_dt, "%Y%m%d")
        abs_path = os.path.join(parent_dir, subdir)

        for m in range(1, 11):
            for f in os.listdir(abs_path):
                match = re.search(fname_re, f)
                if (match):
                    curr_fname = match.group(1)
                    fed_fnames.append(curr_fname)
                    break
            curr_dt += timedelta(seconds=60)
            if (curr_dt > max_dt):
                break
            if (curr_dt.minute == 59):
                adjusted_dt = curr_dt + timedelta(hours=1)
                fname_re = r'(IXTR9\d_KNES_{}_\w+\.{}\d\d.nc)'
                fname_re = fname_re.format(datetime.strftime(curr_dt, "%d%H%M"),
                                           datetime.strftime(adjusted_dt, "%Y%m%d"))
            else:
                fname_re = r'(IXTR9\d_KNES_{}_\w+\.{}\d\d.nc)'
                fname_re = fname_re.format(datetime.strftime(curr_dt, "%d%H%M"),
                                           datetime.strftime(curr_dt, "%Y%m%d"))


        # Update directory we're looking in and go again
        subdir = datetime.strftime(curr_dt, "%Y%m%d")
        abs_path = os.path.join(parent_dir, subdir)
        for m in range(1, 11):
            for f in os.listdir(abs_path):
                match = re.search(fname_re, f)
                if (match):
                    curr_fname = match.group(1)
                    fed_fnames.append(curr_fname)
                    break
            curr_dt += timedelta(seconds=60)
            if (curr_dt > max_dt):
                break
            if (curr_dt.minute == 59):
                adjusted_dt = curr_dt + timedelta(hours=1)
                fname_re = r'(IXTR9\d_KNES_{}_\w+\.{}\d\d.nc)'
                fname_re = fname_re.format(datetime.strftime(curr_dt, "%d%H%M"),
                                           datetime.strftime(adjusted_dt, "%Y%m%d"))
            else:
                fname_re = r'(IXTR9\d_KNES_{}_\w+\.{}\d\d.nc)'
                fname_re = fname_re.format(datetime.strftime(curr_dt, "%d%H%M"),
                                           datetime.strftime(curr_dt, "%Y%m%d"))
    else:
        dir_files = os.listdir(abs_path)
        dir_files.sort()
        for m in range(1, 11):
            for f in dir_files:
                match = re.search(fname_re, f)
                if (match):
                    curr_fname = match.group(1)
                    fed_fnames.append(curr_fname)
                    break
            curr_dt += timedelta(seconds=60)

            if (curr_dt > max_dt):
                break

            if (curr_dt.minute == 59):
                adjusted_dt = curr_dt + timedelta(hours=1)
                fname_re = r'(IXTR9\d_KNES_{}_\w+\.{}\d\d.nc)'
                fname_re = fname_re.format(datetime.strftime(curr_dt, "%d%H%M"),
                                           datetime.strftime(adjusted_dt, "%Y%m%d"))
            else:
                fname_re = r'(IXTR9\d_KNES_{}_\w+\.{}\d\d.nc)'
                fname_re = fname_re.format(datetime.strftime(curr_dt, "%d%H%M"),
                                           datetime.strftime(curr_dt, "%Y%m%d"))

    f_name = mid_dt.strftime("%Y-%m-%d_%H-%M-%S")
    f_name += '.txt'
    f_path = os.path.join(out_dir, f_name)

    with open(f_path, 'w') as fh:
        for fed_file in fed_fnames:
            fh.write('{}\n'.format(fed_file))

    return fed_fnames






def main():
    track_path_1min = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/initial_best_track_interp_1min.txt'
    track_path_60min = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/initial_best_track_interp_60min.txt'
    track_path_10min = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/initial_best_track_interp_10min.txt'

    fname_flashes_ne = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/flash_stats/flashes_ne.txt'
    fname_flashes_nw = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/flash_stats/flashes_nw.txt'
    fname_flashes_sw = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/flash_stats/flashes_sw.txt'
    fname_flashes_se = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/flash_stats/flashes_se.txt'

    fname_hourly_totals = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/flash_stats/hourly_totals.txt'

    glm_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/aws'
    glm_gridded_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded/nc'

    # flash_paths = {'ne': fname_flashes_ne,
    #                'nw': fname_flashes_nw,
    #                'sw': fname_flashes_sw,
    #                'se': fname_flashes_se}
    #
    # # run_process_flashes(track_path_1min, glm_path, flash_paths)
    # # total_flashes_by_hour(flash_paths, write=True, outpath=fname_hourly_totals)
    # # total_flashes_by_hour(flash_paths, pp=True)
    #
    # # flash_count_df = pd.read_csv(fname_hourly_totals, sep=',', header=0)
    # # print(flash_count_df)
    #
    # # plot_flashes_vs_intensity(fname_hourly_totals, track_path_60min)
    # buff = geodesic_point_buffer(25.8, -72.55, 450)
    # quad_coords = get_quadrant_coords(buff)
    #
    # n = quad_coords['n']
    # s = quad_coords['s']
    # e = quad_coords['e']
    # w = quad_coords['w']


    ############################################################################
    ###### Match FED File names to Interpolated Best Track Center fixes ########
    ############################################################################
    # test_dt = '2019-09-08 20:40:00'
    # print('Fetching files for {}...'.format(test_dt))
    # fed_files = get_fed_files(glm_gridded_path, test_dt)
    # for f in fed_files:
    #     print('     {}'.format(f))

    # track_df = track_csv_to_df(track_path_10min)
    # for index, row in track_df.iterrows():
    #     print('Fetching files for {}...'.format(index))
    #     fed_files = get_fed_files(glm_gridded_path, index)
    #     for f in fed_files:
    #         print('     {}'.format(f))

    # print(f.split('.'))
    ############################################################################
    ############################################################################
    ############################################################################



if __name__ == '__main__':
    main()
