"""
Python 3.6

File contains:
* Configuration class to hold local file paths.
* Class to hold URLs of NOAA/NWS RSS feeds.

24 Jul 2020
"""
from os.path import join

class Paths():
    """
    Class to hold local paths.
    """
    base_path = '/home/mnichol3/code/wx-scripts/projects/noaa-rss'
    logs   = join(base_path, 'logs')
    raw_db = join(base_path, 'raw_rss')
    output = join(base_path, 'out')

class Feeds():
	"""
	Class to hold NOAA RSS URLs.
	"""
	twdat = 'https://www.nhc.noaa.gov/xml/TWDAT.xml'         # NHC Tropical Weather Discussion - Atlantic
	twdep = 'https://www.nhc.noaa.gov/xml/TWDEP.xml'         # NHC Tropical Weather Discussion - EastPac
	reprpd = 'https://www.nhc.noaa.gov/xml/REPRPD.xml'       # NHC Weather Recon Flights Plan of the Day
	spcmd = 'http://www.spc.noaa.gov/products/spcmdrss.xml'  # SPC Mesoscale Discussions
	spcac = 'http://www.spc.noaa.gov/products/spcacrss.xml'  # SPC Convective Outlooks
