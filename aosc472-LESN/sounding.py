"""
04 March 2019
Author: Matt Nicholson
"""

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np
import pandas as pd
import metpy.calc as mpcalc
from metpy.cbook import get_test_data
from metpy.plots import Hodograph, SkewT
from metpy.units import units

DATA_PATH = '/home/mnichol3/Documents/coursework/AOSC472/lake-effect-snow-case-study/'

def process_file(fname):
    data = []
    indexes = [3, 4, 5, 9]


    with open(fname) as f:
        for line in f:
            temp = []

            line = line.strip('\n')

            splits = line.split(' ')

            if (len(splits) < 40): # < 200 hPa, all data present
                temp = [param for param in splits if (param != '')]
            else:
                temp2 = [param for param in splits if (param != '')]
                if (len(temp2) > 5):
                    idx_a = 0
                    idx_b = 0
                    while (idx_a <= 10):
                        if (idx_a not in indexes):
                            temp.append(temp2[idx_b])
                            idx_a += 1
                            idx_b += 1
                        else:
                            temp.append(np.nan)
                            idx_a += 1

            if (temp):
                data.append(temp)

    return data




def make_plot(fname):
    file_data = process_file(fname)
    col_names = ['pressure', 'height', 'temperature', 'dewpoint', 'relativeH',
             'mixingR', 'direction', 'speed', 'theta', 'thetaE', 'thetaV']

    data = pd.DataFrame(file_data, columns=col_names, dtype=float)

    data['u_wind'], data['v_wind'] = mpcalc.wind_components(data['speed'],
                                                    np.deg2rad(data['direction']))

    #print(data)

    p = data['pressure'].values * units.hPa
    T = data['temperature'].values * units.degC
    Td = data['dewpoint'].values * units.degC
    wind_speed = data['speed'].values * units.knots
    wind_dir = data['direction'].values * units.degrees

    u, v = mpcalc.wind_components(wind_speed, wind_dir)

    fig = plt.figure(figsize=(9,9))
    skew = SkewT(fig, rotation=45)

    skew.plot(p, T, 'r')
    skew.plot(p, Td, 'g')
    skew.plot_barbs(p, u, v)
    skew.ax.set_ylim(1000,100)
    skew.ax.set_xlim(-40, 60)

    #lcl_pres, lcl_temp = mpcalc.lcl(p[0], T[0], Td[0])
    #skew.plot(lcl_pres, lcl_temp, 'ko', markerfacecolor='black')

    #prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
    #skew.plot(p, prof, 'k', linewidth=2)

    #skew.shade_cin(p, T, prof)
    #skew.shade_cape(p, T, prof)

    skew.ax.axvline(0, color='c', linestyle='--', linewidth=2)

    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()

    plt.title('ALB 20180103 00z')

    plt.show()



def main():

    fnames = ['sounding-ALB-20180103-00.txt', 'sounding-BUF-20180102-00.txt']

    fname = DATA_PATH + fnames[0]

    make_plot(fname)



if (__name__ == "__main__"):
    main()
