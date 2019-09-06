"""
Author: Matt Nicholson

Functions for processing GOES imagery files
"""
from os import listdir
from os.path import isfile, join
import pyproj
import numpy as np
from netCDF4 import Dataset

from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
import matplotlib.colors as colors
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.cm as cm
from cartopy.feature import NaturalEarthFeature
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
import sys
import re
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point

from localglmfile import LocalGLMFile
from proj_utils import geod_to_scan, scan_to_geod

from sys import exit


def trim_header(abs_path):
    """
    Trim the header off AWIPS-compatable GLM files and convert to netCDF. Not
    needed for files obtained from AWS

    Parameters
    ----------
    abs_path : str
        Absolute path of the file to read

    Returns
    -------
    abs_path : str
        Absolute path of the new file

    Dependencies
    ------------
    > os.path.isfile
    """
    if (not isfile(abs_path)):
        raise OSError('File does not exist:', abs_path)

    if (not isfile(abs_path + '.nc') and abs_path[-3:] != '.nc'):

        with open(abs_path, 'rb') as f_in:
            f_in.seek(21)
            data = f_in.read()
            f_in.close()
            f_in = None

        with open(abs_path + '.nc', 'wb') as f_out:
            f_out.write(data)
            f_out.close()
            f_out = None

    if (abs_path[-3:] != '.nc'):
        abs_path = abs_path + '.nc'

    return abs_path



def get_fnames_from_dir(base_path):
    """
    Get a list of the imagery files located in the base_path directory

    Parameters
    ----------
    base_path : str
        Absolute path of the directory holding the imagery files

    Returns
    -------
    fnames : list of str
        List of the filenames of the imagery files located in the base_path dir

    Dependencies
    ------------
    > os.listdir
    > os.path.isfile
    > os.path.join
    """
    fnames = [f for f in listdir(base_path) if isfile(join(base_path, f))]

    return fnames



def fname_gen(base_path):
    """
    Similar to get_fnames_from_dir(), but creates a generator instead of returning
    a list

    Parameters
    ----------
    base_path : str
        Absolute path of the directory holding the imagery files

    Returns
    -------
    yields a str

    Dependencies
    ------------
    > os.listdir
    > os.path.isfile
    > os.path.join
    """
    for (f in listdir(base_path)):
        if (isfile(join(base_path, f)):
            yield f



def read_file_glm(abs_path, window=False):
    """
    Read a GLM file into a glm_obj

    Parameters
    ----------
    abs_path : str
        Absolute path to the GLM file to open & read
    window : bool, optional
        If True, the 5-min GLM window data is used. If False, 1-min data is used
        Default: False

    Returns
    -------
    glm_obj : LocalGLMFile object
        LocalGLMFile object containing the data from the glm file

    Dependencies
    ------------
    > localglmfile.py
    > netCDF4.Dataset
    """
    data_dict = {}
    f_path = trim_header(abs_path)

    fh = Dataset(f_path, 'r')

    data_dict['long_name'] = fh.variables['goes_imager_projection'].long_name
    data_dict['lat_0'] = fh.variables['goes_imager_projection'].latitude_of_projection_origin
    data_dict['lon_0'] = fh.variables['goes_imager_projection'].longitude_of_projection_origin
    data_dict['semi_major_axis'] = fh.variables['goes_imager_projection'].semi_major_axis
    data_dict['semi_minor_axis'] = fh.variables['goes_imager_projection'].semi_minor_axis
    data_dict['height'] = fh.variables['goes_imager_projection'].perspective_point_height
    data_dict['inv_flattening'] = fh.variables['goes_imager_projection'].inverse_flattening
    data_dict['sweep_ang_axis'] = fh.variables['goes_imager_projection'].sweep_angle_axis

    data_dict['x'] = fh.variables['x'][:]
    data_dict['y'] = fh.variables['y'][:]

    if (window is not False):
        data_dict['data'] = fh.variables['Flash_extent_density_window'][:]
    else:
        data_dict['data'] = fh.variables['Flash_extent_density'][:]

    fh.close()
    fh = None

    glm_obj = LocalGLMFile(f_path)
    glm_obj.set_data(data_dict)

    return glm_obj



def read_file_abi(abi_file, extent=None):
    """
    Opens & reads a GOES-16 ABI data file, returning a dictionary of data

    Parameters:
    ------------
    abi_file : str
        Absolute path of the GOES-16 ABI file to be opened & processed
    extent : list of float, optional
        List of floats used to subset the ABI data
        Format: [min_lat, max_lat, min_lon, max_lon]


    Returns:
    ------------
    data_dict : dictionary of str
        Dictionar of ABI image data & metadata from the netCDF file
    """
    data_dict = {}
    product_re = r'OR_ABI-L\d\w?-(\w{3,5})[CFM]\d?-M\d'
    sector_re = r'OR_ABI-L\d\w?-\w{3,5}([CFM]\d?)-M\d'

    # Get the data product from the filename
    prod_match = re.search(product_re, abi_file)
    if (prod_match):
        prod = prod_match.group(1)
    else:
        raise IOError('Unable to parse ABI product from filename')

    # Get the scan sector from the filename
    sector_match = re.search(sector_re, abi_file)
    if (sector_match):
        sector = sector_match.group(1)
    else:
        raise IOError('Unable to parse ABI scan sector from filename')

    # Open the netCDF file
    fh = Dataset(abi_file, mode='r')

    if ('Rad' in prod):
        prod_key = 'Rad'
        data_dict['min_data_val'] = fh.variables['min_radiance_value_of_valid_pixels'][0]
        data_dict['max_data_val'] = fh.variables['max_radiance_value_of_valid_pixels'][0]
    elif ('CMIP' in prod):
        prod_key = 'CMI'
        data_dict['min_data_val'] = fh.variables['min_brightness_temperature'][0]
        data_dict['max_data_val'] = fh.variables['max_brightness_temperature'][0]
    else:
        raise ValueError('Invalid ABI product key')


    data_dict['band_id'] = fh.variables['band_id'][0]

    data_dict['band_wavelength'] = "%.2f" % fh.variables['band_wavelength'][0]
    data_dict['semimajor_ax'] = fh.variables['goes_imager_projection'].semi_major_axis
    data_dict['semiminor_ax'] = fh.variables['goes_imager_projection'].semi_minor_axis
    data_dict['inverse_flattening'] = fh.variables['goes_imager_projection'].inverse_flattening

    data_dict['data_units'] = fh.variables[prod_key].units

    # Seconds since 2000-01-01 12:00:00
    add_seconds = fh.variables['t'][0]

    # Datetime of scan
    scan_date = datetime(2000, 1, 1, 12) + timedelta(seconds=float(add_seconds))
    scan_date = datetime.strftime(scan_date, '%Y%m%d-%H:%M:%S') # Format: YYYYMMDD-HH:MM:SS (UTC)

    # Satellite height in meters
    sat_height = fh.variables['goes_imager_projection'].perspective_point_height

    # Satellite longitude & latitude
    sat_lon = fh.variables['goes_imager_projection'].longitude_of_projection_origin
    sat_lat = fh.variables['goes_imager_projection'].latitude_of_projection_origin

    # Satellite lat/lon extend
    lat_lon_extent = {}

    # Geospatial lat/lon center
    data_dict['lat_center'] = fh.variables['geospatial_lat_lon_extent'].geospatial_lat_center
    data_dict['lon_center'] = fh.variables['geospatial_lat_lon_extent'].geospatial_lon_center

    # Satellite sweep
    sat_sweep = fh.variables['goes_imager_projection'].sweep_angle_axis

    if (extent is not None):

        # Get the indices of the x & y arrays that define the data subset
        min_y, max_y, min_x, max_x = subset_grid(extent, fh.variables['x'][:], fh.variables['y'][:])

        # Ensure the min & max values are correct
        y_min = min(min_y, max_y)
        y_max = max(min_y, max_y)
        x_min = min(min_x, max_x)
        x_max = max(min_x, max_x)

        data = fh.variables[prod_key][y_min : y_max, x_min : x_max]

        # KEEP!!!!! Determines the plot axis extent
        lat_lon_extent['n'] = extent[1]
        lat_lon_extent['s'] = extent[0]
        lat_lon_extent['e'] = extent[3]
        lat_lon_extent['w'] = extent[2]

        # Y image bounds in scan radians
        # X image bounds in scan radians
        data_dict['y_image_bounds'] = [fh.variables['y'][y_min], fh.variables['y'][y_max]]
        data_dict['x_image_bounds'] = [fh.variables['x'][x_min], fh.variables['x'][x_max]]

        y_min, x_min = scan_to_geod(fh.variables['y'][y_min], fh.variables['x'][x_min])
        y_max, x_max = scan_to_geod(fh.variables['y'][y_max], fh.variables['x'][x_max])

    else:
        data = fh.variables[prod_key][:]

        lat_lon_extent['n'] = fh.variables['geospatial_lat_lon_extent'].geospatial_northbound_latitude
        lat_lon_extent['s'] = fh.variables['geospatial_lat_lon_extent'].geospatial_southbound_latitude
        lat_lon_extent['e'] = fh.variables['geospatial_lat_lon_extent'].geospatial_eastbound_longitude
        lat_lon_extent['w'] = fh.variables['geospatial_lat_lon_extent'].geospatial_westbound_longitude

        y_bounds = fh.variables['y_image_bounds'][:]
        x_bounds = fh.variables['x_image_bounds'][:]

        # Format: (North, South)
        data_dict['y_image_bounds'] = y_bounds

        # Format: (west, East)
        data_dict['x_image_bounds'] = x_bounds

        y_min, x_min = scan_to_geod(min(y_bounds), min(x_bounds))
        y_max, x_max = scan_to_geod(max(y_bounds), max(x_bounds))

    fh.close()
    fh = None

    data_dict['scan_date'] = scan_date
    data_dict['sector'] = sector
    data_dict['product'] = prod
    data_dict['sat_height'] = sat_height
    data_dict['sat_lon'] = sat_lon
    data_dict['sat_lat'] = sat_lat
    data_dict['lat_lon_extent'] = lat_lon_extent
    data_dict['sat_sweep'] = sat_sweep
    data_dict['data'] = data
    data_dict['y_min'] = y_min
    data_dict['x_min'] = x_min
    data_dict['y_max'] = y_max
    data_dict['x_max'] = x_max

    return data_dict




def georeference(x, y, sat_lon, sat_height, sat_sweep, data=None):
    """
    Calculates the longitude and latitude coordinates of each data point

    Parameters
    ------------
    x : list of scan radians
    y : list of scan radians
    sat_lon : something
    sat_height : a number of some sort
    sat_sweep : i honestly dont know
    data : 2d array


    Returns
    ------------
    (lons, lats) : tuple of lists of floats
        Tuple containing a list of data longitude coordinates and a list of
        data latitude coordinates

    Dependencies
    ------------
    > pyproj
    > numpy
    """

    Xs = [i * sat_height for i in x]
    Ys = [j * sat_height for j in y]

    p = pyproj.Proj(proj='geos', h=sat_height, lon_0=sat_lon, sweep=sat_sweep)

    lons, lats = np.meshgrid(Xs, Ys)
    lons, lats = p(lons, lats, inverse=True)

    if (data is not None):
        lats[np.isnan(data)] = 57
        lons[np.isnan(data)] = -152

    return (lons, lats)



def idx_of_nearest(coords, val):
    X = np.abs(coords.flatten()-val)
    idx = np.where(X == X.min())
    idx = idx[0][0]
    return coords.flatten()[idx]



def create_bbox(lats, lons, point1, point2):
    bbox = {}

    p_lons = np.array([point1[1], point2[1]])
    p_lats = np.array([point1[0], point2[0]])

    lon1 = idx_of_nearest(lons, p_lons[0])
    lon2 = idx_of_nearest(lons, p_lons[1])

    lat1 = idx_of_nearest(lats, p_lats[0])
    lat2 = idx_of_nearest(lats, p_lats[1])

    if (lon1[1] > lon2[1]):
        bbox['max_lon'] = lon1
        bbox['min_lon'] = lon2
    else:
        bbox['max_lon'] = lon2
        bbox['min_lon'] = lon1

    if (lat1[1] > lat2[1]):
        bbox['max_lat'] = lat1
        bbox['min_lat'] = lat2
    else:
        bbox['max_lat'] = lat2
        bbox['min_lat'] = lat1

    return bbox



def plot_geos(data_dict):
    """
    Plot the GOES-16 ABI file on a geostationary-projection map

    Parameters
    ------------
    data_dict : dictionary
        Dictionary of data & metadata from GOES-16 ABI file


    Returns
    ------------
    A plot of the ABI data on a geostationary-projection map

    The projection x and y coordinates equals the scanning angle (in radians)
    multiplied by the satellite height
    http://proj4.org/projections/geos.html <-- 404'd
    https://proj4.org/operations/projections/geos.html

    """

    sat_height = data_dict['sat_height']
    sat_lon = data_dict['sat_lon']
    sat_sweep = data_dict['sat_sweep']
    scan_date = data_dict['scan_date']

    X, Y = georeference(data_dict['x'], data_dict['y'], sat_lon, sat_height,
                        sat_sweep, data=data_dict['data'])

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Geostationary(central_longitude=sat_lon,
                                satellite_height=sat_height,false_easting=0,false_northing=0,
                                globe=None, sweep_axis=sat_sweep))


    #ax.set_xlim(int(data_dict['lat_lon_extent']['w']), int(data_dict['lat_lon_extent']['e']))
    #ax.set_ylim(int(data_dict['lat_lon_extent']['s']), int(data_dict['lat_lon_extent']['n']))

    ax.coastlines(resolution='10m', color='gray')
    plt.pcolormesh(X, Y, data_dict['data'], cmap=cm.binary_r, vmin=data_dict['min_data_val'], vmax=data_dict['max_data_val'])

    plt.title('GOES-16 Imagery', fontweight='semibold', fontsize=15)
    plt.title('%s' % scan_date.strftime('%H:%M UTC %d %B %Y'), loc='right')
    ax.axis('equal')

    plt.show()



def plot_mercator(sat_data, plot_comms, glm_data=None, ax_extent=None):
    """
    Plot the GOES-16 data on a lambert-conformal projection map. Includes ABI
    imagery, GLM flash data, 100km, 200km, & 300km range rings, and red "+" at
    the center point

    Parameters
    ------------
    sat_data : dict
        Dictionary of data & metadata from GOES-16 ABI file
    plot_comms : dict
        Dictionary containing commands on whether or not to display the plot, save
        it, and if to save it where to save it to.
        Keys: 'save', 'show', 'outpath'
    glm_data: dict, optional
        Dictionary of data & metadata from GOES-16 GLM file
        Currently only supports Flash Extent Density (FED) data
    ax_extent: list, optional
        Geographic extent of the plot.
        Format: [min lon, max lon, min lat, max lat]



    Returns
    ------------
    A plot of the ABI data on a geostationary-projection map

    Dependencies
    ------------
    > numpy
    > cartopy.crs
    > matplotlib
    > pyplot
    > matplotlib.ticker
    > matplotlib.colors
    > mpl_toolkits.axes_grid1.make_axes_locatable
    > cartopy.mpl.gridliner.LONGITUDE_FORMATTER
    > cartopy.mpl.gridliner.LATITUDE_FORMATTER
    > matplotlib.cm
    > cartopy.feature.NaturalEarthFeature
    > proj_utils.scan_to_geod

    Notes
    -----
    - Uses imshow(), preferred over plot_mercator() for that reason
    - x & y scan_to_geod conversion handled in file reading func

    """
    z_ord = {'bottom': 1, 'sat_vis': 2, 'sat_inf': 3, 'sat': 2,
             'map':8, 'grid':9, 'top': 10}

    #################### Validate the plot_comms parameter ####################
    if (plot_comms['save']):
        if ((plot_comms['outpath'] is None) or (plot_comms['outpath'] == '')):
            raise ValueError("Must provide outpath value if 'save' is True")

    valid_keys = ['outpath', 'save', 'show']
    true_keys = list(plot_comms.keys())
    true_keys.sort()
    if (not true_keys == valid_keys):
        raise ValueError('Invalid plot_comm parameter')
    if (not plot_comms['save'] and not plot_comms['show']):
        raise ValueError("Plot 'save' and 'show' flags are both False. Halting execution as it will accomplish nothing")


    ########## Process the satellite data in preparation for plotting #########
    scan_date = sat_data['scan_date']   # Format: YYYYMMDD-HH:MM:SS (UTC)
    band = sat_data['band_id']
    print('Plotting satellite image Band {} {}z'.format(band, scan_date))

    # Define a single PlateCarree projection object to reuse
    crs_plt = ccrs.PlateCarree()    # DONT USE GLOBE ARG

    if (ax_extent is not None):
        axis_extent = ax_extent
    else:
        # min lon, max lon, min lat, max lat
        axis_extent = [sat_data['x_min'], sat_data['x_max'],
                       sat_data['y_min'], sat_data['y_max']]

    # Define globe object
    globe = ccrs.Globe(semimajor_axis=sat_data['semimajor_ax'],
                       semiminor_axis=sat_data['semiminor_ax'],
                       flattening=None, inverse_flattening=sat_data['inverse_flattening'])

    # Define geostationary projection used for conveting to Mercator
    crs_geos = ccrs.Geostationary(central_longitude=sat_data['sat_lon'],
                                  satellite_height=sat_data['sat_height'],
                                  false_easting=0, false_northing=0, globe=globe,
                                  sweep_axis=sat_data['sat_sweep'])

    # Transform the min x, min y, max x, & max y points from scan radians to
    # decimal degree lat & lon in PlateCarree projection
    trans_pts = crs_geos.transform_points(crs_plt, np.array([sat_data['x_min'], sat_data['x_max']]),
                                          np.array([sat_data['y_min'], sat_data['y_max']]))

    # Create a tuple of the points defining the extent of the satellite image
    proj_extent = (min(trans_pts[0][0], trans_pts[1][0]),
                   max(trans_pts[0][0], trans_pts[1][0]),
                   min(trans_pts[0][1], trans_pts[1][1]),
                   max(trans_pts[0][1], trans_pts[1][1]))

    # Create the figure & subplot
    fig = plt.figure(figsize=(8, 10))

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator(globe=globe))

    plt.title('GOES-16 Band {} {}z'.format(band, scan_date),
              fontsize=12, loc='left')

    ax.set_extent(axis_extent)

    # Set entire plot background black
    ax.imshow(
        np.tile(
            np.array(
                [[[0, 0, 0]]], dtype=np.uint8),
            [2, 2, 1]),
        origin='upper', transform=crs_plt, extent=[-180, 180, -180, 180],
        zorder=z_ord['bottom']
    )

    states = NaturalEarthFeature(category='cultural', scale='10m', facecolor='none',
                             name='admin_1_states_provinces_shp')

    ax.add_feature(states, linewidth=.8, edgecolor='black', zorder=z_ord['map'])

    # cmap hsv looks the coolest
    if (band == 11 or band == 13):
        # Infrared bands
        color = cm.binary
        v_max = 50   # Deg C
        v_min = -90  # Deg C
        data = _k_2_c(sat_data['data'])     # Convert data from K to C
        cbar_label = 'Temp (deg C)'
    else:
        # Non-infrared bands (most of the time will be visual)
        color = cm.gray
        data = sat_data['data']
        cbar_label = 'Radiance ({})'.format(sat_data['data_units'])

    ######################## Plot the satellite imagery #######################
    img = ax.imshow(data, cmap=color, extent=proj_extent, origin='upper',
                    vmin=v_min, vmax=v_max, transform=crs_geos, zorder=z_ord['sat'])

    ######################### Plot GLM FED, if passed #########################
    if (glm_data is not None):
        raise NotImplementedError('GLM FED plotting not yet implemented')

    # Set lat & lon grid tick marks
    lon_ticks = [x for x in range(-180, 181) if x % 2 == 0]
    lat_ticks = [x for x in range(-90, 91) if x % 2 == 0]

    gl = ax.gridlines(crs=crs_plt, linewidth=1, color='gray',
                      alpha=0.5, linestyle='--', draw_labels=True,
                      zorder=z_ord['grid'])

    gl.xlabels_top = False
    gl.ylabels_right=False
    gl.xlocator = mticker.FixedLocator(lon_ticks)
    gl.ylocator = mticker.FixedLocator(lat_ticks)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'color': 'red'}
    gl.ylabel_style = {'color': 'red'}

    cbar = _make_colorbar(ax, img, orientation='horizontal')

    # Increase font size of colorbar tick labels
    plt.setp(cbar.ax.yaxis.get_ticklabels(), fontsize=10)

    cbar.set_label(cbar_label, fontsize = 10)

    # plt.tight_layout()    # Throws 'Tight layout not applied' warning, per usual

    # Adjust surrounding whitespace
    plt.subplots_adjust(left=0, bottom=0.05, right=1, top=0.95, wspace=0, hspace=0)

    if (plot_comms['save']):
        plt_fname = '{}-{}-{}.png'.format(sat_data['sector'], sat_data['product'], scan_date)
        print('     Saving figure as {}'.format(plt_fname))
        fig.savefig(join(plot_comms['outpath'], plt_fname), dpi=500)
    if (plot_comms['show']):
        plt.show()
    plt.close('all')



def plot_mercator2(data_dict, out_path):
    """
    Plot the GOES-16 data on a lambert-conformal projection map. Includes ABI
    imagery, GLM flash data, 100km, 200km, & 300km range rings, and red "+" at
    the center point

    Parameters
    ------------
    data_dict : dictionary
        Dictionary of data & metadata from GOES-16 ABI file


    Returns
    ------------
    A plot of the ABI data on a geostationary-projection map

    Notes
    -----
    - Uses georeference() and pcolormesh

    The projection x and y coordinates equals
    the scanning angle (in radians) multiplied by the satellite height
    (http://proj4.org/projections/geos.html)
    """
    scan_date = data_dict['scan_date']
    data = data_dict['data']

    globe = ccrs.Globe(semimajor_axis=data_dict['semimajor_ax'], semiminor_axis=data_dict['semiminor_ax'],
                       flattening=None, inverse_flattening=data_dict['inverse_flattening'])

    X, Y = georeference(data_dict['x'], data_dict['y'], data_dict['sat_lon'],
                        data_dict['sat_height'], sat_sweep = data_dict['sat_sweep'],
                        data=data_dict['data'])

    fig = plt.figure(figsize=(10, 5))

    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator(globe=globe))

    states = NaturalEarthFeature(category='cultural', scale='50m', facecolor='none',
                             name='admin_1_states_provinces_shp')

    ax.add_feature(states, linewidth=.8, edgecolor='black')
    #ax.coastlines(resolution='10m', color='black', linewidth=0.8)

    # TODO: For presentation sample, disable title and add it back in on ppt
    plt.title('GOES-16 Ch.' + str(data_dict['band_id']),
              fontweight='semibold', fontsize=10, loc='left')

    #cent_lat = float(center_coords[1])
    #cent_lon = float(center_coords[0])

    """
    lim_coords = geodesic_point_buffer(cent_lat, cent_lon, 400)
    lats = [float(x[1]) for x in lim_coords.coords[:]]
    lons = [float(x[0]) for x in lim_coords.coords[:]]

    min_lon = min(lons)
    max_lon = max(lons)

    min_lat = min(lats)
    max_lat = max(lats)

    ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
    """

#    ax.set_extent([lat_lon_extent['w'], lat_lon_extent['e'], lat_lon_extent['s'],
#                   lat_lon_extent['n']], crs=ccrs.PlateCarree())

    band = data_dict['band_id']
    if (band == 11 or band == 13):
        color = cm.binary
    else:
        color = cm.gray

    #color = cm.hsv
    # cmap hsv looks the coolest
    cmesh = plt.pcolormesh(X, Y, data, transform=ccrs.PlateCarree(), cmap=color)

    # Set lat & lon grid tick marks
    lon_ticks = [x for x in range(-180, 181) if x % 2 == 0]
    lat_ticks = [x for x in range(-90, 91) if x % 2 == 0]

    gl = ax.gridlines(crs=ccrs.PlateCarree(), linewidth=1, color='gray',
                      alpha=0.5, linestyle='--', draw_labels=True)
    gl.xlabels_top = False
    gl.ylabels_right=False
    gl.xlocator = mticker.FixedLocator(lon_ticks)
    gl.ylocator = mticker.FixedLocator(lat_ticks)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'color': 'red', 'weight': 'bold'}
    gl.ylabel_style = {'color': 'red', 'weight': 'bold'}

    cbar = plt.colorbar(cmesh,fraction=0.046, pad=0.04)

    # Increase font size of colorbar tick labels
    plt.setp(cbar.ax.yaxis.get_ticklabels(), fontsize=12)
    cbar.set_label('Radiance (' + data_dict['data_units'] + ')', fontsize = 14, labelpad = 20)

    plt.tight_layout()

    fig = plt.gcf()
    fig.set_size_inches((8.5, 11), forward=False)
    fig.savefig(join(out_path, scan_date.strftime('%Y'), scan_date.strftime('%Y%m%d-%H%M')) + '.png', dpi=500)

    #plt.show()
    plt.close(fig)



def subset_grid(extent, grid_Xs, grid_Ys):
    """
    Finds the ABI grid indexes corresponding to the given min & max lat and lon
    coords

    Parameters
    ----------
    extent : list of float
        List containing the min and max lat & lon coordinates
        Format: min_lat, max_lat, min_lon, max_lon
    grid_Xs : numpy 2D array
    grid_Ys : numpy 2D array

    Returns
    -------
    Tuple of floats
        Indices of the ABI grid corresponding to the min & max lat and lon coords
        Format: (min_y, max_y, min_x, max_x)
    """
    point1 = geod_to_scan(extent[0], extent[2]) # min lat & min lon
    point2 = geod_to_scan(extent[1], extent[3]) # max lat & max lon

    min_x = _find_nearest_idx(grid_Xs, point1[1])
    max_x = _find_nearest_idx(grid_Xs, point2[1])
    min_y = _find_nearest_idx(grid_Ys, point1[0])
    max_y = _find_nearest_idx(grid_Ys, point2[0])

    return (min_y, max_y, min_x, max_x)



def get_geospatial_extent(abs_path):
    """
    Gets the geospatial extent of the ABI data in the given file

    Parameters
    ----------
    abs_path : str
        Absolute path of the GOES-16 ABI file to be opened & processed

    Returns
    -------
    extent : dict of floats
        Keys: 'north, south, east, west, lat_center, lon_center'
    """
    extent = {}
    fh = Dataset(abs_path, mode='r')

    extent['north'] = fh.variables['geospatial_lat_lon_extent'].geospatial_northbound_latitude
    extent['south'] = fh.variables['geospatial_lat_lon_extent'].geospatial_southbound_latitude
    extent['east'] = fh.variables['geospatial_lat_lon_extent'].geospatial_eastbound_longitude
    extent['west'] = fh.variables['geospatial_lat_lon_extent'].geospatial_westbound_longitude
    extent['lat_center'] = fh.variables['geospatial_lat_lon_extent'].geospatial_lat_center
    extent['lon_center'] = fh.variables['geospatial_lat_lon_extent'].geospatial_lon_center
    fh.close() # Not really needed but good practice
    return extent



def plot_sammich_geos(visual, infrared):
    """
    Plots visual & infrared "sandwich" on a geostationary projection. The visual
    imagery provided cloud texture & structure details and the infrared provided
    cloud top temps

    Parameters
    ----------
    visual : dict
        Dictionary of visual satellite data returned by read_file(). Use band 2
    infrared : dict
        Dictionary of infrared satellite data returned by read_file(). Use band 13

    Notes
    -----
    - Uses imshow instead of pcolormesh
    - Passing the Globe object created with ABI metadata to the PlateCarree
      projection causes the shapefiles to not plot properly
    """
    sat_height = visual['sat_height']
    sat_lon = visual['sat_lon']
    sat_sweep = visual['sat_sweep']
    scan_date = visual['scan_date']

    # Taken care of in read_file_abi()
    # y_min, x_min = scan_to_geod(min(visual['y_image_bounds']), min(visual['x_image_bounds']))
    # y_max, x_max = scan_to_geod(max(visual['y_image_bounds']), max(visual['x_image_bounds']))

    globe = ccrs.Globe(semimajor_axis=visual['semimajor_ax'], semiminor_axis=visual['semiminor_ax'],
                       flattening=None, inverse_flattening=visual['inverse_flattening'])

    crs_geos = ccrs.Geostationary(central_longitude=sat_lon,
                                satellite_height=sat_height,false_easting=0,false_northing=0,
                                globe=globe, sweep_axis=sat_sweep)

    trans_pts = crs_geos.transform_points(ccrs.PlateCarree(), np.array([x_min, x_max]), np.array([y_min, y_max]))
    proj_extent = (min(trans_pts[0][0], trans_pts[1][0]), max(trans_pts[0][0], trans_pts[1][0]),
                   min(trans_pts[0][1], trans_pts[1][1]), max(trans_pts[0][1], trans_pts[1][1]))

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(1, 1, 1, projection=crs_geos)

    states = shpreader.Reader(STATES_PATH)
    states = list(states.geometries())
    states = cfeature.ShapelyFeature(states, ccrs.PlateCarree())

    counties = shpreader.Reader(COUNTIES_PATH)
    counties = list(counties.geometries())
    counties = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())

    #ax.set_extent(extent, crs=ccrs.PlateCarree())
    ax.add_feature(states, linewidth=.8, facecolor='none', edgecolor='gray', zorder=3)
    ax.add_feature(counties, linewidth=.3, facecolor='none', edgecolor='gray', zorder=3)

    # visual & infrared arrays are different dimensions
    # viz_img = plt.imshow(visual['data'], cmap=cm.binary_r, extent=extent,
    #                      vmin=visual['min_data_val'], vmax=visual['max_data_val'], zorder=1)
    viz_img = plt.imshow(visual['data'], cmap=cm.binary_r, vmin=visual['min_data_val'],
                         vmax=visual['max_data_val'], zorder=1, transform=crs_geos, extent=proj_extent)

    infrared_norm = colors.LogNorm(vmin=190, vmax=270)
    # inf_img = plt.imshow(infrared['data'], cmap=cm.nipy_spectral_r, norm=infrared_norm,
    #            extent=extent, zorder=2, alpha=0.4)
    inf_img = plt.imshow(infrared['data'], cmap=cm.nipy_spectral_r, norm=infrared_norm,
                         zorder=2, alpha=0.4, transform=crs_geos, extent=proj_extent)

    cbar_bounds = np.arange(190, 270, 10)
    cbar = plt.colorbar(inf_img, ticks=cbar_bounds, spacing='proportional')
    cbar.ax.set_yticklabels([str(x) for x in cbar_bounds])

    plt.title('GOES-16 Imagery', fontweight='semibold', fontsize=15)
    plt.title('%s' % scan_date.strftime('%H:%M UTC %d %B %Y'), loc='right')
    #ax.axis('equal')  # May cause shapefile to extent beyond borders of figure

    plt.show()



def plot_sammich_mercator(visual, infrared):
    """
    Plots visual & infrared "sandwich" on a Mercator projection. The visual
    imagery provided cloud texture & structure details and the infrared provided
    cloud top temps

    Parameters
    ----------
    visual : dict
        Dictionary of visual satellite data returned by read_file(). Use band 2
    infrared : dict
        Dictionary of infrared satellite data returned by read_file(). Use band 13

    Notes
    -----
    - Uses imshow instead of pcolormesh
    - Passing the Globe object created with ABI metadata to the PlateCarree
      projection causes the shapefiles to not plot properly
    """
    sat_height = visual['sat_height']
    sat_lon = visual['sat_lon']
    sat_sweep = visual['sat_sweep']
    scan_date = visual['scan_date']

    # Left, Right, Bottom, Top
    extent = [visual['lat_lon_extent']['w'], visual['lat_lon_extent']['e'],
              visual['lat_lon_extent']['s'], visual['lat_lon_extent']['n']]

    # Taken care of in read_file_abi()
    # y_min, x_min = scan_to_geod(min(visual['y_image_bounds']), min(visual['x_image_bounds']))
    # y_max, x_max = scan_to_geod(max(visual['y_image_bounds']), max(visual['x_image_bounds']))

    globe = ccrs.Globe(semimajor_axis=visual['semimajor_ax'], semiminor_axis=visual['semiminor_ax'],
                       flattening=None, inverse_flattening=visual['inverse_flattening'])

    crs_geos = ccrs.Geostationary(central_longitude=sat_lon, satellite_height=sat_height,
                                   false_easting=0, false_northing=0, globe=globe, sweep_axis=sat_sweep)

    crs_plt = ccrs.PlateCarree() # Globe keyword was messing everything up

    trans_pts = crs_geos.transform_points(crs_plt, np.array([x_min, x_max]), np.array([y_min, y_max]))

    proj_extent = (min(trans_pts[0][0], trans_pts[1][0]), max(trans_pts[0][0], trans_pts[1][0]),
                   min(trans_pts[0][1], trans_pts[1][1]), max(trans_pts[0][1], trans_pts[1][1]))

    ##################### Filter WWA polygons ######################
    # print('Processing state shapefiles...\n')
    # polys = _filter_polys(STATES_PATH, extent)
    # states = cfeature.ShapelyFeature(polys, ccrs.PlateCarree())
    #
    # print('Processing county shapefiles...\n')
    # polys = _filter_polys(COUNTIES_PATH, extent)
    # counties = cfeature.ShapelyFeature(polys, ccrs.PlateCarree())

    print('\nProcessing state shapefiles...\n')
    states = shpreader.Reader(STATES_PATH)
    states = list(states.geometries())
    states = cfeature.ShapelyFeature(states, crs_plt)

    print('Processing county shapefiles...\n')
    counties = shpreader.Reader(COUNTIES_PATH)
    counties = list(counties.geometries())
    counties = cfeature.ShapelyFeature(counties, crs_plt)
    ################################################################

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
    ax.set_extent(extent, crs=crs_plt)

    print('Creating map...\n')

    ax.add_feature(states, linewidth=.3, facecolor='none', edgecolor='black', zorder=3)
    ax.add_feature(counties, linewidth=.1, facecolor='none', edgecolor='black', zorder=3)

    viz_img = plt.imshow(visual['data'], cmap=cm.Greys_r, extent=proj_extent, origin='upper',
                         vmin=visual['min_data_val'], vmax=visual['max_data_val'],
                         zorder=1, transform=crs_geos, interpolation='none')

    infrared_norm = colors.LogNorm(vmin=190, vmax=270)
    custom_cmap = plotting_utils.custom_cmap()
    inf_img = plt.imshow(infrared['data'], cmap=custom_cmap, extent=proj_extent, origin='upper',
                         norm=infrared_norm, zorder=2, alpha=0.4, transform=crs_geos, interpolation='none')

    cbar_bounds = np.arange(190, 270, 10)
    cbar = plt.colorbar(inf_img, ticks=cbar_bounds, spacing='proportional')
    cbar.ax.set_yticklabels([str(x) for x in cbar_bounds])

    plt.title('GOES-16 Imagery', fontweight='semibold', fontsize=15)
    plt.title('%s' % scan_date.strftime('%H:%M UTC %d %B %Y'), loc='right')
    #ax.axis('equal')  # May cause shapefile to extent beyond borders of figure

    plt.show()



def _rad_to_ref(radiance, channel=2, correct=True):
    """
    Performs a linear conversion of spectral radiance to reflectance factor

    Parameters
    ----------
    radiance : numpy 2d array
        2D array of radiance values
        Units: mW / (m**2 sr cm**-1)
    correct : bool, optional
        If True, the reflectance array is gamma-corrected
    channel : int, optional
        ABI channel pertaining to the radiance data. Default: 2

    Returns
    -------
    ref : numpy 2D array
        2D array of reflectance values with the same dimensions as 'radiance'
    """
    constants = {1: 726.721072, 2: 663.274497, 3: 441.868715}
    d2 = 0.3

    if (channel not in constants.keys()):
        raise ValueError('Invalid ABI channel')

    ref = (radiance * np.pi / d2) / constants[channel]

    # Ensure the data is nominal
    ref = np.maximum(ref, 0.0)
    ref = np.minimum(ref, 1.0)

    if (correct):
        ref = _gamma_corr(ref)

    return ref



def _gamma_corr(ref):
    """
    Adjusts the reflectance array. Results in a brighter image when plotted

    Parameters
    ----------
    ref : numpy 2d array
        2D array of reflectance

    Returns
    -------
    gamma_ref : numpy 2d array
        2D array of gamma-corrected reflectance values
    """
    gamma_ref = np.sqrt(ref)
    return gamma_ref



def _k_2_c(data):
    """
    Converts input from degrees Kelvin to degrees Celsius

    Parameters
    ----------
    data : int, float, or numpy array
        Temperature to be converted from kelvin to celsius

    Returns
    -------
    float or numpy array
        Input parameter in degrees celsius
    """
    return (data - 273.15)



def _find_nearest_idx(array, value):
    """
    Helper function called in subset_grid(). Finds the index of the array element
    with the value closest to the parameter value

    Parameters
    ----------
    array : Numpy array
        Array to search for the nearest value
    value : int or float
        Value to search the array for
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx



def _make_colorbar(ax, mappable, **kwargs):
    """
    Create a custom colorbar because cartopy doesn't like to cooperate
    """
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    import matplotlib as mpl

    divider = make_axes_locatable(ax)
    orientation = kwargs.pop('orientation', 'vertical')
    if (orientation == 'vertical'):
        loc = 'right'
    elif (orientation == 'horizontal'):
        loc = 'bottom'

    cax = divider.append_axes(loc, '5%', pad='3%', axes_class=mpl.pyplot.Axes)
    cbar = ax.get_figure().colorbar(mappable, cax=cax, orientation=orientation)
    return cbar