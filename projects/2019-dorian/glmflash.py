"""
A simple class to represent a GLM flash
"""
from math import sin, cos, sqrt, atan2, radians

class GLMFlash(object):

    def __init__(self, date, time, x, y, area, energy, center_coords):
        super(GLMFlash, self).__init__()
        self.x = x
        self.y = y
        self.area = area
        self.energy = energy
        self.date = date
        self.time = time
        self.radial_dist = self._calc_dist(center_coords, (y, x))



    def _calc_dist(self, coords1, coords2):
        """
        Calculates the distance between a pair of geographic coordinates in decimal-
        degree format

        Parameters
        ----------
        coords1 : Tuple of floats
            coords1[0] = lat 1
            coords1[1] = lon 1

        coords2 : Tuple of floats
            coords2[0] = lat 2
            coords2[1] = lon 2


        Returns
        -------
        dist : float
            Distance between the two coordinates, in km
        """
        R = 6373.0  # Radius of the Earth, in km

        lon1 = radians(coords1[0])
        lat1 = radians(coords1[1])
        lon2 = radians(coords2[0])
        lat2 = radians(coords2[1])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        dist = R * c

        return dist



    def __repr__(self):
        return '<GLMFlash object - {} {} ({:.3f}, {:.3f})>'.format(self.date, self.time, self.x, self.y, )
