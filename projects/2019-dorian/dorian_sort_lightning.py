from os.path import join, isdir, isfile
from os import walk, listdir
import pandas as pd

############ Imports for geodesic point buffer funcs #########
import pyproj
from shapely.ops import transform
from shapely.geometry import Point, LineString
from functools import partial
##############################################################

# from utils import read_file_glm


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



def proccess_flashes(fnames, center_coords, radius):
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



def geodesic_point_buffer(lat, lon, km):
    """
    Creates a circle on on the earth's surface, centered at (lat, lon) with
    radius of km

    Parameters
    ------------
    lat : float
        Latitude coordinate of the circle's center in decimal degrees
    lon : float
        Longitude coordinate of the circle's center in decimal degrees
    km : int
        Radius of the circle, in km


    Returns
    ------------
    ring : LinearRing object
        LinearRing object containing the coordinates of the circle's edge.

        To access the coordinates:
            lats = [float(x[1]) for x in ring.coords[:]]
            lons = [float(x[0]) for x in ring.coords[:]]

            for idx, lat in enumerate(lats):
                print('lat: {0:.3f}, lon: {1:.3f}'.format(lat, lons[idx]))


    Dependencies
    -------------
    > pyproj
    > functools.partial
    > shapely.geometry.Point
    > shapely.ops.transform
    """

    proj_wgs84 = pyproj.Proj(init='epsg:4326')

    # Azimuthal equidistant projection
    aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
    project = partial(
        pyproj.transform,
        pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
        proj_wgs84)
    buf = Point(0, 0).buffer(km * 1000)  # distance in metres

    ring = transform(project, buf).exterior

    return ring



def get_quadrant_coords(buff_obj=None, coords=None, pprint=False):
    """
    Finds the max lon, max lat, min lon, & min lat coords in order to divide a
    geodesic_point_buffer into NE, NW, SE, & SW quadrants. Though both arguments
    are optional, one must be given

    Parameters
    ----------
    buff_obj : LinearRing object, optional
        LinearRing object returned by geodesic_point_buffer()
    coords : tuple of (lats, lons), optional
        Tuple of coordinates representing a geodesic point buffer
    pprint : Bool, optional
        If True, the dictionary & keys will be printed. Default: False

    Returns
    -------
    coord_dict : Dictionary of {str: (float, float)}
        Dictionary containing the coordinates of the northern-, southern- eastern-,
        and western-most coordinates.
        Keys: ['n', 'e', 's', 'w']
    """
    if (buff_obj):
        # Extract the coordinates from the LinearRing object
        lats = [float(x[1]) for x in buff_obj.coords[:]]
        lons = [float(x[0]) for x in buff_obj.coords[:]]
    elif (coord_list):
        # Extract the coordinate lists from the coords tuple
        lats = coords[0]
        lons = coords[1]
    else:
        raise ValueError("Both 'buff_obj' and 'coords' arguments cannot be None")

    coord_dict = {}

    n_idx = lats.index(max(lats))
    s_idx = lats.index(min(lats))

    e_idx = lons.index(max(lons))
    w_idx = lons.index(min(lons))

    coord_dict['n'] = (lats[n_idx], lons[n_idx])
    coord_dict['s'] = (lats[s_idx], lons[s_idx])
    coord_dict['e'] = (lats[e_idx], lons[e_idx])
    coord_dict['w'] = (lats[w_idx], lons[w_idx])

    if (pprint):
        for key, val in coord_dict.items():
            print('{}: {:.3f}, {:.3f}'.format(key, val[0], val[1]))

    return coord_dict
