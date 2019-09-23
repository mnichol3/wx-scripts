from netCDF4 import Dataset
from localglmfile import LocalGLMFile


def read_file_glm_egf(abs_path, product='f'):
    """
    Read a GLM file into a glm_obj

    Parameters
    ----------
    abs_path : str
        Absolute path to the GLM file to open & read
    product : str
        Product (out of events, groups, and flashes) to read. Default is 'f'
        Valid strings: 'f': Flashes, 'g': Groups, 'e': Events

    Returns
    -------
    glm_obj : LocalGLMFile object
        LocalGLMFile object containing the data from the glm file

    Dependencies
    ------------
    > localglmfile.py
    > netCDF4.Dataset
    """
    data_dict = {}

    if (not product in ['e', 'f', 'g']):
        raise ValueError("Invalid product argument. Valid: 'e', 'f', 'g'")

    fh = Dataset(abs_path, 'r')

    data_dict['long_name'] = fh.variables['goes_lat_lon_projection'].long_name
    data_dict['lat_0'] = fh.variables['nominal_satellite_subpoint_lat'][:]
    # File states lon_0 is -75.2, AWIPS states its -75.0
    # data_dict['lon_0'] = fh.variables['nominal_satellite_subpoint_lon'][:]
    data_dict['lon_0'] = -75.2
    data_dict['semi_major_axis'] = fh.variables['goes_lat_lon_projection'].semi_major_axis
    data_dict['semi_minor_axis'] = fh.variables['goes_lat_lon_projection'].semi_minor_axis
    data_dict['height'] = fh.variables['nominal_satellite_height'][:]
    data_dict['inv_flattening'] = fh.variables['goes_lat_lon_projection'].inverse_flattening
    data_dict['sweep_ang_axis'] = 'x'

    if (product == 'f'):
        data_dict['x'] = fh.variables['flash_lon'][:]
        data_dict['y'] = fh.variables['flash_lat'][:]
        flash_stats = {'area': fh.variables['flash_area'][:],
                       'energy': fh.variables['flash_energy'][:],
                       'count': fh.variables['flash_count'][:],
                       'id': fh.variables['flash_id'][:]}
        data_dict['data'] = flash_stats
        data_dict['data_type'] = 'Flashes'
    elif (product == 'e'):
        data_dict['x'] = fh.variables['event_lon'][:]
        data_dict['y'] = fh.variables['event_lat'][:]
        event_stats = {'area': None,
                       'energy': fh.variables['event_energy'][:],
                       'count': fh.variables['event_count'][:],
                       'id': fh.variables['event_id'][:]}
        data_dict['data'] = event_stats
        data_dict['data_type'] = 'Events'
    elif (product == 'g'):
        data_dict['x'] = fh.variables['group_lon'][:]
        data_dict['y'] = fh.variables['group_lat'][:]
        group_stats = {'area': fh.variables['group_area'][:],
                       'energy': fh.variables['group_energy'][:],
                       'count': fh.variables['group_count'][:],
                       'id': fh.variables['group_id'][:]}
        data_dict['data'] = group_stats
        data_dict['data_type'] = 'Groups'

    fh.close()
    fh = None

    glm_obj = LocalGLMFile(abs_path, 'aws')
    glm_obj.set_data(data_dict)

    return glm_obj
