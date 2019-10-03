"""
https://github.com/deeplycloudy/lmatools/blob/master/lmatools/grid/fixed.py
"""
import numpy as np

from coord_sys import GeostationaryFixedGridSystem, GeographicSystem



class EventQuad(object):
    def __init__(self, id, corners, count):
        self.corners = corners
        self.id = str(id).zfill(6)
        self.count = count


    def inc_count(self):
        self.count += 1


    def dec_count(self):
        self.count -= 1


    def __repr__(self):
        return '<EventQuad object - {} - {}>'.format(self.id, self.count)







goesr_nadir_lon = {
    'east':-75.0,
    'west':-137.0,
    'test':-89.5,
}


goesr_full = {
    # all values in radians on the fixed grid
    # The spans here match the values in L1b PUG table 5.1.2.7-4 but
    # when combined with the 10 km resolution give two (2) fewer
    # pixels than claimed in table 5.1.2.6
    'span_EW': 0.151872*2.0,
    'span_NS': 0.151872*2.0,
    'center_EW': 0.0,
    'center_NS': 0.0,
}


goesr_conus = {
    # all values in radians on the fixed grid
    'span_EW': 0.14,
    'span_NS': 0.084,
}


goesr_meso = {
    'span_EW': 0.028,
    'span_NS': 0.028,
}


goeseast_full = goesr_full.copy()
goeseast_full['y_img_bounds'] = {
    'n': 0.151872,
    's': -0.151872
}

goeseast_full['x_img_bounds'] = {
    'w': -0.151872,
    'e': 0.151872
}


goeswest_full = goesr_full.copy()
goestest_full = goesr_full.copy()

goeseast_meso = goesr_meso.copy()
goeswest_meso = goesr_meso.copy()
goestest_meso = goesr_meso.copy()

goeseast_conus = goesr_conus.copy()
goeseast_conus.update({
    'center_EW': -0.031360,
    'center_NS': 0.086240,
})

goeseast_conus['y_img_bounds'] = {
    'n': 0.128240,
    's': 0.044240
}

goeseast_conus['x_img_bounds'] = {
    'w': -0.101360,
    'e': 0.038640
}


goeswest_conus = goesr_conus.copy()
goeswest_conus.update({
    'center_EW': 0.000000,
    'center_NS': 0.086240,
})


goestest_conus = goesr_conus.copy()
goestest_conus.update({
    'center_EW': -0.005040,
    'center_NS': 0.084560,
})


# Resolutions in km
goesr_resolutions = {
    '0.5':   14e-6,
    '1.0':   28e-6,
    '2.0':   56e-6,
    '4.0':   112e-6,
    '8.0':   224e-6, # not technically in the spec, but SYMMETRY.
    '10.0':  280e-6,
    '100.0': 2800e-6,
}


def get_GOESR_coordsys(sat_lon_nadir = -75.0):
    """
    Values from the GOES-R PUG Volume 3, L1b data

    Returns geofixcs, grs80lla: the fixed grid coordinate system and the
    latitude, longitude, altitude coordinate system referenced to the GRS80
    ellipsoid used by GOES-R as its earth reference.
    """
    goes_sweep = 'x' # Meteosat is 'y'
    ellipse = 'GRS80'
    datum = 'WGS84'
    sat_ecef_height=35786023.0
    geofixcs = GeostationaryFixedGridSystem(subsat_lon=sat_lon_nadir,
                   ellipse=ellipse, datum=datum, sweep_axis=goes_sweep,
                   sat_ecef_height=sat_ecef_height)
    grs80lla = GeographicSystem(ellipse='GRS80', datum='WGS84')
    return geofixcs, grs80lla



def get_GOESR_grid(position='east', view='full', resolution='2.0'):
    """
    This helper function returns specifications of the GOES-R fixed grids.

    position is ['east'|'west'|'test']
    resolution is ['0.5'|'1.0'|'2.0'|'4.0'|'10.0']
    view is ['full'|'conus'|'meso']

    returns a dictionary with the keys 'resolution', 'span_EW', 'span_NS',
        'pixels_EW', 'pixels_NS', 'nadir_lon', and (for all non-meso sectors)
        'center_EW', 'center_NS'.
        values are radians, except for the integer
    """
    assert position in ['east', 'west', 'test']
    assert view in ['full', 'conus', 'meso']
    assert resolution in goesr_resolutions.keys()

    view = globals()['goes'+position+"_"+view].copy()
    view['resolution'] = goesr_resolutions[resolution]
    view['pixels_EW'] = int(view['span_EW']/view['resolution'])
    view['pixels_NS'] = int(view['span_NS']/view['resolution'])
    view['nadir_lon'] = goesr_nadir_lon[position]

    return view



def load_pixel_corner_lookup():
    """
    Read GLM event polygon lats, lons, and corner offsets from a corner point
    lookup table.
    Return as a tuple of (lons, lats, corners). Units = radians
    """
    import pickle

    fname = 'G16_corner_lut_fixedgrid.pickle'

    with open(fname, 'rb') as f:
        obj = pickle.load(f)

    lons = obj[0] * 1.0e-6
    lats = obj[1] * 1.0e-6
    corners = obj[2] * 1.0e-6

    return (lons, lats, corners)



def quads_from_corner_lookup(g_lons, g_lats, corner_pts, p_lon, p_lat,
                             nadir_lon=0.0, inflate=1.0, extrapolate=True):
    """

    """
    from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator

    n_corners, n_coords = corner_pts.shape[-2:]

    lon_shift = g_lons + nadir_lon

    pixel_loc = np.vstack((p_lon, p_lat)).T
    grid_loc = (lon_shift.flatten(), g_lats.flatten())

    quads = np.empty((p_lon.shape[0], n_corners, n_coords))

    for ci in range(n_corners):
        corner_interp_lon = LinearNDInterpolator(grid_loc,
                                corner_pts[:,:,ci,0].flatten())
                                #, bounds_error=True)
        corner_interp_lat = LinearNDInterpolator(grid_loc,
                                corner_pts[:,:,ci,1].flatten())
                                #, bounds_error=True)
        dlon = corner_interp_lon(pixel_loc)
        dlat = corner_interp_lat(pixel_loc)

        if extrapolate:
            out_lon = np.isnan(dlon)
            out_lat = np.isnan(dlat)

            if out_lon.sum() > 0:
                did_extrap = True
                corner_extrap_lon = NearestNDInterpolator(grid_loc,
                                    corner_pts[:,:,ci,0].flatten())

                dlon[out_lon] = corner_extrap_lon(pixel_loc[out_lon])

            if out_lat.sum() > 0:
                did_extrap = True
                corner_extrap_lat = NearestNDInterpolator(grid_loc,
                                    corner_pts[:,:,ci,1].flatten())

                dlat[out_lat] = corner_extrap_lat(pixel_loc[out_lat])

        quads[:, ci, 0] = p_lon + dlon*inflate
        quads[:, ci, 1] = p_lat + dlat*inflate

    return quads



def count(listOfCorners):
    """
    EventQuad object has corners stored as string. To convert back to
    (4, 2) numpy array:
             np.fromstring(i, dtype=float).reshape((4, 2))
    """
    import collections

    id_num = 1
    unique_quads = []

    listOfCorners = [x.tostring() for x in listOfCorners]

    flag = False
    val = collections.Counter(listOfCorners)
    uniqueList = list(set(listOfCorners))

    for i in uniqueList:
        # if val[i]>= 2:
        #     flag = True
            # print(i, "-", val[i])
        curr_obj = EventQuad(id_num, i, val[i])
        unique_quads.append(curr_obj)
        id_num += 1

    return unique_quads


if __name__ == '__main__':
    from os.path import join
    from utils import read_file_glm
    from sys import exit

    glm_path = '/media/mnichol3/pmeyers1/MattNicholson/glm/test/2019/244/16'
    glm_fname = 'OR_GLM-L2-LCFA_G16_s20192441601000_e20192441601200_c20192441601226.nc'
    # glm_fname = 'OR_GLM-L2-LCFA_G16_s20192441600200_e20192441600400_c20192441600416.nc'

    glm_file = read_file_glm(join(glm_path, glm_fname), product='e')

    events_x = glm_file.data['x']
    events_y = glm_file.data['y']

    x_lut, y_lut, corner_lut = load_pixel_corner_lookup()

    quads = quads_from_corner_lookup(x_lut, y_lut, corner_lut, events_x, events_y)

    # print(quads.shape)
    quads = count(quads)

    for q in quads:
        print(q)

    # print(len(quads))

    # print(quads[-1].corners)
    # print(np.fromstring(quads[-1].corners, dtype=float).reshape((4, 2)))

    ### Check that sum of all object counts equals the original number of events
    # num_events = 0
    # for q in quads:
    #     num_events += q.count
    # print(num_events)


    # geofixcs, grs80lla = get_GOESR_coordsys()
    # print(geofixcs.fixedgrid)
    # print('-----------------------------------------')
    # print(grs80lla)

    # for pos in ['east', 'west', 'test']:
    #     for view in ['full', 'conus', 'meso']:
    #         for resolution in ['0.5', '1.0', '2.0', '4.0', '8.0', '10.0']:
    #             print('-----\n', pos, view, resolution)
    #             for k, v in get_GOESR_grid(pos, view, resolution).items():
    #                 print(k, v)

    # import numpy as np
    #
    # view = get_GOESR_grid('east', 'full', '8.0')
    # y = np.linspace(view['y_img_bounds']['s'], view['y_img_bounds']['n'], view['pixels_NS'])
    # x = np.linspace(view['x_img_bounds']['w'], view['x_img_bounds']['e'], view['pixels_EW'])
    #
    # print(y.shape)
    # print(x.shape)
