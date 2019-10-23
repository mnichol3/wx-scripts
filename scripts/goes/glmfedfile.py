"""
Author: Matt Nicholson

A simple class for GOES-16 Geostationary Lightning Mapper (GLM)
Flash Extent Density (FED) netCDF files
"""

import re
from datetime import datetime
from os.path import join, split
import numpy as np
from netCDF4 import Dataset

class GLMFEDFile(object):
    """
    Attributes
    ----------
    f_name : str
        Filename of the Flash Extent Density file
    scan_date_time : str
        Date & Time of the GLM observations. Format: YYYY-MM-DD HH:MM (UTC)
    x : numpy nd array
        GOES fixed grid projection x-coordinate (radians)
    y : numpy nd array
        GOES fixed grid projection y-coordinate (radians)
    goes_imager_projection : dict of str/float
        Keys:
            latitude_of_projection_origin  : float
            longitude_of_projection_origin : float
            semi_major_axis                : float
            semi_minor_axis                : float
            perspective_point_height       : float
            inverse_flattening             : float
            sweep_angle_axis               : str
            x_add_offset                   : float
            x_scale_factor                 : float
            y_add_offset                   : float
            y_scale_factor                 : float

    flash_extent_density : numpy ndarray
        Flash Extent Density data
    fed_window : bool
        If False, 1-min data is represented in the flash_extent_density array.
        If True, 5-min FED window data is represented in the flash_extent_density array.

    Functions
    ----------
    __init__             : Initialize a new GLMFEDFile object
    _get_fname           : Get the name of the FED file from the file's absolute path
    _parse_scan_datetime : Parse the file's scan date & time from the filename
    update_x             : Update a GLMFEDFile object's x attribute
    update_y             : Update a GLMFEDFile object's y attribute
    update_fed           : Update a GLMFEDFile object's FED data attribute
    __repr__             : Represent a GLMFEDFile object by printing its scan datetime
                           & filename


    Dependencies                    Alias
    ------------                   -------
    > NumPy                 (import numpy as np)
    > os.path.split         (from os.path import split)
    > datetime.datetime     (from datetime import datetime)
    > netCDF4.Dataset       (from netCDF4 import Dataset)
        * The Class itself doesn't use Dataset, however the partnered read_file()
          func does
    > re                             ---
    """

    def __init__(self, abs_path, projection_dict, x, y, fed, fed_window):
        """
        Parameters
        ----------
        f_name : str
        projection_dict : dict of float/str
        x : numpy ndarray
        y : numpy ndarray
        fed : numpy ndarray
        fed_window : bool
        """
        self.f_name = self._get_fname(abs_path)
        self.scan_date_time = self._parse_scan_datetime()
        self.x = x
        self.y = y
        self.goes_imager_projection = projection_dict
        self.flash_extent_density = fed
        self.fed_window = fed_window



    def _get_fname(self, abs_path):
        """
        Return the filename from the absolute path
        """
        _, filename = split(abs_path)
        return filename



    def _parse_scan_datetime(self):
        """
        Parse the scan date & time from the file name

        Filename ex: IXTR99_KNES_222357_35176.2019052223
                     IXTR9(8 or 9)_KNES_ddHHMM_?????.YYYYmmddHH

                     where:
                        - dd   : day
                        - mm   : month
                        - YYYY : year
                        - HH   : hour (24-hr, UTC)
                        - MM   : minute
                        - ???? : No idea tbh
        """
        scan_date_time = ''

        if (self.f_name is not None):
            scan_date_re = r'\.(\d{8})'         # YYYYMMDD
            scan_time_re = r'_\d{2}(\d{4})_'    # HHMM
            match_date = re.search(scan_date_re, self.f_name)
            match_time = re.search(scan_time_re, self.f_name)

            if (match_date and match_time):
                f_date = match_date.group(1)
                f_time = match_time.group(1)
                f_date_time = '{} {}'.format(f_date, f_time)
                scan_date_time = datetime.strptime(f_date_time, '%Y%m%d %H%M')
                scan_date_time = datetime.strftime(scan_date_time, '%Y-%m-%d %H:%M')

                return scan_date_time
            else:
                raise ValueError('Unable to parse file scan datetime')

        else:
            raise ValueError("'f_name' cannot be None")



    def update_x(self, new_x):
        """
        Update the value of the object's x attribute, e.g., in the case of
        subsetting a mesoscale domain

        Parameters
        ----------
        new_fed : numpy ndarray
        """
        if (not isinstance(new_x, np.ndarray)):
            raise TypeError("'new_x' must be a NumPy ndarray, got {}".format(type(new_x)))
        del self.x
        self.x = new_x



    def update_y(self, new_y):
        """
        Update the value of the object's y attribute, e.g., in the case of
        subsetting a mesoscale domain

        Parameters
        ----------
        new_fed : numpy ndarray
        """
        if (not isinstance(new_y, np.ndarray)):
            raise TypeError("'new_y' must be a NumPy ndarray, got {}".format(type(new_y)))
        del self.y
        self.y = new_y



    def update_fed(self, new_fed):
        """
        Update the value of the object's fed attribute, e.g., in the case of
        subsetting a mesoscale domain

        Parameters
        ----------
        new_fed : numpy ndarray
        """
        if (not isinstance(new_fed, np.ndarray)):
            raise TypeError("'new_fed' must be a NumPy ndarray, got {}".format(type(new_fed)))
        del self.fed
        self.fed = new_fed



    def __repr__(self):
        return '<GLMFEDFile object - {} {}>'.format(self.scan_date_time, self.f_name)


################################################################################
################################# End Class ####################################
################################################################################



def read_file(file_paths, window=False):
    """
    Reads a GLM Flash Extent Density (FED) netCDF file.
    Filename ex: IXTR99_KNES_222357_35176.2019052223

    Parameters
    ----------
    file_paths : list of str
        List of absolute paths of GLM FED files to read
    window : bool, optional
        If True, 5-min FED window data will be read from the file.
        If False, 1-min FED windown data will be read.
        Default is False

    Returns
    --------
    List of GLMFEDFile objects

    Dependencies                    Alias
    ------------                   -------
    > NumPy                 (import numpy as np)
    > os.path.split         (from os.path import split)
    > netCDF4.Dataset       (from netCDF4 import Dataset)
    > glmfedfile.GLMFEDFile (from glmfedfile import GLMFEDFile)
    """
    fed_objs = []

    if (not isinstance(file_paths, list)):
        file_paths = [file_paths]

    for curr_path in file_paths:
        projection_dict = {}

        print('Processing {}'.format(split(curr_path)[1]))

        fh = Dataset(curr_path, 'r')

        projection_dict['latitude_of_projection_origin']  = fh.variables['goes_imager_projection'].latitude_of_projection_origin
        projection_dict['longitude_of_projection_origin'] = fh.variables['goes_imager_projection'].longitude_of_projection_origin
        projection_dict['semi_major_axis']                = fh.variables['goes_imager_projection'].semi_major_axis
        projection_dict['semi_minor_axis']                = fh.variables['goes_imager_projection'].semi_minor_axis
        projection_dict['perspective_point_height']       = fh.variables['goes_imager_projection'].perspective_point_height
        projection_dict['inverse_flattening']             = fh.variables['goes_imager_projection'].inverse_flattening
        projection_dict['sweep_angle_axis']               = fh.variables['goes_imager_projection'].sweep_angle_axis
        projection_dict['x_add_offset']                   = fh.variables['x'].add_offset
        projection_dict['x_scale_factor']                 = fh.variables['x'].scale_factor
        projection_dict['y_add_offset']                   = fh.variables['y'].add_offset
        projection_dict['y_scale_factor']                 = fh.variables['y'].scale_factor

        x = np.asarray(fh.variables['x'][:])
        y = np.asarray(fh.variables['y'][:])

        if (window):
            fed = np.asarray(fh.variables['Flash_extent_density_window'][:])
        else:
            fed = np.asarray(fh.variables['Flash_extent_density'][:])

        fh.close()
        fh = None

        curr_obj = GLMFEDFile(curr_path, projection_dict, x, y, fed, window)
        fed_objs.append(curr_obj)

    return fed_objs



## Main for testing
def main():
    f_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/gridded/nc/20190826'
    f_name = 'IXTR98_KNES_262011_122283.2019082620.nc'
    f_abs = join(f_path, f_name)
    obj = read_file([f_abs])[0]
    print(obj)
    # print(obj.goes_imager_projection)


if __name__ == '__main__':
    main()
