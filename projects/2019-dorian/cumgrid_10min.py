"""
Class to hold 10-min cumulative FED grid data
"""
import numpy as np


class CumGrid_10min(object):
    """
    Attributes
    ----------
    ref_time : str
        Time in the middle of the 10-minute span. Corresponds to a 10-minute
        Best Track interpolated center fix.
        Format: HH:MM (UTC)
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

    def __init__(self, ref_date, ref_time, center_fix, cum_grid, ref_grid):
        """
        Parameters
        ----------
        ref_date : str
        ref_time : str
        center_fix : tuple of float
        cum_grid : numpy ndarray
        ref_grid : numpy ndarray
        """
        self.ref_date = ref_date
        self.ref_time = ref_time
        self.center_fix = center_fix
        self.cum_grid = cum_grid
        self.ref_grid = ref_grid



    def __repr__(self):
        lat = self.center_fix[0]
        lon = self.center_fix[1]
        return '<CumGrid_10min object - {0} {1}z ({2:.4f},{3:.4f})>'.format(self.ref_date, self.ref_time, lat, lon)
