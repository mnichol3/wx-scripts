"""
A simple class to hold metadata for a single Flash Extent file produced by
glmtools
"""
import os
import re
from datetime import datetime

class LocalFlashExtentFile(object):

    def __init__(self, abs_path):
        """
        Parameters
        -----------
        abs_path : str
            Absolute path, including filename, of the FE netCDF file

        Attributes
        -----------
        abs_path : str
            Absolute path, including filename, of the FE netCDF file
        file_name : str
            Name of the netCDF file. Does not include path of the directory
        scan_date : str
            Date corresponding to the input data. Format: YYYY-MM-DD
        scan_date_doy : str
            Date corresponding to the input data, but in day of year format.
            Format: YYYY-DOY
        scan_time : str
            Time corresponding to the input data.
            Format: HH:MM (UTC)

        """
        super(LocalFlashExtentFile, self).__init__()
        self.abs_path = abs_path
        self.filename = None
        self.scan_date = None
        self.scan_date_doy = None
        self.scan_time = None
        if (abs_path is not None):
            self._parse_fname()
            self._parse_scan_datetime()


    def _parse_fname(self):
        self.filename = self.abs_path.rpartition('/')[-1]



    def _parse_scan_datetime(self):
        """
        Ex: GLM-00-00_20190908_231900_60_1src_056urad-dx_flash_extent.nc
        """
        if (self.filename is not None):
            datetime_re = r'GLM-\d{2}-\d{2}_(\d{8}_\d{4})'
            match = re.search(datetime_re, self.filename)

            if (match):
                f_scantime = datetime.strptime(match.group(1), '%Y%m%d_%H%M')
                self.scan_date = datetime.strftime(f_scantime, '%Y-%m-%d')
                self.scan_date_doy = datetime.strftime(f_scantime, '%Y-%j')
                self.scan_time = datetime.strftime(f_scantime, '%H:%M')
            else:
                raise ValueError('Unable to parse file scan datetime')
        else:
            raise ValueError('Filepath cannot be None')



    def get_path(self):
        """
        Returns the path of the directory that contains the FE file.
        When 'os.path.join'd with the filename, the absolute path of the file
        is given

        Ex:
            .../storms/dorian/glm/gridded/251/23
        """
        path = self.abs_path.rpartition('/')[0]
        return path



    def __repr__(self):
        return '<LocalFlashExtentFile object - {} {}>'.format(self.scan_date, self.scan_time)
