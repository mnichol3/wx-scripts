"""
Print dictionary keys and their types all pretty and whatnot


Ex:

scan_date ----------->  <class 'str'>
band_wavelengths ---->  <class 'dict'>
band_ids ------------>  <class 'list'>
sat_height ---------->  <class 'numpy.float64'>
sat_lon ------------->  <class 'numpy.float64'>
sat_sweep ----------->  <class 'str'>
semimajor_ax -------->  <class 'numpy.float64'>
semiminor_ax -------->  <class 'numpy.float64'>
inverse_flattening -->  <class 'numpy.float64'>
lat_center ---------->  <class 'numpy.float32'>
lon_center ---------->  <class 'numpy.float32'>
y_image_bounds ------>  <class 'numpy.ma.core.MaskedArray'>
x_image_bounds ------>  <class 'numpy.ma.core.MaskedArray'>
lat_lon_extent ------>  <class 'dict'>
x_min --------------->  <class 'float'>
y_min --------------->  <class 'float'>
x_max --------------->  <class 'float'>
y_max --------------->  <class 'float'>
data ---------------->  <class 'numpy.ma.core.MaskedArray'>

"""

def pp_keys(dict):
    keys = list(dict.keys())
    max_len_key = max(keys, key=len)

    for key, val in dict.items():
        print('{} {}  {}'.format(key, '-->'.rjust(len(max_len_key) - len(key) + 3, '-'), type(val)))
