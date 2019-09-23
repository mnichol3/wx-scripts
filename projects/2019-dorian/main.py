from datetime import datetime

from nhc_gis_track import track_csv_to_df, pp_df
from dorian_sort_lightning import geodesic_point_buffer, get_quadrant_coords



def main():
    track_path = '/media/mnichol3/tsb1/data/storms/2019-dorian/initial_best_track_interp_1min.txt'

    # Load the best track 1-min interpolation dataframe
    # Col names: date-time (index), storm_num, lat, lon, mslp, wind, ss
    # track_df = track_csv_to_df(track_path)

    lat = 20
    lon = -112
    ring = geodesic_point_buffer(lat, lon, 20)

    ring_dict = get_quadrant_coords(buff_obj=ring, pprint=True)



if __name__ == '__main__':
    main()
