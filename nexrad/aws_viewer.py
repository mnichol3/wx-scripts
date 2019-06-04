import nexradaws
from datetime import datetime

conn = nexradaws.NexradAwsInterface()

def get_years(conn):
    print('\n')
    print('Available years: ')
    years = conn.get_avail_years()
    for x in years:
        print(x)
    print('\n')

    return years



def get_months(conn, year):
    print('\n')
    print('Available months for {}: '.format(year))
    months = conn.get_avail_months(year)
    for x in months:
        print(x)
    print('\n')

    return months



def print_days(conn, month, year):
    print('\n')
    print('Days available for month: {}, year: {}'.format(month, day))
    days = conn.get_avail_days(year, month)
    for x in days:
        print(x)
    print('\n')

    return days



def get_radars(conn, day, month, year):
    print('\n')
    print('Radars available for day: {}, month: {}, year: {}')
    radars = conn.get_avail_radars('2013','05','31')
    for x in radars:
        print(x)
    print('\n')

    return radars



def avail_scans(conn, day, month, year, site):
    availscans = conn.get_avail_scans(year, month, day, site)
    print('\n')
    print("There are {} NEXRAD files available for {}/{}/{} for the {} radar.\n".format(len(availscans), month, day, year, site))
    print('\n')

    for x in availscans:
        print(x)

    return availscans



def get_scans_start_end(conn, day, month, year, site, h_start, m_start, h_end, m_end):

    day = int(day)
    month = int(month)
    year = int(year)
    h_start = int(h_start)
    m_start = int(m_start)
    h_end = int(h_end)
    m_end = int(m_end)

    t_start = datetime(year, month, day, h_start, m_start)
    t_end = datetime(year, month, day, h_end, m_end)

    scans = conn.get_avail_scans_in_range(t_start, t_end, site)
    print('\n')
    print("There are {} scans available between {} and {}\n".format(len(scans), t_start, t_end))

    for x in scans:
        print(x)

    return scans



def download_files(conn, nexrad_objs, out_path):
    print('\n')
    print("Downloading {} NEXRAD files to {}".format(len(nexrad_objs), out_path))

    results = conn.download(nexrad_objs, out_path)

    for scan in results.iter_success():
        print ("{} volume scan time {}".format(scan.radar_id,scan.scan_time))

    return results
