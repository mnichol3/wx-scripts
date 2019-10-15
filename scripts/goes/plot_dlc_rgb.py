from utils import read_file_abi, get_fnames_from_dir, _preprocess_day_land_cloud_rgb, plot_day_land_cloud_rgb
from os.path import join
import os
from sys import exit
from datetime import datetime

def pp_keys(dict):
    keys = list(dict.keys())
    max_len_key = max(keys, key=len)

    for key, val in dict.items():
        print('{} {}  {}'.format(key, '-->'.rjust(len(max_len_key) - len(key) + 3, '-'), type(val)))



def main():
    """
    ffmpeg cmd:
        mp4:  ffmpeg -i image-%03d.png -c:v libx264 -pix_fmt yuv420p out.mp4
        webm: ffmpeg -i image-%03d.png video.webm
    """
    base_path = '/media/mnichol3/pmeyers1/MattNicholson/abi/273'
    out_path = '/media/mnichol3/pmeyers1/MattNicholson/goes_rgb/day_land_cloud/2019-09-30'

    rename = False

    sub_dirs = os.walk(base_path)
    next(sub_dirs)  # We don't care about this one

    plot_comms = {'save': True,
                  'show': False,
                  'outpath': out_path}

    # extent = [-112, -60, 20, 50]
    extent = [-112, -60, 20, 50]

    # Iterate over each hour subdirectory
    for hour in sub_dirs:
        # Get the files for each hour
        for f_mcmip in hour[2]:

            f_path = join(hour[0], f_mcmip)

            rgb_data = _preprocess_day_land_cloud_rgb(f_path)

            plot_day_land_cloud_rgb(rgb_data, plot_comms, ax_extent=[-112, -60, 20, 50])
            print('\n')


    if (rename):
        # Rename output image files as image-000.png, image-001.png, etc
        # Optimizes ffmpeg call
        f_names = os.listdir(out_path)

        # Manually sort the list because os.listdir can be wonky sometimes
        format = 'DayLandCloudRGB-C-%Y%m%d-%H:%M.png'
        f_names.sort(key = lambda x: datetime.strptime(x, format))

        for f_idx, f_name in enumerate(f_names):
            # print(f_idx, f_name)

            src = join(out_path, f_name)

            dst = 'image-{}.png'.format(str(f_idx).zfill(3))

            print('Renaming {} as {}'.format(f_name, dst))

            dst = join(out_path, dst)

            os.rename(src, dst)


if __name__ == '__main__':
    main()
