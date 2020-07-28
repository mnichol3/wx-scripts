"""
Python 3.6

File contains:
* Configuration class to hold local file paths.
* Class to hold URLs of NOAA/NWS RSS feeds.

24 Jul 2020
"""
import os

import logger


class Paths():
    """
    Class to hold local paths.

    ***IMPORTANT***
    User must change the 'base_path' variable.
    """
    base_path = '/home/mnichol3/code/wx-scripts/projects/noaa-rss'
    logs    = os.path.join(base_path, 'logs')
    raw_rss = os.path.join(base_path, 'raw_rss')
    rss_out = os.path.join(base_path, 'rss_out')


class Feeds():
	"""
	Class to hold NOAA RSS URLs.
	"""
	twdat = 'https://www.nhc.noaa.gov/xml/TWDAT.xml'         # NHC Tropical Weather Discussion - Atlantic
	twdep = 'https://www.nhc.noaa.gov/xml/TWDEP.xml'         # NHC Tropical Weather Discussion - EastPac
	reprpd = 'https://www.nhc.noaa.gov/xml/REPRPD.xml'       # NHC Weather Recon Flights Plan of the Day
	spcmd = 'http://www.spc.noaa.gov/products/spcmdrss.xml'  # SPC Mesoscale Discussions
	spcac = 'http://www.spc.noaa.gov/products/spcacrss.xml'  # SPC Convective Outlooks
