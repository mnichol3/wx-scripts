import nexradaws

conn = nexradaws.NexradAwsInterface()

def get_years(conn):
    print('Available years: ')
    years = conn.get_avail_years()
    for x in years:
        print(x)
    print('\n')

    return years



def get_months(conn, year):
    print('Available months for {}: '.format(year))
    months = conn.get_avail_months(year)
    for x in months:
        print(x)
    print('\n')

    return months



def print_days(conn, month, year):
    print('Days available for month: {}, year: {}'.format(month, day))
    days = conn.get_avail_days(year, month)
    for x in days:
        print(x)
    print('\n')

    return days



def get_radars(conn, day, month, year):
    print('Radars available for day: {}, month: {}, year: {}')
    radars = conn.get_avail_radars('2013','05','31')
    for x in radars:
        print(x)
    print('\n')

    return radars
