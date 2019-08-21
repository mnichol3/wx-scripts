import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

def plot_hist(data, num_bins=50):
    """
    data: dict
        {'flash_area': area_list, 'ctr_alt': alt_list}
    """
    fig, ax = plt.subplots(figsize=(4,4))

    xbins = np.linspace(0, 100, 100)
    ybins = np.linspace(0, 20000, 100)

    plt.hist2d(data.values()[0], data.values()[1], bins=(xbins, ybins),
               range=[[1, 200], [0, 20000]], norm=mcolors.PowerNorm(0.5))
    plt.xlabel(data.keys()[0])
    plt.ylabel(data.keys()[1])

    plt.show()

    # xbins = np.linspace(0, 200, 100)
    # ybins = np.linspace(0, 20000, 100)
    #
    # counts, _, _ = np.histogram2d(data.values()[0], data.values()[1], bins=(xbins, ybins))
    #
    # fig, ax = plt.subplots()
    # # ax.set_ylim([0, 19000])
    # ax.set_xlim([0, 200])
    # ax.pcolormesh(xbins, ybins, counts.T)
    # #ax.set_aspect('equal', adjustable='box')
    # plt.show()
