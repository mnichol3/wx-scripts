"""
Author: Matt Nicholson

Functions that assist in processing MRMS data for plotting
"""
import numpy as np
from pyproj import Geod
import pyproj

from grib import fetch_scans, get_grib_objs
from mrmscomposite import MRMSComposite



def get_cross_cubic(grb, point1, point2):
    """
    Calculates the cross section of a single MRMSGrib object's data from point1 to point2
    using cubic interpolation

    Parameters
    ----------
    grb : MRMSGrib object
    point1 : tuple of float
        Coordinates of the first point that defined the cross section
        Format: (lat, lon)
    point2 : tuple of float
        Coordinates of the second point that defined the cross section
        Format: (lat, lon)

    Returns
    -------
    zi : numpy nd array
        Array containing cross-section reflectivity
    """
    lons = grb.grid_lons
    lats = grb.grid_lats

    x, y = np.meshgrid(lons, lats)
    z = grb.data

    # [(x1, y1), (x2, y2)]
    line = [(point1[0], point1[1]), (point2[0], point2[1])]

    # cubic interpolation
    y_world, x_world = np.array(list(zip(*line)))
    col = z.shape[1] * (x_world - x.min()) / x.ptp()
    row = z.shape[0] * (y.max() - y_world ) / y.ptp()

    num = 100
    row, col = [np.linspace(item[0], item[1], num) for item in [row, col]]

    valid_date = grb.validity_date
    valid_time = grb.validity_time

    # Extract the values along the line, using cubic interpolation
    zi = scipy.ndimage.map_coordinates(z, np.vstack((row, col)), order=1, mode='nearest')

    return zi



def get_cross_neighbor(grb, point1, point2):
    """
    Calculates the cross section of a single MRMSGrib object's data from point1 to point2
    using nearest-neighbor interpolation

    Parameters
    ----------
    grb : MRMSGrib object
    point1 : tuple of float
        Coordinates of the first point that defined the cross section
        Format: (lat, lon)
    point2 : tuple of float
        Coordinates of the second point that defined the cross section
        Format: (lat, lon)

    Returns
    -------
    zi : numpy nd array
        Array containing cross-section reflectivity
    """
    lons = grb.grid_lons
    lats = grb.grid_lats

    x, y = np.meshgrid(lons, lats)

    # Read the MRMS reflectivity data from the grib object's memory-mapped array
    z = np.memmap(grb.get_data_path(), dtype='float32', mode='r', shape=grb.shape)

    # Calculate the coordinates of a line defined by point1 & point2 to sample
    line = [(point1[0], point1[1]), (point2[0], point2[1])]

    y_world, x_world = np.array(list(zip(*line)))

    col = z.shape[1] * (x_world - x.min()) / x.ptp()
    row = z.shape[0] * (y.max() - y_world ) / y.ptp()

    num = 1000
    row, col = [np.linspace(item[0], item[1], num) for item in [row, col]]

    valid_date = grb.validity_date
    valid_time = grb.validity_time

    d_lats, d_lons = calc_coords(point1, point2, num)

    # Sample the points along the line in order to get the reflectivity values
    zi = z[row.astype(int), col.astype(int)]

    return (zi, d_lats, d_lons)



def process_slice(base_path, slice_time, point1, point2):
    """
    Computes a vertical cross section slice of MRMS reflectivity data along the
    line defined by point1 & point2

    Parameters
    ----------
    base_path : str
        Path to the parent MRMS data directory
    slice_time : str
        Validity time of the desired data
    point1 : tuple of floats
        First coordinate pair defining the cross section
        Format: (lat, lon)
    point2 : tuple of floats
        Second coordinate pair defining the cross section
        Format: (lat, lon)

    Returns
    -------
    Tuple of (numpy array, list, list)
        Contains the cross section array, lats, and lons
    """
    cross_sections = np.array([])

    scans = fetch_scans(base_path, slice_time) # z = 33
    grbs = get_grib_objs(scans, base_path, point1, point2)

    cross_sections, lats, lons = np.asarray(get_cross_neighbor(grbs[0], point1, point2))

    for grb in grbs[1:]:
        x_sect, _, _ = get_cross_neighbor(grb, point1, point2)
        cross_sections = np.vstack((cross_sections, x_sect))

    return (cross_sections, lats, lons)



def calc_geod_pts(point1, point2, num_pts):
    """
    Calculates a number of points, num_pts, along a line defined by point1 & point2

    Parameters
    ----------
    point1 : tuple of floats
        First geographic coordinate pair
        Format: (lat, lon)
    point2 : tuple of floats
        Second geographic coordinate pair
        Format: (lat, lon)
    num_pts : int
        Number of coordinate pairs to calculate

    Returns
    -------
    Yields a tuple of floats
    Format: (lon, lat)
    """
    geod = Geod("+ellps=WGS84")
    points = geod.npts(lon1=point1[1], lat1=point1[0], lon2=point2[1],
                   lat2=point2[0], npts=num_pts)

    for pt in points:
        yield pt



def get_composite_ref(base_path, slice_time, point1, point2, memmap_path):
    """
    Creates a composite reflectivity product from the 33 MRMS scan angles

    Parameters
    ----------
    base_path : str
        Path of the parent MRMS data directory
    slice_time : str
        Validity time of the desired data
    point1 : tuple of floats
        First coordinate pair defining the cross section
        Format: (lat, lon)
    point2 : tuple of floats
        Second coordinate pair defining the cross section
        Format: (lat, lon)
    memmap_path : str
        Path to the directory being used to store memory-mapped array files

    Returns
    -------
    comp_obj : MRMSComposite object
    """
    scans = fetch_scans(base_path, slice_time)

    grbs = get_grib_objs(scans, base_path, point1, point2)

    valid_date = grbs[0].validity_date
    valid_time = grbs[0].validity_time
    major_axis = grbs[0].major_axis
    minor_axis = grbs[0].minor_axis
    data_shape = grbs[0].shape

    fname = 'mrms-cross-{}-{}z.txt'.format(valid_date, valid_time)

    scan_0 = np.memmap(grbs[0].get_data_path(), dtype='float32', mode='r', shape=grbs[0].shape)
    composite = np.empty_like(scan_0)
    composite[:] = scan_0

    del scan_0

    for grb in grbs[1:]:
        curr_ref = np.memmap(grb.get_data_path(), dtype='float32', mode='r', shape=grb.shape)

        for idx, val in enumerate(composite):
            for sub_idx, sub_val in enumerate(val):
                if (curr_ref[idx][sub_idx] > composite[idx][sub_idx]):
                    composite[idx][sub_idx] = curr_ref[idx][sub_idx]
        del curr_ref

    fname = '{}-{}-{}'.format('comp_ref', valid_date, valid_time)
    outpath = join(memmap_path, fname)

    # write the composite data to memmap array
    fp = np.memmap(outpath, dtype='float32', mode='w+', shape=data_shape)
    fp[:] = composite[:]
    del fp

    comp_obj = MRMSComposite(valid_date, valid_time, major_axis, minor_axis,
                             outpath, fname, data_shape, grid_lons=grbs[0].grid_lons,
                             grid_lats=grbs[0].grid_lats)

    return comp_obj
