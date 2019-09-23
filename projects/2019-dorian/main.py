from datetime import datetime

from nhc_gis_track import track_csv_to_df, pp_df
from dorian_sort_lightning import geodesic_point_buffer, get_quadrant_coords, get_files_for_date_time
from glm_utils import read_file_glm_egf
from localglmfile import LocalGLMFile



def main():
    track_path = '/media/mnichol3/tsb1/data/storms/2019-dorian/initial_best_track_interp_1min.txt'

    # Load the best track 1-min interpolation dataframe
    # Col names: date-time (index), storm_num, lat, lon, mslp, wind, ss
    # track_df = track_csv_to_df(track_path)

    glm_path = '/media/mnichol3/pmeyers1/MattNicholson/storms/dorian/glm/aws'
    glm_fnames = get_files_for_date_time(glm_path, '2019-09-02 23:48:00')

    glm_objs = []
    for f in glm_fnames:
        glm_objs.append(read_file_glm_egf(f, product='f'))

    for obj in glm_objs:
        print(obj)



if __name__ == '__main__':
    main()
