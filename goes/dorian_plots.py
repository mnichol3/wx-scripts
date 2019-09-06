from utils import read_file_abi, get_fnames_from_dir, plot_mercator


# inf_base = '/media/mnichol3/tsb1/data/abi/dorian/inf'
# fnames = get_fnames_from_dir(inf_base)

inf_file = '/media/mnichol3/tsb1/data/abi/dorian/inf/OR_ABI-L2-CMIPM1-M6C13_G16_s20192491031171_e20192491031240_c20192491031307.nc'
outpath = '/home/mnichol3/Pictures/wx/2019-Dorian/plots'

# plot_comms = {'save': False,
#               'show': True,
#               'outpath': None}

plot_comms = {'save': True,
              'show': False,
              'outpath': outpath}

inf_data = read_file_abi(inf_file)
plot_mercator(inf_data, plot_comms)

# for key, val in inf_data.items():
#     print(key)
#
# print(inf_data['data_units'])
