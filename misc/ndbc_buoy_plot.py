import pandas as pd
from os.path import isfile, join


def ingest(fname):
    """
    Takes the absolute path of a NDBC buoy data file and returns a pandas df

    Parameters
    ----------
    fname : str
        Absolute path, including the filename, of the NDBC buoy data file to open

    Returns
    -------
    buoy_df : pandas dataframe
        Dataframe containing the buoy data. Default dtype = str
        Column names:
            'yr'    : Year of the observation
            'mon'   : Month of the observation
            'day'   : Day of the observation
            'hr'    : Hour of the observation
            'min'   : Minute of the observation
            'wdir'  : Wind direction (the direction the wind is coming from in
                      degrees clockwise from true North)
            'wspd'  : Wind speed (m/s) averaged over an eight-minute period
            'wgst'  : Peak 8 second gust speed (m/s) measured during the eight-minute
                      period
            'wvht'  : Significant wave height (meters) is calculated as the average
                      of the highest one-third of all wave heights during the
                      20-minute sampling period
            'dpd'   : Dominant wave period (seconds) is the period with the maximum
                      wave energy
            'apd'   : Average wave period (seconds) of all waves during the 20-minute
                      sampling period
            'mwd'   : The direction from which the waves at the dominant period (DPD)
                      are coming. Units are degrees from true North, increasing clockwise,
                      with North as 0 (zero) degrees and East as 90 degrees
            'pres'  : Sea level pressure (hPa)
            'atmp'  : Air temperature (Celsius)
            'wtmp'  : Sea surface temperature (Celsius)
            'dewp'  : Dewpoint temperature (Celsius) taken at the same height as
                      the air temperature measurement
            'vis'   : Station visibility (nautical miles). Buoy stations are limited
                      to reports from 0 to 1.6 nmi
            'ptdy'  : Pressure tendency is the direction (plus or minus) and the
                      amount of pressure change (hPa) for a three hour period
                      ending at the time of the observation
            'tide'  : The water level in feet above or below Mean Lower Low Water

        For a full explaination of the Standard Meteorological Data fields,
        see http://ndbc.noaa.gov/measdes.shtml
    """
    # Validate the absolute path
    if (not isfile(fname)):
        raise FileNotFoundError('File does not exist')

    col_names = ['yr', 'mon', 'day', 'hr', 'min', 'wdir', 'wspd', 'wgst', 'wvht',
                 'dpd', 'apd', 'mwd', 'pres', 'atmp', 'wtmp', 'dewp', 'vis', 'ptdy',
                 'tide']

    # Call read_csv using python engine since the C engine cannot handle regex
    # separators
    buoy_df = pd.read_csv(fname, sep=r'\s{1,6}', names=col_names, dtype=str,
                          skiprows=[0,1], na_values='MM', engine='python')

    return buoy_df



def filter_na_vals(df, fields):
    """
    Remove rows containing NaN values for specified data fields

    Parameters
    ----------
    df : pandas dataframe
        Pandas dataframe containing NDBC buoy data. See ingest() docstring for
        column names and descriptions
    fields : str or list of str
        Fields (columns) to remove if they contain NaN values. "any" drops
        all rows containing NaN for any column value

    Returns
    -------
    filtered_df : pandas dataframe
        Pandas dataframe with the rows containing NaN values for the specified
        fields removed
    """
    # Validate df param
    if (not isinstance(df, pd.DataFrame)):
        raise TypeError("'df' parameter must be a Pandas DataFrame, not {}".format(type(df)))

    # Validate fields param
    if (type(fields) == str):
        if (fields == 'all'):
            filtered_df = df.dropna(how='any')
            if (filtered_df.empty):
                # If removing rows where any field is NaN results in an empty
                # DataFrame (which is likely given the varying temporal resolutions
                # of the obs), print a warning
                print('Warning: All NaN removed, resulting DataFrame is empty')
        else:
            fields = [fields]
            filtered_df = df.dropna(subset=fields)
    elif (type(fields) == list):
        filtered_df = df.dropna(subset=fields)
    else:
        raise TypeError("'fields' parameter must be a str or list, not {}".format(type(fields)))

    return filtered_df



base_path = '/media/mnichol3/tsb1/data/storms/2019-dorian'
fname = '41025_5day.txt'
abs_path = join(base_path, fname)
buoy_df = ingest(abs_path)
print(buoy_df.shape)
filtered_df = filter_na_vals(buoy_df, 'all')
