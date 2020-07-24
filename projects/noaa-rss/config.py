"""
Python 3.6

File contains:
* Configuration class to hold local file paths.
* Class to hold URLs of NOAA/NWS RSS feeds.

24 Jul 2020
"""

class Paths():
    """
    Class to hold local paths.
    """
    logs = '/path/to/base/log/dir'
    raw_db = '/path/to/raw/rss/db'


class Feeds():
	"""
	Class to hold NOAA RSS URLs.
	"""
	twdat = 'https://www.nhc.noaa.gov/xml/TWDAT.xml'         # NHC Tropical Weather Discussion - Atlantic
	twdep = 'https://www.nhc.noaa.gov/xml/TWDEP.xml'         # NHC Tropical Weather Discussion - EastPac
	reprpd = 'https://www.nhc.noaa.gov/xml/REPRPD.xml'       # NHC Weather Recon Flights Plan of the Day
	spcmd = 'http://www.spc.noaa.gov/products/spcmdrss.xml'  # SPC Mesoscale Discussions
	spcac = 'http://www.spc.noaa.gov/products/spcacrss.xml'  # SPC Convective Outlooks
