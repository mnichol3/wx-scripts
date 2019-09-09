"""
Author: Matt Nicholson

This file contains functions to ingest, process, and plot NOAA National Data Buoy
Center (NDBC) buoy data. For more information on the data, see
https://www.ndbc.noaa.gov
"""
import pandas as pd
from os.path import isfile, join
import datetime
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from sys import exit

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

    Dependencies
    ------------
    > os.path.isfile
    > pandas
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

    # Replace the original year, month, day, hr, & minute columns with a single
    # date-time column
    buoy_df = _format_df_time(buoy_df)

    # Reverse the order of the rows so time increases with depth
    # (i.e. newest data will be at the bottom). Makes for easier plotting
    buoy_df = buoy_df.iloc[::-1]

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

    Dependencies
    ------------
    > pandas
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



def replace_na_vals(df, val):
    """
    Replace the missing values with the value passed as "val"

    Parameters
    ----------
    df : Pandas DataFrame
    val : int, str, etc

    Returns
    -------
    new_df : Pandas DataFrame
        Copy of input df, but with missing values replaces

    Example
    -------
    replace_na_vals(df, np.nan) with replace the missing data values ('MM')
    with np.nan
    """
    new_df = df.replace('MM', val)
    return new_df



def subset_time(df, start, end):
    """
    Select a temporal subset from the buoy data

    Parameters
    ----------
    df : Pandas DataFrame
        DataFrame containing the buoy data. See ingest() docstring for
        column names and descriptions
    start : str
        Date & time that defines the beginning of the temporal subset
        Format: DDMMYY-HHMM (Time is in universal time coordinates)
    end : str
        Date & time that defines the end of the temporal subset
        Format: DDMMYY-HHMM (Time is in universal time coordinates)

    Returns
    -------
    subset : Pandas DataFrame
        DataFrame containing data for the temporal subset defined by the 'start'
        and 'end' parameters. Column names are the same as the input DataFrame

    Dependencies
    ------------
    > datetime
    """
    temp_subset = _datetime_range(start, end)

    subset = df.loc[df['dt'].isin(temp_subset)]
    return subset



################################################################################
############################## Plotting Functions ##############################
################################################################################

def plot_pressure(df, buoy_no):
    """
    Plot atmospheric pressure vs time

    Parameters
    ----------
    df : Pandas DataFrame
        DataFrame containing the buoy data
    buoy_no : str
        NDBC buoy number for use in the title
    """

    # Replace any missing data values ("MM") with Numpy.NaN so the plotting
    # function can handle them
    filtered_df = replace_na_vals(df, np.NaN)

    del df

    first_dt = filtered_df['dt'].iloc[0]
    last_dt = filtered_df['dt'].iloc[-1]

    x_ticks = _calc_x_ticks(filtered_df['dt'].tolist())
    x_tick_labels = ['{}/{}\n{}'.format(x[4:6], x[6:8], x.split('-')[1]) for x in x_ticks]

    fig, ax = plt.subplots()
    ax.plot(filtered_df['dt'].tolist(), [float(x) for x in filtered_df['pres'].tolist()])

    ax.set(xlabel='Date & Time (UTC)', ylabel='Pressure (hPa)',
           title='NDBC Station {} Atmospheric Pressure {}z - {}z'.format(buoy_no, first_dt, last_dt))

    plt.xticks(ticks=x_ticks,fontsize=10)
    ax.set_xticklabels(x_tick_labels)

    ax.grid()
    plt.tight_layout()
    plt.show()



def plot_pressure_wind(df, buoy_no):
    """
    Plot atmospheric pressure vs time and wind speed vs time

    Parameters
    ----------
    df : Pandas DataFrame
        DataFrame containing the buoy data
    buoy_no : str
        NDBC buoy number for use in the title
    """

    # Replace any missing data values ("MM") with Numpy.NaN so the plotting
    # function can handle them
    filtered_df = replace_na_vals(df, np.NaN)

    del df

    first_dt = filtered_df['dt'].iloc[0]
    last_dt = filtered_df['dt'].iloc[-1]

    x_ticks = _calc_x_ticks(filtered_df['dt'].tolist())
    x_tick_labels = ['{}/{}\n{}'.format(x[4:6], x[6:8], x.split('-')[1]) for x in x_ticks]

    fig, ax1 = plt.subplots()
    color = 'tab:red'
    ax1.plot(filtered_df['dt'].tolist(), [float(x) for x in filtered_df['pres'].tolist()],
             color=color)
    ax1.set_xlabel('Date & Time (UTC)')
    ax1.set_ylabel('Pressure (hPa)', color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    plt.xticks(ticks=x_ticks,fontsize=10)
    ax1.set_xticklabels(x_tick_labels)

    # Clone the axis and plot wind speed on it

    ax2 = ax1.twinx()

    color = 'tab:blue'
    ax2.set_ylabel('Wind Speed (m/s)', color=color)
    ax2.plot(filtered_df['dt'].tolist(), [float(x) for x in filtered_df['wspd'].tolist()],
             color=color)

    ax2.tick_params(axis='y', labelcolor=color)
    plt.xticks(ticks=x_ticks,fontsize=10)
    ax2.set_xticklabels(x_tick_labels)

    ax1.grid()
    plt.title('NDBC Station {} Atmospheric Pressure & Wind Speed {}z - {}z'.format(buoy_no, first_dt, last_dt))
    # plt.tight_layout()
    plt.show()



################################################################################
############################### Helper Functions ###############################
################################################################################



def _calc_x_ticks(datetimes):
    ticks = [x for x in datetimes if ((x[-2:] == '00') and (int(x[-4:]) % 3 == 0))]
    return ticks



def _format_df_time(df):
    """
    Format a buoy DataFrame's time and combine into one column

    Parameters
    ----------
    df : Pandas DataFrame

    Returns
    -------
    new_df : Pandas DataFrame
        DataFrame with 'yr', 'mon', 'day', 'hr', & 'min' columns replaced by
        'date'

    Dependencies
    ------------
    > pandas
    > datetime
    """
    datetimes = []
    for idx, yr in enumerate(df['yr'].tolist()):
        curr_row = df.iloc[idx]
        curr_dt = '{}{}{}-{}{}'.format(curr_row['yr'], curr_row['mon'],
                                       curr_row['day'], curr_row['hr'],
                                       curr_row['min'])
        curr_dt = datetime.datetime.strptime(curr_dt, "%Y%m%d-%H%M")
        curr_dt = datetime.datetime.strftime(curr_dt, "%Y%m%d-%H%M")
        datetimes.append(curr_dt)

    # datetimes = np.array(datetimes)

    # Remove the yr, mon, day, hr, & min columns as we dont need them anymore
    new_df = df.drop(['yr', 'mon', 'day', 'hr', 'min'], axis=1)

    # Add the new datetime list as a column. Will be added as the last colunmn
    new_df['dt'] = datetimes

    # Reorder the columns so that ['dt'] is on the left to increase readability
    cols = new_df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    new_df = new_df[cols]

    return new_df



def _datetime_range(start, end):
    """
    Creates a range of datetime objects for the period defined by start & end
    """
    start_dt = datetime.datetime.strptime(start, "%Y%m%d-%H%M")
    end_dt = datetime.datetime.strptime(end, "%Y%m%d-%H%M")

    diff = (end_dt + datetime.timedelta(minutes = 10)) - start_dt

    datetimes = []
    for x in range(int(diff.total_seconds() / 600)):
        curr_dt = start_dt + datetime.timedelta(minutes = x*10)
        datetimes.append(datetime.datetime.strftime(curr_dt, "%Y%m%d-%H%M"))

    return datetimes



def main():
    base_path = '/media/mnichol3/tsb1/data/storms/2019-dorian'
    fname = '41025_5day.txt'
    buoy_no = '41025'
    abs_path = join(base_path, fname)

    # Raw buoy data df
    buoy_df = ingest(abs_path)
    buoy_df = replace_na_vals(buoy_df, np.NaN)
    # print(buoy_df)
    # exit(0)

    # Get the temporal subset we're interested in
    buoy_df = subset_time(buoy_df, '20190905-0000', '20190908-0000')
    
    # plot_pressure(buoy_df, buoy_no)
    plot_pressure_wind(buoy_df, buoy_no)



if __name__ == '__main__':
    main()
