from utils import ingest, print_stats, calc_geo_area
from plotting import *


if (__name__ == '__main__'):
    flash_df = ingest()
    print_stats(flash_df)

    area = flash_df['area'].tolist()
    duration = flash_df['duration'].tolist()
    duration = [x*1000 for x in duration] # convert from seconds to miliseconds

    altitude = flash_df['ctr_alt'].tolist()

    # plot_hist_area(area, altitude, save=True, show=False)
    # plot_hist_dur(duration, altitude, save=True, show=False)
    # plot_hist_dur_basic(duration, save=True, show=False)
