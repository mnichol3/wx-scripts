from utils import read_file_abi


vis_path = '/media/mnichol3/tsb1/data/abi/dorian/OR_ABI-L1b-RadM1-M6C02_G16_s20192481730202_e20192481730260_c20192481730298.nc'
inf_path = '/media/mnichol3/tsb1/data/abi/dorian/OR_ABI-L2-CMIPM1-M6C13_G16_s20192481730202_e20192481730271_c20192481730342.nc'

vis = read_file_abi(vis_path)
inf = read_file_abi(inf_path)

for key, val in vis.items():
    print(key, val)
