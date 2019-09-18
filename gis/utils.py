import pyproj
from shapely.ops import transform
from shapely.geometry import Point, LineString
from shapely.geometry import Polygon as shp_Polygon
from functools import partial



def geodesic_point_buffer(lat, lon, km):
    """
    Creates a circle on on the earth's surface, centered at (lat, lon) with
    radius of km. Used to form the range rings needed for plotting

    Parameters
    ------------
    lat : float
        Latitude coordinate of the circle's center

    lon : float
        Longitude coordinate of the circle's center

    km : int
        Radius of the circle, in km


    Returns
    ------------
    A list of floats that prepresent the coordinates of the circle's edges

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

    return transform(project, buf).exterior
