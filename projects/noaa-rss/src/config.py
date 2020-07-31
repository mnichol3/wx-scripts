"""
Python 3.6

File contains:
* Configuration class to hold local file paths.
* Class to hold URLs of NOAA/NWS RSS feeds.

24 Jul 2020
"""
import logger
from rss_feed import RSSFeed

"""
Dictionary containing RSSFeed objects for NOAA RSS Feeds currently implemented.
"""
Feeds = {'twdat'  : RSSFeed('twdat', 'NHC Tropical Weather Discussion - Atlantic', 'https://www.nhc.noaa.gov/xml/TWDAT.xml', 'nhc'),
         'twdep'  : RSSFeed('twdep', 'NHC Tropical Weather Discussion - EastPac', 'https://www.nhc.noaa.gov/xml/TWDEP.xml', 'nhc'),
         'reprpd' : RSSFeed('reprpd', 'NHC Weather Recon Flights Plan of the Day', 'https://www.nhc.noaa.gov/xml/REPRPD.xml', 'nhc'),
         'spcmd'  : RSSFeed('spcmd', 'SPC Mesoscal Discussion', 'http://www.spc.noaa.gov/products/spcmdrss.xml', 'spc'),
         'spcac'  : RSSFeed('spcmd', 'SPC Convective Outlook', 'http://www.spc.noaa.gov/products/spcacrss.xml', 'spc')
         }
