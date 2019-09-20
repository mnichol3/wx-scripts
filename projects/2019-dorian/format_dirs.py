"""
Author: Matt Nicholson

Creates a file tree for ABI & GLM data and moves the data files into their
respective date & hour subdirectories
"""
import os
import re
import sys
import shutil


def create_subdirs():
    # base_path = '/media/mnichol3/tsb1/data/storms/2019-dorian'
    base_path = base_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian'

    sensors = ['abi/inf', 'glm/aws']

    j_days = ['244', '245', '246', '247', '248', '249']

    hours = [str(x).zfill(2) for x in range(0, 24)]

    for sensor in sensors:
        curr_dir = os.path.join(base_path, sensor)

        for day in j_days:
            curr_dir_day = os.path.join(curr_dir, day)
            try:
                os.mkdir(curr_dir_day)
            except:
                pass
            print(curr_dir_day)

            for hour in hours:
                curr_dir_hr = os.path.join(curr_dir_day, hour)
                try:
                    os.mkdir(curr_dir_hr)
                except:
                    pass
                print(curr_dir_hr)
    print('Done!')



def sort_files():
    scantime_re = re.compile(r'G\d{2}_s(\d{4})(\d{3})(\d{2})')

    # base_path = '/media/mnichol3/tsb1/data/storms/2019-dorian'
    base_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian'

    sensors = ['abi/inf', 'glm/aws']

    for sensor in sensors:
        curr_dir = os.path.join(base_path, sensor)

        for f in os.listdir(curr_dir):
            if (os.path.isfile(os.path.join(curr_dir, f))):
                match = scantime_re.search(f)
                if (match is not None):
                    day = match.group(2)
                    hour = match.group(3)

                    curr_path = os.path.join(curr_dir, f)
                    new_path = os.path.join(curr_dir, day, hour, f)
                    # print(curr_path)
                    # print(new_path)
                    # sys.exit(0)
                    shutil.move(curr_path, new_path)

create_subdirs()
sort_files()
