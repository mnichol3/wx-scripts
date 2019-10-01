"""
https://github.com/deeplycloudy/lmatools/blob/master/lmatools/grid/fixed.py
"""
from coord_sys import GeostationaryFixedGridSystem, GeographicSystem


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


if __name__ == '__main__':
    geofixcs, grs80lla = get_GOESR_coordsys()
    print(geofixcs.fixedgrid)
    print('-----------------------------------------')
    print(grs80lla)
    # for pos in ['east', 'west', 'test']:
    #     for view in ['full', 'conus', 'meso']:
    #         for resolution in ['0.5', '1.0', '2.0', '4.0', '8.0', '10.0']:
    #             print('-----\n', pos, view, resolution)
    #             for k, v in get_GOESR_grid(pos, view, resolution).items():
    #                 print(k, v)
