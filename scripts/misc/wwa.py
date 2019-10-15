"""
Author: Matt Nicholson

This file holds functions dedicated to processing and plotting National Weather
Service watch & warning polygons
"""
import datetime
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from os.path import join
import numpy as np


def get_wwa_polys(abs_path, date, time, wwa_type=['SV', 'TO']):
    """
    Gets NWS WWA polygons for a specified date & time

    Parameters
    ----------
    abs_path : str
        Absolute path of the WWA shapefile
    date : str
        Format: MMDDYYYY
    time : str
        Format: HHMM
    wwa_type : list of str, optional
        Types of warnings to get. Default: SV (Severe Thunderstorm) & TO (Tornado)

    Returns
    -------
    polys : dict; key : str, value : polygon

    Dependencies
    ------------
    > cartopy.io.shapereader
    > _valid_wwa_time()
    > _format_wwa_time()

    Notes
    -----
    Native shapefile datetime format: 201905232120
    WWA shapefile download link:
        http://mesonet.agron.iastate.edu/request/gis/watchwarn.phtml
    WWA shapefile docs:
        http://mesonet.agron.iastate.edu/info/datasets/vtec.html
    """
    polys = {}
    target_dt = _format_wwa_time(date, time)
    wwa_reader = shpreader.Reader(abs_path)

    if ('SV' in wwa_type):
        filtered_wwa_sv = [rec.geometry for rec in wwa_reader.records() if (rec.attributes['GTYPE'] == 'P')
                        and (_valid_wwa_time(rec.attributes['ISSUED'], rec.attributes['EXPIRED'], target_dt))
                        and (rec.attributes['PHENOM'] == 'SV')]
        polys['SV'] = filtered_wwa_sv
    if ('TO' in wwa_type):
        filtered_wwa_to = [rec.geometry for rec in wwa_reader.records() if (rec.attributes['GTYPE'] == 'P')
                        and (_valid_wwa_time(rec.attributes['ISSUED'], rec.attributes['EXPIRED'], target_dt))
                        and (rec.attributes['PHENOM'] == 'TO')]
        polys['TO'] = filtered_wwa_sv
    return polys



def get_wwa_polys2(abs_path, start, end, wwa_type=['SV', 'TO']):
    """
    Gets NWS WWA polygons active between a specified start date & time and
    end date & time

    Parameters
    ----------
    abs_path : str
        Absolute path of the WWA shapefile
    start : str
        Format: MMDDYYYY-HHMM
    end : str
        Format: MMDDYYYY-HHMM
    wwa_type : list of str, optional
        Types of warnings to get. Default: SV (Severe Thunderstorm) & TO (Tornado)

    Returns
    -------
    polys : dict; key : str, value : polygon

    Dependencies
    ------------
    > cartopy.io.shapereader
    > _valid_wwa_time()
    > _format_wwa_time()

    Notes
    -----
    Native shapefile datetime format: 201905232120
    WWA shapefile download link:
        http://mesonet.agron.iastate.edu/request/gis/watchwarn.phtml
    WWA shapefile docs:
        http://mesonet.agron.iastate.edu/info/datasets/vtec.html
    """
    polys = {}
    start_dt = _format_wwa_time2(start)
    end_dt = _format_wwa_time2(end)
    wwa_reader = shpreader.Reader(abs_path)

    #### debug ####
    # for rec in wwa_reader.records():
    #     print(rec.attributes)
    #     print('\n')

    if ('SV' in wwa_type):
        filtered_wwa_sv = [rec.geometry for rec in wwa_reader.records() if (rec.attributes['GTYPE'] == 'P')
                        and (_valid_wwa_time2(rec.attributes['ISSUED'], start_dt, end_dt))
                        and (rec.attributes['PHENOM'] == 'SV')]
        polys['SV'] = filtered_wwa_sv
    if ('TO' in wwa_type):
        filtered_wwa_to = [rec.geometry for rec in wwa_reader.records() if (rec.attributes['GTYPE'] == 'P')
                        and (_valid_wwa_time2(rec.attributes['ISSUED'], start_dt, end_dt))
                        and (rec.attributes['PHENOM'] == 'TO')]
        polys['TO'] = filtered_wwa_to
    return polys



def plot_wwa_polys(extent, outpath, start, end, save=False, show=True):
    """
    Plot WWA polygons on a simple map

    Parameters
    ----------
    extent : list
        Geographic extent of the plot.
        Format: [min_lat, max_lat, min_lon, max_lon]
    outpath : str
        Absolute path of the directory to save the plot to
    start : str
        Start date & time of accumulated WWA polygons
        Format: MMDDYYY-HHMM
    end : str
        end date & time of accumulated WWA polygons
        Format: MMDDYYY-HHMM

    Returns
    -------
    None

    Dependencies
    ------------
    > matplotlib
    > pyplot
    > cartopy.ccrs
    > cartopy.feature
    > sys.path.join
    """
    z_ord = {'wwa': 2, 'map': 1, 'base': 0}
    plt_extent = [extent[2], extent[3], extent[0], extent[1]]

    county_path = '/media/mnichol3/tsb1/data/gis/nws_c_02ap19/c_02ap19.shp'
    state_path = '/media/mnichol3/tsb1/data/gis/nws_s_11au16/s_11au16.shp'

    crs_plt = ccrs.PlateCarree()

    fig = plt.figure(figsize=(12, 8))

    ax = fig.add_subplot(111, projection=ccrs.Mercator())

    # Set axis background color to black
    ax.imshow(
        np.tile(
            np.array(
                [[[0, 0, 0]]], dtype=np.uint8),
            [2, 2, 1]),
        origin='upper', transform=crs_plt, extent=[-180, 180, -180, 180]
    )

    counties = shpreader.Reader(county_path)
    counties = list(counties.geometries())
    counties = cfeature.ShapelyFeature(counties, crs_plt)

    states = shpreader.Reader(state_path)
    states = list(states.geometries())
    states = cfeature.ShapelyFeature(states, crs_plt)

    ax.add_feature(states, linewidth=.8, facecolor='black',
                   edgecolor='gray', zorder=z_ord['map'])
    ax.add_feature(counties, facecolor='none', linewidth=.2, edgecolor='gray',
                   zorder=z_ord['map'])
    ax.set_extent(plt_extent, crs=crs_plt)

    wwa_keys = wwa_polys.keys()

    if ('SV' in wwa_keys):
        sv_polys = cfeature.ShapelyFeature(wwa_polys['SV'], crs_plt)
        ax.add_feature(sv_polys, linewidth=.8, facecolor='none', edgecolor='yellow', zorder=z_ord['wwa'])
    if ('TO' in wwa_keys):
        to_polys = cfeature.ShapelyFeature(wwa_polys['TO'], crs_plt)
        ax.add_feature(to_polys, linewidth=.8, facecolor='none', edgecolor='red', zorder=z_ord['wwa'])

    plt.title('NWS Tornado Warnings - {}z to {}z'.format(start, end),
              loc='right',
              fontsize=12)

    plt.gca().set_aspect('equal', adjustable='box')

    # Try to cut down on whitespace surrounding the actual plot
    plt.subplots_adjust(left=0, bottom=0.05, right=1, top=0.95, wspace=0, hspace=0)
    
    if (save):
        if (outpath is not None):
            fname = 'WWAplot - {}z to {}z.png'.format(start, end)
            path = join(outpath, fname)
            plt.savefig(path, dpi=600)
        else:
            raise ValueError('Error: Outpath cannot be None')
    if (show):
        plt.show()
    plt.close('all')


def _valid_wwa_time(issued, expired, target):
    target = int(target)
    expired = int(expired)
    issued = int(issued)
    return (target >= issued and target <= expired)



def _valid_wwa_time2(issued, start, end):
    start = int(start)
    end = int(end)
    issued = int(issued)
    return (end >= issued and start <= issued)




def _format_wwa_time(date, time):
    """
    Formats a datetime string to filter WWA polygons

    Parameters
    ----------
    date : str
        Format: MMDDYYYY
    time : str
        Format: HHMM

    Returns
    -------
    str
        WWA polygon datetime
        Format: YYYYMMDDHHMM

    Dependencies
    ------------
    datetime
    """
    dt = datetime.datetime.strptime(date + time,'%m%d%Y%H%M')
    return datetime.datetime.strftime(dt, '%Y%m%d%H%M')



def _format_wwa_time2(date_time):
    """
    Formats a datetime string to filter WWA polygons

    Parameters
    ----------
    date_time : str
        Format: MMDDYYYY-HHMM

    Returns
    -------
    str
        WWA polygon datetime
        Format: YYYYMMDDHHMM

    Dependencies
    ------------
    datetime
    """
    dt = datetime.datetime.strptime(date_time,'%m%d%Y-%H%M')
    return datetime.datetime.strftime(dt, '%Y%m%d%H%M')




start = '09052019-0000'
end = '09052019-1430'
extent = [31.72, 36.64, -83.04, -74.71]
outpath = '/home/mnichol3/Coding/wx-scripts/misc'
poly_path = '/home/mnichol3/Downloads/wwa_201909050000_201909051430/wwa_201909050000_201909051430.shp'
wwa_polys = get_wwa_polys2(poly_path, start, end)
plot_wwa_polys(extent, outpath, start, end, save=True, show=False)
# plot_wwa_polys(extent, outpath, start, end)
