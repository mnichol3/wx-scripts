from utils import read_file_abi, get_fnames_from_dir, _preprocess_day_land_cloud_rgb, plot_day_land_cloud_rgb
from os.path import join
from sys import exit

def pp_keys(dict):
    keys = list(dict.keys())
    max_len_key = max(keys, key=len)

    for key, val in dict.items():
        print('{} {}  {}'.format(key, '-->'.rjust(len(max_len_key) - len(key) + 3, '-'), type(val)))


base_path = '/media/mnichol3/tsb1/data/abi'
f_red = 'OR_ABI-L2-CMIPC-M6C05_G16_s20192591601148_e20192591603521_c20192591604082.nc'
f_green = 'OR_ABI-L2-CMIPC-M6C03_G16_s20192591601148_e20192591603521_c20192591604000.nc'
f_blue = 'OR_ABI-L2-CMIPC-M6C02_G16_s20192591601148_e20192591603521_c20192591604035.nc'
f_mcmip = 'OR_ABI-L2-MCMIPC-M6_G16_s20192591626148_e20192591628521_c20192591629067.nc'

# plot_comms = {'save': False,
#               'show': True,
#               'outpath': None}

plot_comms = {'save': True,
              'show': False,
              'outpath': '/home/mnichol3/Coding/wx-scripts/goes'}

red_data = read_file_abi(join(base_path, f_red))
green_data = read_file_abi(join(base_path, f_green))
blue_data = read_file_abi(join(base_path, f_blue))

f_path = join(base_path, f_mcmip)
rgb_data = _preprocess_day_land_cloud_rgb(f_path)

pp_keys(rgb_data)

plot_day_land_cloud_rgb(rgb_data, plot_comms, ax_extent=[-112, -60, 20, 50])
