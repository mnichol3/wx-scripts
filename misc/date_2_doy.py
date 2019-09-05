"""
Python 3.6

Author: Matt Nicholson

Converts a date (format: MM-DD-YYYY) into day of year (int)

Example usage:
--------------

$ python date_2_doy.py '05-23-2019'

09-05-2019 --> 248

"""
import datetime
import sys

def calc_day(date_str):
	"""
	Converts a date into day of year

	Parameters
	---------
	date_str : str
		Date string to be converted to day of year
		Format: MM-DD-YYYY

	Returns
	-------
	doy : int
		Day of year corresponding to the parameter date
	"""
	doy = datetime.datetime.strptime(date_str, '%m-%d-%Y').timetuple().tm_yday
	return doy

def main():
	date_str = sys.argv[1]
	if (type(date_str) != str):
		raise ValueError('Date argument must be a string of format mm-dd-yyyy')
	day_of_year = calc_day(date_str)
	print("\n{} --> {}\n".format(date_str, day_of_year))

if __name__ == '__main__':
	main()
