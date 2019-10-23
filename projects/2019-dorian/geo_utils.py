import numpy as np
from os.path import join

import glmfedfile
from proj_utils import geod_to_scan, scan_to_geod



def get_nrst_grid(y, x, fed_obj):
    """
    Get the GOES-16 Fixed Grid cell nearest to the point represented by (x, y)

    Parameters
    -----------
    x : float
        Longitude in decimal degrees
    y : float
        Latitude in decimal degrees
    fed_obj : GLMFEDFile object
    """
    pt_y, pt_x = geod_to_scan(y, x)

    x_idx = (np.abs(fed_obj.x - pt_x)).argmin()
    nrst_x = fed_obj.x[x_idx]

    y_idx = (np.abs(fed_obj.y - pt_y)).argmin()
    nrst_y = fed_obj.y[y_idx]

    print('Nearest x to {0:.6f} is {1:.6f}'.format(pt_x, nrst_x))
    print('Nearest y to {0:.6f} is {1:.6f}'.format(pt_y, nrst_y))

    print(scan_to_geod(nrst_y, nrst_x))



def main():
    f_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded/nc/20190826'
    f_name = 'IXTR98_KNES_262011_122283.2019082620.nc'
    f_abs = join(f_path, f_name)
    obj = glmfedfile.read_file([f_abs])[0]

    geo_lat = 38.989540
    geo_lon = -76.945641

    get_nrst_grid(geo_lat, geo_lon, obj)



if __name__ == '__main__':
    main()
