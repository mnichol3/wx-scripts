"""
https://github.com/deeplycloudy/glmtools/blob/master/examples/plot_glm_test_data.ipynb
"""
from datetime import datetime, timedelta
from os.path import join
import subprocess
from sys import exit

import glmtools
from glmtools.io.glm import GLMDataset


make_grid_path = '/home/mnichol3/Coding/glmtools/glmtools/examples/grid/make_GLM_grids.py'
local_glm_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/aws/244/16'
outpath = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded'

f_names = ['OR_GLM-L2-LCFA_G16_s20192441640000_e20192441640200_c20192441640217.nc',
           'OR_GLM-L2-LCFA_G16_s20192441640200_e20192441640400_c20192441640427.nc',
           'OR_GLM-L2-LCFA_G16_s20192441640400_e20192441641000_c20192441641029.nc']

f_paths = [join(local_glm_path, f) for f in f_names]

date_start = datetime(2019, 9, 1, 16, 40)
duration = timedelta(0, 60*5)
date_end = date_start + duration

cmd = "python {0} -o {1}"
cmd += " --fixed_grid --split_events --goes_position=east --goes_sector=conus"
cmd += " --dx=2.0 --dy=2.0"
cmd += " --start={3} --end={4} {2}"

cmd = cmd.format(make_grid_path, outpath, ' '.join(f_paths),
                date_start.isoformat(), date_end.isoformat())

print(cmd.split())
exit(0)
# out_bytes = subprocess.check_output(cmd.split())

proc = subprocess.Popen(cmd.split())
try:
    outs, errs = proc.communicate()
except subprocess.TimeoutExpired:
    proc.kill()
    outs, errs = proc.communicate()


# print(out_bytes)
