"""
01 Mar 2019
Author: Matt Nicholson

"""
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature
import pandas as pd


ASOS_DATA_PATH = '/home/mnichol3/Coding/wx-scripts/aosc472-LESN/data/asos.txt'


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
    col_names = ['station', 'valid', 'lon', 'lat', 'tmpf', 'dwpf', 'relh', 'drct',
                'sknt', 'alti', 'mslp', 'p01i', 'vsby', 'gust', 'skyl1', 'skyl2',
                'skyl3', 'wxcodes']

    stations = get_asos_stations(asos_df)

    for stn in stations:
        temp_df = asos_df.loc[(asos_df.station == stn), col_names]
        asos_staion_dict[stn] = temp_df

    return asos_staion_dict



def main():
    asos = read_data(ASOS_DATA_PATH)
    #print(get_asos_stations(asos))
    #print(get_date_range(asos))
    asos = sort_df(asos)
    #df_to_csv(asos, 'asos-df-sorted.csv') # It works!!
    #print(df_by_station(asos)['ROC']) # It works!!

if (__name__ == "__main__"):
    main()
