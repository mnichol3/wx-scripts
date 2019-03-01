"""
01 Mar 2019
Author: Matt Nicholson

"""
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math


ASOS_DATA_PATH = '/home/mnichol3/Coding/wx-scripts/aosc472-LESN/data/asos.txt'
COL_NAMES = ['station', 'valid', 'lon', 'lat', 'tmpf', 'dwpf', 'relh', 'drct',
            'sknt', 'alti', 'mslp', 'p01i', 'vsby', 'gust', 'skyl1', 'skyl2',
            'skyl3', 'wxcodes']


def read_data(fname, debug=True):
    """
    Reads the ASOS data file into a pandas dataframe with values being stored
    as strings. Returns the new dataframe.

    Parameters
    ----------
    fname : str
        Name of the ASOS file to be opened & read
    debug : bool
        Indicates if 5 debug rows are included at the beginning of the file. If
        they are, they are skipped when reading the data from the file


    Returns
    -------
    asos_df : Pandas dataframe
        Dataframe containing the data from the ASOS txt file. Data are stored as
        strings
    """

    if (debug):
        asos_df = pd.read_csv(ASOS_DATA_PATH, sep=",", header=0, dtype=str, skiprows=5)
    else:
        asos_df = pd.read_csv(ASOS_DATA_PATH, sep=",", header=0, dtype=str)

    return asos_df



def get_asos_stations(asos_df):
    """
    Takes a dataframe containing ASOS data and returns a list of ASOS stations
    included in the dataframe

    Parameters
    ----------
    asos_df : Pandas Dataframe
        Dataframe containing the data from the ASOS txt file. Data are stored as
        strings


    Returns
    -------
    asos_stations : list of str
        List of the ASOS stations in asos_df
    """
    stations = asos_df.station.unique()

    return stations



def get_date_range(asos_df):
    """
    Gets the date range of observations in the ASOS dataframe

    Parameters
    ----------
    asos_df : Pandas Dataframe
        Dataframe containing the data from the ASOS txt file. Data are stored as
        strings


    Returns
    -------
    Tuple of str
        Tuple of str, the first element being the start date & time, the second
        being the end date & time. Format: YYYY-MM-DD HH:MM
    """
    s_date = asos_df.iloc[0][1]
    e_date = asos_df.iloc[-1][1]

    return (s_date, e_date)



def sort_df(asos_df):
    """
    Sorts an ASOS dataframe first by station name, then by date & time

    Parameters
    ----------
    asos_df : Pandas dataframe
        Dataframe containing the data from the ASOS txt file. Data are stored as
        strings


    Returns
    -------
    sorted_df : Pandas dataframe
        Dataframe containing the data from the ASOS txt file, sorted in ascending
        order first by station name, then by obs date & time. Data are stored as
        strings
    """
    sorted_df = asos_df.sort_values(by=['station', 'valid'])

    return sorted_df



def df_to_csv(asos_df, fname):
    """
    Writes an ASOS dataframe to a csv file, with the filename given by the
    fname parameter. Elements are comma-delimited and lines are terminated by
    whataver newline character or character sequence the OS uses

    Parameters
    ----------
    asos_df : Pandas dataframe
        Dataframe containing the data from the ASOS txt file. Data are stored as
        strings
    fname : str
        Desired name of the csv file. May include path


    Returns
    -------
    None
    """
    if (fname[-4:] != '.csv'):
        fname = fname + '.csv'

    asos_df.to_csv(fname, sep=',', index=False, header=True)



def df_by_station(asos_df):
    """
    Creates dataframes containing data from a respective site. Returns a dictionary
    where the key is the station name and the value is that station's ASOS
    observation dataframe

    Parameters
    ----------
    asos_df : Pandas dataframe
        Dataframe containing the data from the ASOS txt file. Data are stored as
        strings. Dataframe is preferably sorted, though it shouldn't really matter


    Returns
    -------
    asos_staion_dict : Dictionary; key : str, val : Pandas dataframe
        Dictionary, where each key is a string containing the name of an ASOS
        station and the value is a dataframe containing that station's ASOS
        observation data
    """
    asos_staion_dict = {}

    stations = get_asos_stations(asos_df)

    for stn in stations:
        temp_df = asos_df.loc[(asos_df.station == stn), COL_NAMES]
        asos_staion_dict[stn] = temp_df

    return asos_staion_dict



def plot_temp(station, station_df):
    """
    Plots the temperature & dewpoint for a specific station

    Parameters
    ----------
    station : str
        3-letter ASOS station ID
    station_df : Pandas dataframe
        Dataframe containing ASOS observations taken at the argument ASOS station


    Returns
    -------
    None, displays a plot
    """
    # Filter the station dataframe for rows with valid temp & dewpoint values
    valid_data = station_df.loc[(station_df.tmpf != 'M') & (station_df.dwpf != 'M'), COL_NAMES]

    times = valid_data['valid'].tolist()

    temp = valid_data['tmpf'].tolist()
    temp = [float(x) for x in temp]

    dewp = valid_data['dwpf'].tolist()
    dewp = [float(y) for y in dewp]

    s_time = times[0]
    e_time = times[-1]

    plt.plot(times, temp, label = 'Temp')
    plt.plot(times, dewp, label = 'Dewpoint')

    plt.legend(['Temp', 'DewP'])
    plt.xlabel('Date & time')
    plt.ylabel('Temp (f)')

    if (tick_freq == 0):
        x_tick_freq = 6
    else:
        x_tick_freq = tick_freq

    plt.xticks(times[::x_tick_freq], np.array(times)[::x_tick_freq], rotation=60, ha='right')

    plt.title(station + ' Temp & Dewpoint from ' + s_time + ' to ' + e_time)
    plt.tight_layout()
    plt.show()



def plot_wind(station, station_df, tick_freq=0):
    """
    Plots wind speed for a specific station

    Parameters
    ----------
    station : str
        3-letter ASOS station ID
    station_df : Pandas dataframe
        Dataframe containing ASOS observations taken at the argument ASOS station


    Returns
    -------
    None, displays a plot
    """

    valid_data = station_df.loc[(station_df.drct != 'M') & (station_df.sknt != 'M'), COL_NAMES]

    times = valid_data['valid'].tolist()

    w_dir = valid_data['drct'].tolist()
    w_dir = [float(x) for x in w_dir]

    w_spd = valid_data['sknt'].tolist()
    w_spd = [float(y) for y in w_spd]

    u = [0] * len(times)
    v = [0] * len(times)

    for idx, n in enumerate(w_spd):
        u[idx] = n * math.sin(math.radians(w_dir[idx]))
        v[idx] = n * math.cos(math.radians(w_dir[idx]))

    s_time = times[0]
    e_time = times[-1]

    #plt.plot(times, temp, label = 'Temp')
    #plt.plot(times, dewp, label = 'Dewpoint')

    #plt.legend(['Temp', 'DewP'])
    plt.barbs(times, w_spd, u, v, w_spd, length=6, pivot='tip')
    #plt.xlabel('Date & time')
    plt.ylabel('Wind Speed (kts)')

    if (tick_freq == 0):
        x_tick_freq = 6
    else:
        x_tick_freq = tick_freq

    plt.xticks(times[::x_tick_freq], np.array(times)[::x_tick_freq], rotation=60, ha='right')

    plt.title(station + ' Wind Speed & Dir from ' + s_time + ' to ' + e_time)
    plt.tight_layout()
    plt.show()



def main():
    asos = read_data(ASOS_DATA_PATH)
    asos = sort_df(asos)
    df_dict = df_by_station(asos) # It works!!
    #print(df_dict['BUF'])
    #plot_temp('ROC', df_dict['ROC'])
    plot_wind('ROC', df_dict['ROC'], 15)

if (__name__ == "__main__"):
    main()
