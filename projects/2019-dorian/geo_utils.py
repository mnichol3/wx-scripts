import numpy as np
from os.path import join
from pyproj import Proj

############ Imports for geodesic point buffer funcs #########
import pyproj
from shapely.ops import transform, polygonize
from shapely.geometry import Point, LineString
from functools import partial
##############################################################

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

    Returns
    -------
    idx_dict : dict of floats
        Dictionary containing the values and their indexes that are closest to
        the 'x' & 'y' arguments
        Keys: ['y_idx', 'y_val', 'x_idx', 'x_val']
    """
    pt_y, pt_x = geod_to_scan(y, x)

    x_idx = (np.abs(fed_obj.x - pt_x)).argmin()
    nrst_x = fed_obj.x[x_idx]

    y_idx = (np.abs(fed_obj.y - pt_y)).argmin()
    nrst_y = fed_obj.y[y_idx]

    # print('Nearest x to {0:.6f} is {1:.6f}'.format(pt_x, nrst_x))
    # print('Nearest y to {0:.6f} is {1:.6f}'.format(pt_y, nrst_y))

    idx_dict = {
                    'y_idx' : y_idx,
                    'y_val' : nrst_y,
                    'x_idx' : x_idx,
                    'x_val' : nrst_x
                }

    return idx_dict



def get_grid_subset(min_y, max_y, min_x, max_x, fed_obj):
    """
    Get a geographic subset of the ABI Fixed Grid defined by [min_y, max_y, min_x, max_x].

    Getting the geographic subset must take place using scanning angle radians
    (as opposed to georeferencing the scanning angle radians and using geodetic
    lat & lon to take the subset) as the geometry of the grid being overlayed
    on the GRS-80 ellipsoid makes subsetting much more difficult

    Parameters
    -----------
    min_y : float
        Smallest latitude (y) point that defines the geographic subset, in
        decimal degrees
    max_y : float
        Largest latitude (y) point that defines the geographic subset, in
        decimal degrees
    min_x : float
        Smallest longitude (x) point that defines the geographic subset, in
        decimal degrees
    max_x : float
        Largest longitude (x) point that defines the geographic subset, in
        decimal degrees
    fed_obj : GLMFEDFile object
        GLMFEDFile object containing the data to subset

    Returns
    -------
    dict of floats

    """
    # Get the indexes of the smallest lat & lon points in the ABI Fixed Grid
    # x  y coordinate arrays
    min_dict = get_nrst_grid(min_y, min_x, fed_obj)

    min_y_idx = min_dict['y_idx']
    min_x_idx = min_dict['x_idx']

    del min_dict

    # Get the indexes of the largest lat & lon points in the ABI Fixed Grid
    # x & y coordinate arrays
    max_dict = get_nrst_grid(max_y, max_x, fed_obj)

    max_y_idx = max_dict['y_idx']
    max_x_idx = max_dict['x_idx']

    del max_dict

    fed_obj.update_x(fed_obj.x[min_x_idx : max_x_idx])
    fed_obj.update_y(fed_obj.y[max_y_idx : min_y_idx]) # Grid Y values decrease from right to left

    # 2dArray[y1 : y2, x1 : x2]
    fed_obj.update_fed(fed_obj.flash_extent_density[max_y_idx: min_y_idx, min_x_idx : max_x_idx])




def georeference(fed_obj):
    """
    Transform GLMFEDFILE coordinates from scanning angle (radians) to geodetic
    lat & lon (deciman degrees)
    """
    sat_h     = fed_obj.goes_imager_projection['perspective_point_height']
    sat_lon   = fed_obj.goes_imager_projection['longitude_of_projection_origin']
    sat_sweep = fed_obj.goes_imager_projection['sweep_angle_axis']

    # Projection x & y coordinates equal the scanning angle (in radians) multiplied
    # by the satellite height
    # https://proj.org/operations/projections/geos.html
    x_trans = fed_obj.x * sat_h
    y_trans = fed_obj.y * sat_h

    # Create a Proj geostationary projection object
    p = Proj(proj='geos', h=sat_h, lon_0=sat_lon, sweep=sat_sweep)

    # Convert projection coordinates to geodetic lat & lon
    x_trans, y_trans = np.meshgrid(x_trans, y_trans)
    lons, lats = p(x_trans, y_trans, inverse=True)

    # Assign pixels showing space to a single point in the Gulf of Alaska
    lats[np.isnan(fed_obj.flash_extent_density)] = 57
    lons[np.isnan(fed_obj.flash_extent_density)] = -152

    # print(lons)
    # print(lats)
    # print(lons.shape)
    # print(lats.shape)
    fed_obj.x = lons
    fed_obj.y = lats
    fed_obj.coord_type = 'geod'

    return fed_obj



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
    coords : tuple of (lat, lon), optional
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



def get_quadrants(range_buffer, nsew_pts):
    """
    Split a geodesic point buffer into 4 quadrants and return them as
    a dictionary of polygons
    """
    quad_dict = {}
    quarters = []

    # Create lines to bisect the circular point buffer with
    horiz_bisect_line = LineString([Point(nsew_pts['w'][1] - 1, nsew_pts['w'][0]),
                                    Point(nsew_pts['e'][1] + 1, nsew_pts['e'][0])])

    verti_bisect_line = LineString([Point(nsew_pts['s'][1], nsew_pts['s'][0] - 1),
                                    Point(nsew_pts['n'][1], nsew_pts['n'][0] + 1)])

    # Bisect the cilcular polygon, yielding two halves
    halves = horiz_bisect_line.union(LineString(list(range_buffer.coords)))
    halves = polygonize(halves)

    # Bisect each of the halves created above, creating 4 quadrants
    for half in halves:
        quarter = verti_bisect_line.union(LineString(list(half.exterior.coords)))
        quarter = polygonize(quarter)
        quarters.append(quarter)

    quadrants = []
    for geom in quarters:
        for g in geom:
            quadrants.append(g)

    sort_1 = sorted(quadrants, key = lambda q: q.centroid.x)
    west_pts = sort_1[:2]
    east_pts = sort_1[2:]

    sort_west = sorted(west_pts, key = lambda p: p.centroid.y)
    sort_east = sorted(east_pts, key = lambda p: p.centroid.y)

    quad_dict['sw'] = sort_west[0]
    quad_dict['nw'] = sort_west[1]

    quad_dict['se'] = sort_east[0]
    quad_dict['ne'] = sort_east[1]

    return quad_dict



def main():
    f_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded/nc/20190826'
    f_name = 'IXTR98_KNES_262011_122283.2019082620.nc'
    f_abs = join(f_path, f_name)
    obj = glmfedfile.read_file([f_abs])[0]

    # Interpolated Best Track center fix for 12z 01 Sep
    btcf = (26.5, -76.5)

    # Construct 400km buffer around the Best Track center fix
    # buffer_ring  = geodesic_point_buffer(btcf[0], btcf[1], 400)
    # extrema_dict = get_quadrant_coords(buffer_ring)
    # storm_quads  = get_quadrants(buffer_ring, extrema_dict)


    ######################## Test grid subsetting funcs ########################
    # btcf1 = (26.5, -77.5)
    # btcf2 = (27.5, -76.5)
    # get_grid_subset(btcf1[0], btcf2[0], btcf1[1], btcf2[1], obj)
    # georeference(obj)
    # print(obj.flash_extent_density.shape)
    # print(obj.x)
    # print(obj.y)
    ############################################################################




if __name__ == '__main__':
    main()
