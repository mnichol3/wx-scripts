import os
import re
import glob
import subprocess
from datetime import datetime, timedelta
import logging
import concurrent.futures

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
    end = datetime.strptime(end, '%m-%d-%Y-%H:%M')
    prev = start

    while (prev <= end):
        # Increment 6 hours
        curr = prev + timedelta(seconds=21600)

        chunks.append((prev, curr))
        prev = curr

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
        chunks = chunks[:-1]
        prev = prev - timedelta(seconds=21600)
        # chunks.append((prev.strftime('%m-%d-%Y-%H:%M'), end.strftime('%m-%d-%Y-%H:%M')))
        chunks.append((prev, end))

    return chunks



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
                        or
                YYYY-MM-DD HH:MM
    """
    fnames = []
    scantime_re = re.compile(r'_s(\d{11})')

    try:
        date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M')
    except:
        date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')

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
    return fnames



def grid_flash_chunk(start_date, end_date):
    local_glm_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/aws'
    outpath = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded'
    make_grid_path = '/home/mnichol3/Coding/glmtools/glmtools/examples/grid/make_GLM_grids.py'

    curr_dt = start_date
    next_dt = start_date + timedelta(seconds=60)

    while (curr_dt <= end_date):
        curr_dt_str = curr_dt.strftime('%Y-%m-%d %H:%M:%S')
        print('\nProcessing: {} to {}'.format(curr_dt_str[:-3], next_dt.strftime('%Y-%m-%d %H:%M')))

        subdir_path = os.path.join(local_glm_path, curr_dt.strftime('%j/%H'))

        # Get list of absolute paths of GLM files for the current date & time
        curr_fnames = get_files_for_date_time(local_glm_path, curr_dt_str)

        cmd = "python {0} -o {1}"
        cmd += " --fixed_grid --split_events --goes_position=east --goes_sector=conus"
        cmd += " --dx=2.0 --dy=2.0"
        cmd += " --start={3} --end={4} {2}"

        cmd = cmd.format(make_grid_path, outpath, ' '.join(curr_fnames),
                        curr_dt.isoformat(), next_dt.isoformat())

        out_bytes = subprocess.check_output(cmd.split())

        grid_dir_base = outpath
        nc_files = glob.glob(os.path.join(grid_dir_base, curr_dt.strftime('%j/%H'),'*.nc'))
        # for f in nc_files:
        #     print(f)

        curr_dt = next_dt
        next_dt = next_dt + timedelta(seconds=60)



def main():
    log_format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")

    num_threads = 3

    start_date = datetime(2019, 8, 24, 12, 0)  # 24 Aug 2019 12:00z
    end_date = datetime(2019, 8, 25, 12, 0)
    # end_date = datetime(2019, 9, 9, 0, 0)      # 09 Sep 2019 00:00z

    time_chunks = calc_date_chunks(start_date.strftime('%m-%d-%Y-%H:%M'), end_date.strftime('%m-%d-%Y-%H:%M'))
    # for chunk in time_chunks:
    #     # grid_flash_chunk(chunk[0], chunk[1])
    #     print(chunk)


    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_thread = {executor.submit(grid_flash_chunk, chunk[0], chunk[1]):
                                         chunk for chunk in time_chunks}

        for future in concurrent.futures.as_completed(future_thread):
            result = future.result()
            print("Finished processing!")

main()
