
from os.path import join
import pandas as pd
from sys import exit


def ingest():
    """
    Accumulate flashes into pandas DF
    """

    base_path = '/home/mnichol3/Coding/wx-scripts/wtlma'

    flash_files = ['flash-out-05232019-2050.txt',
                   'flash-out-05232019-2100.txt',
                   'flash-out-05232019-2110.txt',
                   'flash-out-05232019-2120.txt',
                   'flash-out-05232019-2130.txt',
                   'flash-out-05232019-2140.txt',
                   'flash-out-05232019-2150.txt']

    df_cols = ['start', 'end', 'duration', 'area', 'ctr_alt', 'ctr_lat', 'ctr_lon',
               'tot_energy']

    flash_df = pd.read_csv(join(base_path, flash_files[0]), sep=',', names=df_cols)

    for f in flash_files[1:]:
        curr_path = join(base_path, f)
        curr_df = pd.read_csv(curr_path, sep=',', names=df_cols)
        flash_df = pd.concat([flash_df, curr_df], ignore_index=True)

    return flash_df



def print_stats(df):
    area_list = df['area'].tolist()
    print('Flash area (km^2):')
    print('     min: {}'.format(min(area_list)))
    print('     max: {}'.format(max(area_list)))
    print('     avg: {}\n'.format(sum(area_list)/len(area_list)))

    energy_list = df['tot_energy']
    print('Total flash energy:')
    print('     min: {}'.format(min(energy_list)))
    print('     max: {}'.format(max(energy_list)))
    print('     avg: {}\n'.format(sum(energy_list)/len(energy_list)))

    duration_list = df['duration']
    print('Flash duration (s):')
    print('     min: {}'.format(min(duration_list)))
    print('     max: {}'.format(max(duration_list)))
    print('     avg: {}\n'.format(sum(duration_list)/len(duration_list)))

    alt_list = df['ctr_alt']
    print('Flash altitude (m):')
    print('     min: {}'.format(min(alt_list)))
    print('     max: {}'.format(max(alt_list)))
    print('     avg: {}\n'.format(sum(alt_list)/len(alt_list)))

    lat_list = df['ctr_lat']
    print('Flash lats:')
    print('     min: {}'.format(min(lat_list)))
    print('     max: {}'.format(max(lat_list)))
    print('     avg: {}\n'.format(sum(lat_list)/len(lat_list)))

    lon_list = df['ctr_lon']
    print('Flash lons:')
    print('     min: {}'.format(min(lon_list)))
    print('     max: {}'.format(max(lon_list)))
    print('     avg: {}\n'.format(sum(lon_list)/len(lon_list)))

    print('Number of flashes: {}'.format(df.shape[0]))
