from utils import ingest, print_stats
from plotting import plot_hist


if (__name__ == '__main__'):
    flash_df = ingest()
    print_stats(flash_df)

    data_dict = {'flash_area': flash_df['area'],
                 'flash_alt':  flash_df['ctr_alt']
    }

    plot_hist(data_dict, num_bins=200)
