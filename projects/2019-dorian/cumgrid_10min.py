"""
Class to hold 10-min cumulative FED grid data
"""
import numpy as np


class CumGrid_10min(object):
    """
    Attributes
    ----------
    ref_datetime : str
        Date & (midpoint) time of the 10-minute span. Corresponds to a 10-minute
        Best Track interpolated center fix.
        Format: YYYY-MM-DD_HH-MM-SS (UTC)
    ref_date : str
        Date of the 10-minute span. Format: YYYY-MM-DD
    btcf : tuple of floats
        Geodetic coordinates of the Best Track center fix, in decimal degrees.
        Format: (lat, lon)
    cum_grid : 400x400 numpy ndarray
        Cumulative Flash Extent Density grid for the 10-minute span
    ref_grid : 400x400 numpy ndarray
        ABI Fixed Grid scanning angle (in radians) grid corresponding to the
        cum_grid

    Functions
    ----------
    __init__             : Initialize a new GLMFEDFile object
    __repr__             : Represent a GLMFEDFile object by printing its scan datetime
                           & filename


    Dependencies                    Alias
    ------------                   -------
    > NumPy                 (import numpy as np)

    """

    def __init__(self, ref_datetime, center_fix, cum_grid, ref_grid_x, ref_grid_y):
        """
        Parameters
        ----------
        ref_datetime : str
        center_fix : tuple of float
        cum_grid : numpy ndarray
        ref_grid : numpy ndarray
        """
        self.ref_datetime = ref_datetime
        self.center_fix = center_fix
        self.cum_grid = cum_grid
        self.ref_grid_x = ref_grid_x
        self.ref_grid_y = ref_grid_y



    def __repr__(self):
        lat = self.center_fix[0]
        lon = self.center_fix[1]
        return '<CumGrid_10min object - {0}z ({1:.4f},{2:.4f})>'.format(self.ref_datetime, lat, lon)
