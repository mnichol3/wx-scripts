"""
Author: Matt Nicholson

A simple class for local GOES-16 Geostationary Lightning Mapper (GLM) netCDF files
"""
import os
import re
from datetime import datetime


class LocalGLMFile(object):

    def __init__(self, abs_path, type):
        super(LocalGLMFile, self).__init__()
        self.abs_path = abs_path
        self.filename = None
        self.scan_date = None
        self.scan_time = None
        self.data = None
        self.data_type = None
        if (abs_path is not None):
            self._parse_fname(abs_path)
            if (type == 'awips'):
                self._parse_scan_datetime_awips()
            elif(type == 'aws'):
                self._parse_scan_datetime_aws()
            else:
                raise ValueError("Invalid type argument. Must be 'aws' or 'awips'")



    def set_data(self, new_data):
        self.data = new_data
        self.data_type = new_data['data_type']



    def _parse_fname(self, abs_path):
        _, self.filename = os.path.split(abs_path)



    def _parse_scan_datetime_aws(self):
        """
        Ex: OR_GLM-L2-LCFA_G16_s20192481255200_e20192481255400_c20192481255427.nc
        """
        if (self.filename is not None):
            datetime_re = r'_s(\d{11})'
            match = re.search(datetime_re, self.filename)

            if (match):
                f_scantime = datetime.strptime(match.group(1), '%Y%j%H%M')
                self.scan_date = datetime.strftime(f_scantime, '%m-%d-%Y')
                self.scan_time = datetime.strftime(f_scantime, '%H:%M')
            else:
                raise ValueError('Unable to parse file scan datetime')
        else:
            raise ValueError('Filepath cannot be None')



    def _parse_scan_datetime_awips(self):
        """
        Ex: IXTR99_KNES_222357_35176.2019052223
        """
        if (self.filename is not None):
            scan_date_re = r'\.(\d{8})'
            scan_time_re = r'_\d{2}(\d{4})_'
            match_date = re.search(scan_date_re, self.filename)
            match_time = re.search(scan_time_re, self.filename)

            if (match_date and match_time):
                f_date = match_date.group(1)
                f_time = match_time.group(1)

                self.scan_date = datetime.strftime(f_date, '%m-%d-%Y')
                self.scan_time = datetime.strftime(f_time, '%H:%M')
            else:
                raise ValueError('Unable to parse file scan datetime')

        else:
            raise ValueError('Filepath cannot be None')



    def __repr__(self):
        return '<LocalGLMFile object - {} {} {}>'.format(self.scan_date, self.scan_time, self.data_type)
