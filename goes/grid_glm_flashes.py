import numpy as np
import os
import glob
import subprocess
from datetime import datetime, timedelta
from sys import exit

import glmtools
from glmtools.io.glm import GLMDataset


def grid_glm_date():
    base_f_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/aws/245/03'
    outpath = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded'
    make_grid_path = '/home/mnichol3/Coding/glmtools/glmtools/examples/grid/make_GLM_grids.py'


    fnames = [
        'OR_GLM-L2-LCFA_G16_s20192450332000_e20192450332200_c20192450332226.nc',
        'OR_GLM-L2-LCFA_G16_s20192450332200_e20192450332400_c20192450332428.nc',
        'OR_GLM-L2-LCFA_G16_s20192450332400_e20192450333000_c20192450333024.nc'
    ]

    fnames = [os.path.join(base_f_path, f) for f in fnames]

    # Set the start time and duration
    startdate = datetime(2019, 9, 2, 3, 32)
    # print(startdate.strftime('%Y-%j-%H:%M'))
    duration = timedelta(0, 60*5)
    enddate = startdate+duration

    cmd = "python {0} -o {1}"
    cmd += " --fixed_grid --split_events --goes_position=east --goes_sector=conus"
    cmd += " --dx=2.0 --dy=2.0"
    cmd += " --start={3} --end={4} {2}"

    cmd = cmd.format(make_grid_path, outpath, ' '.join(fnames),
                    startdate.isoformat(), enddate.isoformat())

    # for arg in cmd.split():
    #     print(arg)
    # exit(0)

    out_bytes = subprocess.check_output(cmd.split())

    grid_dir_base = outpath
    nc_files = glob.glob(os.path.join(grid_dir_base, startdate.strftime('%j/%H'),'*.nc'))
    for f in nc_files:
        print(f)



def check_data():
    base_f_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/aws/245/03'

    fnames = [
        'OR_GLM-L2-LCFA_G16_s20192450332000_e20192450332200_c20192450332226.nc',
        'OR_GLM-L2-LCFA_G16_s20192450332200_e20192450332400_c20192450332428.nc',
        'OR_GLM-L2-LCFA_G16_s20192450332400_e20192450333000_c20192450333024.nc'
    ]

    fnames = [os.path.join(base_f_path, f) for f in fnames]

    for f in fnames:
        glm = GLMDataset(f)
        print(glm.dataset)
        print('----------------------------------------------------------------')
        print('----------------------------------------------------------------')
        print('----------------------------------------------------------------')


# check_data()
grid_glm_date()
