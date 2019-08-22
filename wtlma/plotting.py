# Python 2.7
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import numpy as np

def plot_hist_area(x, y, save=False, show=True):
    """
    data: dict
        {'flash_area': area_list, 'ctr_alt': alt_list}
    """
    fig, ax = plt.subplots(figsize=(8,6))

    xbins = np.linspace(0, 50, 100)
    ybins = np.linspace(0, 20000, 100)

    hist = plt.hist2d(x, y, bins=(xbins, ybins),
               range=[[1, 50], [0, 20000]], norm=mcolors.PowerNorm(0.5),
               cmap=cm.hot)

    plt.xlabel('Flash Area (km^2)')
    plt.ylabel('Flash Altitude (m)')
    # plt.title('WTLMA Flash Area vs. Altitude for 05-23-2019 2050-2200z')
    plt.colorbar(hist[3], ax=ax)
    plt.tight_layout()

    if (save):
        plt.savefig('05232019-FlashAreaVsAlt.png', dpi=300)
    if (show):
        plt.show()



def plot_hist_dur(x, y, save=False, show=True):
    """
    data: dict
        {'flash_area': area_list, 'ctr_alt': alt_list}
    """
    fig, ax = plt.subplots(figsize=(8,6))

    xbins = np.linspace(0, 500, 100)
    ybins = np.linspace(0, 20000, 100)

    hist = plt.hist2d(x, y, bins=(xbins, ybins),
               range=[[0, 500], [0, 20000]], norm=mcolors.PowerNorm(0.5),
               cmap=cm.hot)

    plt.xlabel('Flash Duration (ms)')
    plt.ylabel('Flash Altitude (m)')
    # plt.title('WTLMA Flash Area vs. Altitude for 05-23-2019 2050-2200z')
    plt.colorbar(hist[3], ax=ax)
    plt.tight_layout()

    if (save):
        plt.savefig('05232019-FlashDurationVsAlt.png', dpi=300)
    if (show):
        plt.show()
