from os.path import join, isdir, isfile
from os import walk, listdir
import pandas as pd

from utils import read_file_glm


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



def proccess_flashes(base_path):
    """
    TODO: Mon 23 Sept

    * Get the 3 GLM files pertaining to each minute
        * Possible implementations
            1) for 0 to num_files-3:
                    read file[i]
                    read file[i+1]
                    read file[i+2]
                    i += 3

            2) preprocess filenames into dict
                {'00': [fname_0000, fname_0020, fname_0040],
                 '01': [fname_0100, fname_0120, fname_0140],
                  ...
                 }
    """
    return -1


# base_path = '/media/mnichol3/tsb1/data/storms/2019-dorian/glm/aws'
base_path = '/media/mnichol3/tsb1/data/storms/2019-dorian/abi/inf'

out_base = '/media/mnichol3/tsb1/data/storms/2019-dorian/glm/accum'

pp_dirs(base_path)
