"""
Author: Matt Nicholson

This file contains files to access & parse High-Density/High-Accuracy Observations
(HDOBs) from NOAA & USAF weather reconassaince aircraft
"""
import pandas as pd
from datetime import datetime, timedelta
from os.path import isfile

class HDOBFile(object):
    """
    A class to represent a single HDBO file

    Object attributes
    ------------------
    mission_id : str
        Includes callsign, something else, and storm name
        Ex: AF304 3005A DORIAN
    obs_num : str
        Observation number (01-99), assigned sequentially for each HDOB
        message during the flight. This sequence is independent of the numbering
        of the numbering of other types of observations (RECCO, DROP, VORTEX, etc),
        which each have their own numbering sequence
    obs_date : str
        Year, month, and day of the first data line of the message
    data_first_dt : str
        Datetime of the first data line of the message
    data_last_dt : str
        Datetime of the last data line of the message
    data : Pandas DataFrame
    """

    def __init__(self, mission_header, data):
        """
        Construct an HDOBFile object

        Parameters
        -----------
        mission_header : str
            2nd line of text in the HDBO file
            Ex: AF304 3005A DORIAN        HDOB 51 20190902
        data : Pandas DataFrame
        """
        super(HDOBFile, self).__init__()

        self.aircraft_callsign, self.mission_id, self.storm_name, \
        self.obs_num, self.obs_date = self._parse_mission_meta(mission_header)

        self.obs_time_first, self.obs_time_last = self._pasrse_data_start_end(data)
        self.data = data


    def _parse_mission_meta(self, mission_header):
        """
        Extract the aircraft callsign, mission id, obs number, and date of the
        first data line from the file header

        Parameters
        ----------
        mission_header : str
            2nd line of text in the HDBO file
            Ex: AF304 3005A DORIAN        HDOB 51 20190902

        Returns
        --------
        tuple of str
            Format: (aircraft callsign, mission id, storm name, obs num, first data date)
        """
        meta = [x for x in mission_header.split(' ') if x != '']
        if ('HDOB' not in meta):
            raise ValueError('Attempting to parse an obs that is not an HDOB')

        return (meta[0], meta[1], meta[2], meta[4], meta[5])



    def _pasrse_data_start_end(self, data):
        """
        Get the times that the first & last observations in the file were taken

        Parameters
        ----------
        data : Pandas DataFrame

        Return
        -------
        tuple of str
            Format: (first, last)
        """
        first = data['obs_time'].iloc[0]
        last = data['obs_time'].iloc[-1]

        return (first, last)



    def __repr__(self):
        return '<HDOBFile object - {} {} {}-{}z {}>'.format(self.storm_name, self.obs_date,
                        self.obs_time_first, self.obs_time_last, self.aircraft_callsign)



def get_hdob_fnames(date=None, start=None, end=None, octant='AHONT1'):
    """
    Fetches NOAA & USAF aircraft observation files published on the given date,
    or during the time period defined by start & end. Returns a dictionary
    containing a list of NOAA HDOB filenames and a list of USAF HDOB filenames

    Parameters
    ------------
    date : str, optional
        Desired date of the aircraft obs. Format: YYYYMMDD
    start : str, optional
        Date & time that defines the beginning of the desired time period
        Format: YYYYMMDD-HHMM (UTC)
    end : str, optional
        Date & time that defines the end of the desired time period. Must be
        given if 'start' is given
        Format: YYYYMMDD-HHMM (UTC)
    octant : str, optional
        Octant code indicating where the observation was taken. Default is 'AHONT1'
        (Atlantic Basin)

    Returns
    ------------
    fname_dict : dictionary; keys : str, values : list of str
        A dictionary containing a list of NOAA aircraft observations and a list
        of USAF aircraft observtions. EX: {'usaf': usaf_list, 'noaa': noaa_list}


    Notes
    ------
    * 22 Sep 2019
        - Handle case where flight from previous day continues into the
          day specified by 'date'

          Ex: date = '20190906'

          https://www.nhc.noaa.gov/archive/recon/2019/AHONT1/AHONT1-KWBC.201909060000.txt
          https://www.nhc.noaa.gov/archive/recon/2019/AHONT1/AHONT1-KWBC.201909060010.txt
          https://www.nhc.noaa.gov/archive/recon/2019/AHONT1/AHONT1-KWBC.201909060020.txt

    """
    col_names = ['filename', 'date_time']
    drop_cols = [0, 3, 4]
    fname_dict = {'noaa': [], 'usaf': []}
    base_url = 'https://www.nhc.noaa.gov/archive/recon/'

    if (date):
        date = datetime.strptime(date, '%Y%m%d')
        url_year = date.year
    elif (start):
        if not (end):
            raise ValueError("'end' argument cannot be None")
        start = datetime.strptime(start, '%Y%m%d-%H%M')
        end = datetime.strptime(end, '%Y%m%d-%H%M')
        url_year = start.year
    else:
        raise ValueError("'date' and 'start' args cannot both be None")

    base_url = base_url + '{}/{}/'.format(url_year, octant)

    # Read the list of filenames from the url
    fname_df = pd.read_html(base_url, skiprows=[0,1,2,3,4,5,6,7,8,9])[0]

    # Drop all columns except for the filename & publishing date time columns
    fname_df.drop(fname_df.columns[drop_cols],axis=1,inplace=True)

    # Drop any NaN values
    fname_df = fname_df.dropna(how="all")

    # set the dataframe column names
    fname_df.columns = col_names

    if (date):
        for idx, row in fname_df.iterrows():
            curr_dt = datetime.strptime(row['date_time'].split(' ')[0], '%Y-%m-%d')
            curr_fname = row['filename']
            if (curr_dt == date):
                if ('KNHC' in curr_fname):
                    fname_dict['usaf'].append(base_url + '{}'.format(curr_fname))
                else:
                    fname_dict['noaa'].append(base_url + '{}'.format(curr_fname))
    else:
        for idx, row in fname_df.iterrows():
            curr_dt = datetime.strptime(row['date_time'], '%Y-%m-%d %H:%M')
            curr_fname = row['filename']
            if ((curr_dt >= start) and (curr_dt <= end)):
                if ('KNHC' in curr_fname):
                    fname_dict['usaf'].append(base_url + '{}'.format(curr_fname))
                else:
                    fname_dict['noaa'].append(base_url + '{}'.format(curr_fname))

    return fname_dict



def parse_hdob_file(path):
    """
    Read an HDOB file and return a HDOBFile object

    Parameters
    ----------
    path : str
        Absolute path or url to the HDOB file to be opened & processed

    Returns
    -------
    hdob_file : HDOBFile object
    """
    col_names = ["obs_time", "lat", "lon", "static_air_press", "geo_pot_height",
                 "sfc_press_dval", "t_air", "t_dew", "wind_dir_spd", "wind_peak",
                 "sfc_wind_peak", "rain_rate", "qc_flags"]
    file_header = ''
    obs_data = []

    # Determine if 'path' is a path or url
    if isfile(path):
        # open & read local file
        with open(path, 'r') as fh:
            for idx, line in enumerate(fh):
                line = line.rstrip('\n')

                if (idx == 3):
                    file_header = line
                elif ((idx > 3) and (idx < 24)):
                    curr_line = line.split(' ')
                    curr_line = [x for x in curr_line if x != ' ']
                    obs_data.append(curr_line)
    hdob_df = pd.DataFrame(data=obs_data, index=range(0, len(obs_data)), columns=col_names)
    hdob_obj = HDOBFile(file_header, hdob_df)
    print(hdob_obj)
    # elif (isURL):



def minutes_degrees(coord, kywrd):
    """
    Converts coordinates from decimal minutes to decimal degrees

    Parameters
    ------------
    coord : str
        A single coordinate, either longitude or latitude, with a single char
        at the end indicating the hemisphere
    kywrd : str
        Indicates whether the coordinate is a latitude or longitude coordinate,
        as they are formatted differently

    Returns
    ------------
    deg : str
        Decimal degree coordinate
    """
    if (kywrd == 'lat'):
        deg = coord[:2]
        mins = coord[2:4]
    elif (kywrd == 'lon'):
        deg = coord[:3]
        mins = coord[3:5]
    else:
        raise ValueError('Invalid keyword parameter {}. Must be "lat" or "lon"'.format(kywrd))
    dec = float(mins) / 60
    deg = float(deg) + dec

    if (coord[-1] == "S" or coord[-1] == "W"):
        deg = deg * -1

    deg = str(deg)[:6]

    return deg



def main():
    fname = 'AHONT1-KNHC.201909020423.txt'
    # parse_hdob_file(fname)
    fnames = get_hdob_fnames(date='20190906')
    for f in fnames['noaa']:
        print(f)
    for f in fnames['usaf']:
        print(f)




if __name__ == '__main__':
    main()
