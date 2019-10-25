"""
21 June 2019
Author : Matt Nicholson

This file contains functions to convert GOES-16 N/S Elevation angle and E/W
Scanning Angle coordinates to GRS80 Ellipsoid latitude and longitude coordinates
and vice versa.

Equations obtained from:

United States, Congress, National Oceanic & Atmospheric Administration.
    “GOES R Series Product Definition and User's Guide.”
    GOES R Series Product Definition and User's Guide, 2nd ed., vol. 3,
    Harris Corporation, 2018, pp. 56–60.


Example usage
--------------
in : print(geod_to_scan(48.0563, -70.1242))
out: (0.12390027294128181, 0.00950246171751412)

in : print(geod_to_scan(33.943546, -84.52599))
out: (0.09557181243071429, -0.023614853364253407)

in:
    print('NW: ', scan_to_geod(0.11088, -0.0728))
    print('NE: ', scan_to_geod(0.11088, -0.0448))
    print('SW: ', scan_to_geod(0.08288, -0.0728))
    print('SE: ', scan_to_geod(0.08288, -0.0448))
out:
    NW:  (42.324332772441274, -111.59881367398036)
    NE:  (41.3977345174855, -95.77874169810512)
    SW:  (29.26380930573638, -104.3619728276011)
    SE:  (28.846349046410847, -92.23420546721754)
"""

from numpy import sin, cos, tan, arcsin, arctan, sqrt, degrees, radians, ndarray, asarray



def scan_to_geod(y, x):
    """
    Calculates the GRS80 ellipsoid geodetic latitude & longitude coordinates
    from GOES-R ABI fixed grid y & x coordinates

    Parameters
    ----------
    y : float
        GOES-R ABI fixed grid y coordinate representing the N/S Elevation Angle,
        in radians
    x : float
        GOES-R ABI fixed grid x coordinate representing the E/W Elevation Angle,
        in radians

    Returns
    -------
    tuple of floats
        Tuple containing two floats; the first is the Geodetic Latitude (in deg.),
        the second is the Geodetic Longitude (in deg.)
        Format: (lat, lon)

    Dependencies                              Alias
    -------------                            -------
    > proj_utils._calc_a                       ---
    > proj_utils._calc_b                       ---
    > proj_utils._calc_c                       ---
    > proj_utils._calc_rs                      ---
    > proj_utils._calc_sx                      ---
    > proj_utils._calc_sy                      ---
    > proj_utils._calc_sz                      ---
    > numpy.sqrt                      (from numpy import sqrt)
    > numpy.arctan                    (from numpy import arctan)
    > numpy.degrees                   (from numpy import degrees)

    References
    -----------
    United States, Congress, National Oceanic & Atmospheric Administration.
        “GOES R Series Product Definition and User's Guide.”
        GOES R Series Product Definition and User's Guide, 2nd ed., vol. 3,
        Harris Corporation, 2018, pp. 56–60.
    """
    r_eq = 6378137          # semi major axis of projection, m
    inv_f = 298.257222096   # inverse flattening
    r_pol = 6356752.31414   # semi minor axis of projection, m
    e = 0.0818191910435
    h_goes = 35786023       # perspective point height, m
    H = 42164160            # h_goes + r_eq, m
    lambda_0 = -1.308996939 # longitude of origin projection

    if (not isinstance(x, float)):
        x = float(x)
    if (not isinstance(y, float)):
        y = float(y)

    a = _calc_a(x, y, r_eq, r_pol)
    b = _calc_b(x, y, H)
    c = _calc_c(H, r_eq)
    r_s = _calc_rs(a, b, c)
    s_x = _calc_sx(r_s, x, y)
    s_y = _calc_sy(r_s, x)
    s_z = _calc_sz(r_s, x, y)

    lat1 = (r_eq**2) / (r_pol**2)
    lat2 = s_z / (sqrt((H - s_x)**2 + s_y**2))
    lat = arctan(lat1 * lat2)

    lon1 = arctan(s_y / (H - s_x))
    lon = lambda_0 - lon1

    ################### For debugging ###################
    # print('a ', a)
    # print('b ', b)
    # print('c ', c)
    # print('r_s ', r_s)
    # print('s_x ', s_x)
    # print('s_y ', s_y)
    # print('s_z ', s_z)
    #####################################################

    lon = degrees(lon)
    lat = degrees(lat)

    return (lat, lon)



def geod_to_scan(lat, lon):
    """
    Calculates GOES-R ABI fixed grid y & x coordinates from latitude and longitude
    coordinates

    Parameters
    ----------
    lat : float
        GRS80 Ellipsoid geodetic latitude coordinate, in degrees
    lon : float
        GRS80 Ellipsoid geodetic longitude coordinate, in degrees

    Returns
    -------
    tuple of floats
        Tuple of two floats; the first is the N/S Elevation angle (in radians),
        the second is the E/W Elevation angle (in radians)

    Dependencies                              Alias
    ------------                             -------
    > proj_utils._calc_thetac                  ---
    > proj_utils._calc_rc                      ---
    > proj_utils._calc_sx_inv                  ---
    > proj_utils._calc_sy_inv                  ---
    > proj_utils._calc_sz_inv                  ---
    > numpy.sqrt                      (from numpy import sqrt)
    > numpy.arctan                    (from numpy import arctan)
    > numpy.radians                   (from numpy import radians)

    References
    ----------
    United States, Congress, National Oceanic & Atmospheric Administration.
        “GOES R Series Product Definition and User's Guide.”
        GOES R Series Product Definition and User's Guide, 2nd ed., vol. 3,
        Harris Corporation, 2018, pp. 56–60.
    """
    r_eq = 6378137          # semi major axis of projection, m
    inv_f = 298.257222096   # inverse flattening
    r_pol = 6356752.31414   # semi minor axis of projection, m
    e = 0.0818191910435
    h_goes = 35786023       # perspective point height, m
    H = 42164160            # h_goes + r_eq, m
    lambda_0 = -1.308996939 # longitude of origin projection

    if (not isinstance(lat, float)):
        lat = float(lat)
    if (not isinstance(lon, float)):
        lon = float(lon)

    lat = radians(lat)
    lon = radians(lon)

    theta_c = _calc_thetac(r_eq, r_pol, lat)
    r_c = _calc_rc(r_pol, e, theta_c)
    s_x = _calc_sx_inv(H, r_c, theta_c, lon, lambda_0)
    s_y = _calc_sy_inv(r_c, theta_c, lon, lambda_0)
    s_z = _calc_sz_inv(r_c, theta_c)

    y = arctan(s_z / s_x)

    x = -s_y / (sqrt(s_x**2 + s_y**2 + s_z**2))

    return (y, x)



def get_fixed_grid_edges(y, x, grid_res):
    """
    Get the coordinates of the ABI Fixed Grid cell edges

    See GOES-16 PUG Vol. 3 Sec. 5.1.2

    Parameters
    ----------
    y : numpy ndarray
        y (E/W scanning angle) coordinates, in radians
    x : numpy ndarray
        x (N/S elevation angle) coordinates, in radians
    grid_res : str
        Grid resolution. Valid values: ['0.5', '1.0', '2.0', '4.0', '10.0']

    Returns
    -------
    tuple of numpy ndarrays containing grid cell edges
        Format: (y_edges, x_edges)

    Dependencies                    Alias
    ------------                   -------
    > NumPy                 (import numpy as np)
    """
    # These values represent the distance from the center of a grid cell to the
    # edges. Obtained from the GOES-16 PUG Vol. 3 Sec. 5.1.2
    res_vals = {
                '0.5' : 0.7e-05,
                '1.0' : 1.4e-05,
                '2.0' : 2.8e-05,
                '4.0' : 5.6e-05,
                '10.0': 14.0e-05
                }

    # More useful than getting a KeyError
    if (grid_res not in res_vals.keys()):
        raise ValueError(("Invalid grid resolution '{}'."
                          "Valid values: ['0.5', '1.0', '2.0', '4.0', '10.0']".format(resolution)))

    # Get the edge offset value for the given grid cell resolution
    edge_offset = res_vals[grid_res]

    # Subtract the edge offset from each grid cell centroid value, which yields
    # the left edge of every cell (and the right edge for every cell in x[n-1])
    #
    # Add the offset value to the last centroid in the array to obtain
    # it's right edge
    x_edges = x - edge_offset
    x_edges = np.append(x_edges, x[-1] + edge_offset)

    y_edges = y - edge_offset
    y_edges = np.append(y_edges, y[-1] + edge_offset)

    return (y_edges, x_edges)



def remove_glm_ellipse(lat, lon):
    """
    Remove the GLM parallax correction built into the L2 Events, Groups,
    & Flashes (EGF) data

    Parameters
    -----------
    lat : float or numpy array of floats
        Geodetic latitude(s) of GLM EGF data
    lon : float or numpy array of floats
        Geodetic longitude(s) of GLM EGF data

    Returns
    -------
    alpha : float or numpy array of floats
        North/South elevation angle (y-axis), in radians
    beta : float or numpy array of floats
        East/West scanning angle (x-axis), in radians

    Dependencies                    Alias
    ------------                   -------
    > numpy.radians         (from numpy import radians)
    > numpy.asarray         (from numpy import asarray)
    > numpy.ndarray         (from numpy import ndarray)
    > numpy.sin             (from numpy import sin)
    > numpy.cos             (from numpy import cos)
    > numpy.tan             (from numpy import tan)
    > numpy.arcsin          (from numpy import arcsin)
    > numpy.arctan          (from numpy import arctan)
    > numpy.sqrt            (from numpy import sqrt)

    References
    ----------
    United States, Congress, National Oceanic & Atmospheric Administration.
        “GOES R Series Product Definition and User's Guide.”
        GOES R Series Product Definition and User's Guide, 2nd ed., vol. 3,
        Harris Corporation, 2018, pp. 56–60.

    Van Bezooijen R.W.H, et al. “Image Navigation and Registration for the Geostationary
        Lightning Mapper (Glm).” Proceedings of Spie - the International Society
        for Optical Engineering, vol. 10004, 2016, doi:10.1117/12.2242141.
    """
    re_grs80    = 6.378137e6       # GRS80 equatorial radius, in meters
    rp_grs80    = 6.35675231414e6  # GRS80 polar radius, in meters
    sat_lon_r   = -1.308996939     # GOES-16 longitude of projection origin, in radians
    sat_lon_d   = -75.0            # GOES-16 longitude of projection origin, in degrees
    sat_h_grs80 = 35786023         # GOES-16 height above GRS80 surface, in meters

    re_le = 6.378137e6 + 14.0e3    # GLM Lightning Ellipse equatorial radius, in meters
    rp_le = 6.362755e6             # GLM Lightning Ellipse polar radius, in meters

    sat_H  = sat_h_grs80 + re_grs80             # GOES-16 GRS80 geocentric distance, in meters
    ff_grs = (re_grs80 - rp_grs80) / re_grs80   # GRS80 flattening factor
    ff_le  = (re_le - rp_le) / re_le            # GLM Lightning Ellipse flattening factor

    # Validate the arguments
    if (not isinstance(lon,  ndarray)):
        if (isinstance(lon, float) or isinstance(lon, int)):
            lon = asarray([lon])
        else:
            raise ValueError("'lon' arg must be a float, int, or numpy ndarray")

    if (not isinstance(lat,  ndarray)):
        if (isinstance(lat, float) or isinstance(lat, int)):
            lat = asarray([lat])
        else:
            raise ValueError("'lat' arg must be a float, int, or numpy ndarray")

    delta_lon = lon - sat_lon_d
    delta_lon[delta_lon < -180] += 360
    delta_lon[delta_lon > 180] -= 360

    lon_rad = radians(delta_lon)
    lat_rad = radians(lat)

    # Calculate the geocentric lat & lon
    lon_geocent = lon_rad
    lat_geocent = arctan(tan(lat_rad) * (1.0 - ff_grs)**2.0)

    cos_lat = cos(lat_geocent)
    sin_lat = sin(lat_geocent)

    # Calculate the vector from the center of the lightning ellipse to a point
    # on the surface
    R_num = re_le * (1.0 - ff_le)
    R_denom = sqrt(1.0 - ff_le * (2.0 - ff_le) * cos_lat**2)

    R_le = (R_num / R_denom)

    v_x = R_le * cos_lat * cos(lon_geocent) - sat_H
    v_y = R_le * cos_lat * sin(lon_geocent)
    v_z = R_le * sin_lat

    # Take the unit vector of V
    v_mag = sqrt(v_x**2 + v_y**2 + v_z**2)
    v_x /= v_mag
    v_y /= v_mag
    v_z /= v_mag

    # Implement DCM rotation due to reference frame change.
    # x-axis points towards Earth, z-axis points up, y-axis points left
    v_x *= -1
    v_y *= -1

    alpha = arctan(v_z / v_x)    # y-axis
    beta = -arcsin(v_y)          # x-axis

    return (alpha, beta)



################################################################################
############## Helper Functions: geod_to_scan() & scan_to_geod() ###############
################################################################################


def _calc_a(x, y, r_eq, r_pol):
    """
    Calculates the a coefficient used to calculate the distance from the satellite
    to a point P

    Parameters
    ----------
    x : float
        GOES-R ABI fixed grid y coordinate representing the N/S Elevation Angle,
        in radians
    y : float
        GOES-R ABI fixed grid y coordinate representing the N/S Elevation Angle,
        in radians
    r_eq : int
        GOES-16 semi-major axis of projection, in meters
    r_pol
        GOES-16 semi-minor axis of projection, in meters

    Returns
    -------
    float

    Dependencies                    Alias
    -------------                  -------
    > numpy.sin             (from numpy import sin)
    > numpy.cos             (from numpy import cos)
    """
    f = sin(x)**2 + cos(x)**2
    g = cos(y)**2 + (r_eq**2 / r_pol**2) * (sin(y)**2)
    return f * g



def _calc_b(x, y, H):
    """
    Calculates the b coefficient used to calculate the distance from the satellite
    to a point P

    Parameters
    ----------
    x : float
        GOES-R ABI fixed grid y coordinate representing the N/S Elevation Angle,
        in radians
    y : float
        GOES-R ABI fixed grid y coordinate representing the N/S Elevation Angle,
        in radians
    H : int
        GOES-16 projection perspective point height, in meters

    Returns
    -------
    float

    Dependencies                    Alias
    -------------                  -------
    > numpy.cos             (from numpy import cos)
    """
    f = -2 * H * (cos(x)) * (cos(y))
    return f



def _calc_c(H, r_eq):
    """
    Calculates the b coefficient used to calculate the distance from the satellite
    to a point P

    Parameters
    ----------
    H : int
        GOES-16 projection perspective point height, in meters
    r_eq : int
        GOES-16 semi-major axis of projection, in meters

    Returns
    -------
    float

    Dependencies                    Alias
    -------------                  -------
    None
    """
    return (H**2 - r_eq**2)



def _calc_rs(a, b, c):
    """
    Calculates the distance from the satellite to a point P using the quadratic
    formula

    Parameters
    ----------
    a : float
        'a' coefficient for the quadratic formula
    b : float
        b coefficient for the quadratic formula
    c : float
        c coefficient for the quadratic formula

    Returns
    -------
    float
        distance of the satellite from point P, in meters

    Dependencies                    Alias
    -------------                  -------
    > numpy.sqrt           (from numpy import sqrt)
    """
    try:
        num = -b - sqrt((b**2) - 4*a*c)
    except ValueError:
        print('\nWarning: ValueError caught in _calc_rs')
        print('Attempting again with the absolute value\n')
        num = -b - sqrt(abs((b**2) - 4*a*c))
    den = 2 * a
    return num / den



def _calc_sx(r_s, x, y):
    """
    Calculates the x-axis of the satellite coordinate frame for scan_to_geod

    Parameters
    ----------
    r_s : float
        Distance from the satellite to point P, in meters
    x : float
        GOES-R ABI fixed grid x coordinate representing the E/W Elevation Angle,
        in radians
    y : float
        GOES-R ABI fixed grid y coordinate representing the N/S Elevation Angle,
        in radians

    Returns
    -------
    s_x : float
        x-axis of the satellite coordinate frame

    Dependencies                    Alias
    -------------                  -------
    > numpy.cos             (from numpy import cos)
    """
    s_x = r_s * cos(x) * cos(y)
    return s_x



def _calc_sy(r_s, x):
    """
    Calculates the y-axis of the satellite coordinate frame for scan_to_geod

    Parameters
    ----------
    r_s : float
        Distance from the satellite to point P, in meters
    x : float
        GOES-R ABI fixed grid x coordinate representing the E/W Elevation Angle,
        in radians

    Returns
    -------
    s_y : float
        y-axis of the satellite coordinate frame

    Dependencies                    Alias
    -------------                  -------
    > numpy.sin             (from numpy import sin)
    """
    s_y = -r_s * sin(x)
    return s_y



def _calc_sz(r_s, x, y):
    """
    Calculates the z-axis of the satellite coordinate frame for scan_to_geod

    Parameters
    ----------
    r_s : float
        Distance from the satellite to point P, in meters
    x : float
        GOES-R ABI fixed grid x coordinate representing the E/W Elevation Angle,
        in radians
    y : float
        GOES-R ABI fixed grid y coordinate representing the N/S Elevation Angle,
        in radians

    Returns
    -------
    s_z : float
        z-axis of the satellite coordinate frame

    Dependencies                    Alias
    -------------                  -------
    > numpy.sin             (from numpy import sin)
    > numpy.cos             (from numpy import cos)
    """
    s_z = r_s * cos(x) * sin(y)
    return s_z



def _calc_thetac(r_eq, r_pol, lat):
    """
    Calculates the geocentric latitude, in radians

    Parameters
    ----------
    r_eq : int
        GOES-16 semi-major axis of projection, in meters
    r_pol : int
        GOES-16 semi-minor axis of projection, in meters
    lat : float
        GRS80 geodetic latitude, in radians

    Returns
    -------
    theta_c : float
        Geocentric latitude, in radians

    Dependencies                    Alias
    -------------                  -------
    > numpy.tan             (from numpy import tan)
    > numpy.arctan          (from numpy import arctan)
    """
    theta_c = (r_pol**2) / (r_eq**2)
    theta_c = theta_c * tan(lat)
    theta_c = arctan(theta_c)
    return theta_c



def _calc_rc(r_pol, e, theta_c):
    """
    Calculates the geodetic distance to the point on the ellipsoid

    Parameters
    ----------
    r_pol : int
        GOES-16 semi-minor axis of projection, in meters
    e : float
        Uh...
    theta_c
        Geocentric latitude, in radians

    Returns
    -------
    r_c : float
        Geocentric distance to the point on the ellipsoid, in meters

    Dependencies                    Alias
    -------------                  -------
    > numpy.sqrt            (from numpy import sqrt)
    > numpy.cos             (from numpy import cos)
    """
    den = sqrt(1 - e**2 * cos(theta_c)**2)
    r_c = r_pol / den
    return r_c



def _calc_sx_inv(H, r_c, theta_c, lon, lambda_0):
    """
    Calculates the x-axis of the satellite coordinate frame for geod_to_scan

    Parameters
    ----------
    H : int
        GOES-16 imagery projection perspective point height + semi-major axis, in meters
    r_c : float
        Geodetic distance to the point on the ellipsoid
    theta_c : float
        Geocentric latitude, in radians
    lon : float
        Geodetic longitude coordinate, in radians
    lambda_0: float
        GOES-16 longitude of projection origin, in radians

    Returns
    -------
    s_x : float
        X-axis of the satellite coordinate frame

    Dependencies                    Alias
    -------------                  -------
    > numpy.cos             (from numpy import cos)
    """
    s_x = H - (r_c * cos(theta_c) * cos(lon - lambda_0))
    return s_x



def _calc_sy_inv(r_c, theta_c, lon, lambda_0):
    """
    Calculates the y-axis of the satellite coordinate frame for geod_to_scan

    Parameters
    ----------
    r_c : float
        Geodetic distance to the point on the ellipsoid
    theta_c : float
        Geocentric latitude, in radians
    lon : float
        Geodetic longitude coordinate, in radians
    lambda_0: float
        GOES-16 longitude of projection origin, in radians

    Returns
    -------
    s_y : float
        Y-axis of the satellite coordinate frame

    Dependencies                    Alias
    -------------                  -------
    > numpy.sin             (from numpy import sin)
    > numpy.cos             (from numpy import cos)
    """
    s_y = -r_c * cos(theta_c) * sin(lon - lambda_0)
    return s_y



def _calc_sz_inv(r_c, theta_c):
    """
    Calculates the z-axis of the satellite coordinate frame for geod_to_scan

    Parameters
    ----------
    r_c : float
        Geodetic distance to the point on the ellipsoid
    theta_c : float
        Geocentric latitude, in radians

    Returns
    -------
    s_z : float
        Z-axis of the satellite coordinate frame

    Dependencies                    Alias
    -------------                  -------
    > numpy.sin             (from numpy import sin)
    """
    s_z = r_c * sin(theta_c)
    return s_z



################################################################################
############## Helper Functions: geod_to_scan() & scan_to_geod() ###############
################################################################################




def main():
    alpha = 0.08288
    beta = -0.0448

    lat, lon = scan_to_geod(alpha, beta)

    print('-'*30)
    print('Raw:')
    print('     alpha: {0:.5f}'.format(alpha))
    print('     beta: {0:.5f}'.format(beta))
    print('     lat:   {0:.5f}'.format(lat))
    print('     lon:  {0:.5f}'.format(lon))

    alpha, beta = remove_glm_ellipse(lat, lon)
    lat, lon = scan_to_geod(alpha, beta)

    print('-'*30)
    print('Corrected:')
    print('     alpha: {0:.5f}'.format(alpha[0]))
    print('     beta: {0:5f}'.format(beta[0]))
    print('     lat:   {0:.5f}'.format(lat))
    print('     lon:  {0:.5f}'.format(lon))
    print('-'*30)

    """
    Output:
    ------------------------------
    Raw:
        alpha: 0.08288
        beta: -0.0448
        lat: 28.846349046410847
        lon: -92.23420546721754
    ------------------------------
    Corrected:
         alpha: 0.08306
         beta: -0.044897
         lat: 28.919735289856177
         lon: -92.28812036958603
    ------------------------------
    """


if __name__ == '__main__':
    main()
