import os
import re
import glob
import subprocess
from datetime import datetime, timedelta
import logging
import concurrent.futures
import pandas as pd

import glmtools
from glmtools.io.glm import GLMDataset

import warnings



def calc_date_chunks(start, end):
    """
    Creates 6-hr time chunks

    Parameters
    ----------
    start : str
        Format: 'MM-DD-YYYY-HH:MM'
    end : str
        Format: 'MM-DD-YYYY-HH:MM'

    Returns
    --------
    chunks : list of tuples of (str, str)
        stf format: 'MM-DD-YYYY-HH:MM'

    Dependencies
    -------------
    > datetime
    """
    chunks = []

    start = datetime.strptime(start, '%m-%d-%Y-%H:%M')
    end = datetime.strptime(end, '%m-%d-%Y-%H:%M') #- timedelta(seconds=3600)
    prev = start

    while (prev < end):
        # Increment 6 hours
        curr = prev + timedelta(seconds=21600)

        chunks.append((prev, curr))
        prev = curr + timedelta(seconds=3600)

    """
    Adjust the last tuple incase the time period doesnt divide evenly into
    6-hr periods

    Ex
    ---
    Unadjusted:
        in:  calc_date_chunks('09-01-2019-15:00', '09-06-2019-13:00')[-1]
        out: ('09-06-2019-09:00', '09-06-2019-15:00')

    Adjusted:
        in:  calc_date_chunks('09-01-2019-15:00', '09-06-2019-13:00')[-1]
        out: ('09-06-2019-09:00', '09-06-2019-13:00')

    """
    if (chunks[-1][1] > end):
        bad_chunk = chunks[-1]  # Get the bad chunk since we want its start time
        chunks = chunks[:-1]    # Remove last chunk (the bad one)
        chunks.append((bad_chunk[0], end))

    return chunks



def get_files_for_date_time(base_path, f_time):
    """
    Get the GLM files for a given date & time

    Parameters
    ----------
    base_path : str
        Path to the local parent GLM file directory
    date_time : str
        Date and time of the desired GLM files.
        Format: YYYY-MM-DD HH:MM:SS
                        or
                YYYY-MM-DD HH:MM
    """
    fnames = []
    scantime_re = re.compile(r'_s(\d{11})')

    try:
        date_time = datetime.strptime(f_time, '%Y-%m-%d %H:%M')
    except:
        date_time = datetime.strptime(f_time, '%Y-%m-%d %H:%M:%S')

    # Parse the subdirectory path for the desired date & time of the GLM file
    subdir_path = os.path.join(base_path, str(date_time.timetuple().tm_yday), str(date_time.hour).zfill(2))

    file_count = 0
    for f in os.listdir(subdir_path):

        # Iterate through the files in the date & hour subdirectory tree and
        # attempt to match the starting scan date & time in the file name
        match = re.search(scantime_re, f)
        if (match):

            # If the scan date & time in the file name is matched, create
            # a datetime object from it to compare to our desired datetime obj
            f_scantime = datetime.strptime(match.group(1), '%Y%j%H%M')
            if ((f_scantime == date_time) and os.path.isfile(os.path.join(subdir_path, f))):
                fnames.append(os.path.join(subdir_path, f))

                # Since we're looking for the GLM files for a given hour & minute,
                # and GLM publishes at most 3 files a minute, once we find our 3
                # files we can break the loop and save some execution time
                file_count += 1
                if (file_count >= 3):
                    break
    print('Number of files found for {}: {}'.format(f_time, len(fnames)))
    return fnames



def grid_flash_chunk(start_date, end_date, track_df):
    local_glm_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/aws'
    outpath = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded'
    make_grid_path = '/home/mnichol3/Coding/glmtools/glmtools/examples/grid/make_GLM_grids.py'

    curr_dt = start_date
    next_dt = start_date + timedelta(seconds=60)


    # Step through the datetime chunk at 1-min intervals to conserve memory
    while (curr_dt <= end_date):
        curr_dt_str = curr_dt.strftime('%Y-%m-%d %H:%M:%S')
        print('\nProcessing: {} to {}'.format(curr_dt_str[:-3], next_dt.strftime('%Y-%m-%d %H:%M')))

        curr_dt_zerod = curr_dt.replace(minute=0, second=0)

        lat = track_df['lat'].loc[track_df.index == curr_dt_zerod].iloc[0]
        lon = track_df['lon'].loc[track_df.index == curr_dt_zerod].iloc[0]
        print(lat, lon)

        subdir_path = os.path.join(local_glm_path, curr_dt.strftime('%j/%H'))

        # Get list of absolute paths of GLM files for the current date & time
        curr_fnames = get_files_for_date_time(local_glm_path, curr_dt_str)
        print('Ingesting:')
        for f in curr_fnames:
            print('     {}'.format(f.split('/', 11)[-1]))
        print('\n')

        # cmd = "python {0} -o {1}"
        # cmd += " --fixed_grid --split_events --goes_position=east --goes_sector=conus"
        # cmd += " --dx=2.0 --dy=2.0"
        # cmd += " --start={3} --end={4} {2}"
        #
        # cmd = cmd.format(make_grid_path, outpath, ' '.join(curr_fnames),
        #                 curr_dt.isoformat(), next_dt.isoformat())

        # Create the command using meso sector and the current hour's interpolated
        # best track lat & lon as the center
        cmd = "python {0} -o {1}"
        cmd += " --fixed_grid --split_events --goes_position=east " #--goes_sector=meso"
        cmd += ' --dx=2.0 --dy=2.0 --ctr_lat={5} --ctr_lon={6} --width={7} --height={8}'
        cmd += " --start={3} --end={4} {2}"

        cmd = cmd.format(make_grid_path, outpath, ' '.join(curr_fnames),
                         curr_dt.isoformat(), next_dt.isoformat(), lat, lon,
                         2500.0, 2500.0)
        try:
            out_bytes = subprocess.check_output(cmd.split())
        except:
            curr_dt = next_dt
            next_dt = next_dt + timedelta(seconds=60)
        else:

            grid_dir_base = outpath
            nc_files = glob.glob(os.path.join(grid_dir_base, curr_dt.strftime('%j/%H'),'*.nc'))
            # for f in nc_files:
            #     print(f)

            curr_dt = next_dt
            next_dt = next_dt + timedelta(seconds=60)



def track_csv_to_df(abs_path):
    """
    Read a best track csv into a Pandas DataFrame

    Parameters
    ----------
    abs_path : str
        Absolute path, including the filename, of the csv/txt file to read

    Returns
    -------
    df : Pandas DataFrame
        DataFrame containing the best track data
        Column names: ['date-time', 'name', 'storm_num', 'basin', 'lat',
                       'lon', 'mslp', 'storm_type', 'wind', 'ss']

        or

        col_names = ['date-time', 'storm_num', 'lat', 'lon', 'mslp', 'wind', 'ss']
        if reading an interpolated data file

    Notes
    -----
    * Taken from nhc_gis_track.py
    """
    from os.path import isfile

    if (isfile(abs_path)):
        df = pd.read_csv(abs_path, sep=',', header=0, index_col='date-time')
        return df
    else:
        raise FileNotFoundError('File not found: {}'.format(abs_path))




def main():
    import sys

    track_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/initial_best_track_interp_60min.txt'

    # Delete previos log file, if present
    if os.path.isfile('make_GLM_grid.log'):
        os.remove('make_GLM_grid.log')

    # log_format = "%(asctime)s: %(message)s"
    # logging.basicConfig(format=log_format, level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")

    num_threads = 3

    # start_date = datetime(2019, 8, 24, 12, 0)  # 24 Aug 2019 12:00z
    start_date = datetime(2019, 8, 27, 12, 0)  # 24 Aug 2019 12:00z
    end_date = datetime(2019, 9, 9, 0, 0)
    # end_date = datetime(2019, 9, 9, 0, 0)      # 09 Sep 2019 00:00z

    # Read 60-min interpolated track dataframe and change its index from str
    # to datetime objects
    track_df = track_csv_to_df(track_path)
    track_dts = [datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in list(track_df.index)]
    track_df = track_df.reindex(track_dts)

    time_chunks = calc_date_chunks(start_date.strftime('%m-%d-%Y-%H:%M'), end_date.strftime('%m-%d-%Y-%H:%M'))
    # for chunk in time_chunks:
    #     print(chunk)

    track_chunks = []
    for chunk in time_chunks:
        curr_coords = track_df.loc[(track_df.index >= chunk[0]) & (track_df.index <= chunk[1])]
        track_chunks.append(curr_coords)

    # for idx, chunk in enumerate(time_chunks):
    #     try:
    #         grid_flash_chunk(chunk[0], chunk[1], track_chunks[idx])
    #     except:
    #         pass

    #### Using best track coordinates
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_thread = {executor.submit(grid_flash_chunk, chunk[0], chunk[1], track_chunks[idx]):
                                         chunk for idx, chunk in enumerate(time_chunks)}

        for future in concurrent.futures.as_completed(future_thread):
            result = future.result()
            print("Finished processing!")


    #### Without best track coordinates
    # with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    #     future_thread = {executor.submit(grid_flash_chunk, chunk[0], chunk[1]):
    #                                      chunk for chunk in time_chunks}

        # for future in concurrent.futures.as_completed(future_thread):
        #     result = future.result()
        #     print("Finished processing!")

main()
