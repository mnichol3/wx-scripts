"""
Python 3.6

Class to represent a parsed RSS feed to save locally.

30 Jul 2020
"""
import json
import feedparser as fp
import re
import os
import sys
from datetime import timedelta

import logger
import parsed_rss
import utils
from config import Feeds, Paths


class ParsedRSS:

    def __init__(self, feed_obj):
        """
        Parameters
        ----------
        feed_obj : RSSFeed object
            RSSFeed instance representing the feed to parse.

        Attributes
        ----------
        retr_time : datetime obj
            Time the RSS feed was retrieved & parsed.
        feed_url : str
            RSS feed URL.
        short_name : str
            Abbreviation of the product contained in the RSS feed.
        long_name : str
            Long name describing the product contained in the RSS feed.
        prod_time : datetime object
            Time the product/forecast in the RSS feed was produced.
        rss_text : str
            Parsed RSS feed text.
        pub_office : str
            Office/agency that produced the RSS feed.
        file_path : str
            Path of the json file the object will be saved to, including filename.
        file_name : str
            Name of the json file the object will be saved to.
        """
        self.feed_url   = feed_obj.url
        self.short_name) = feed_obj.short_name
        self.long_name  = feed_obj.long_name
        self.pub_office = feed_obj.office
        self.prod_time  = None
        self.retr_time  = None
        self.rss_text   = None
        self.file_path  = None
        self.file_name  = None
        self.parse()

    def parse(self):
        """
        Parse the RSS feed.

        Parameters
        ----------
        None.

        Returns
        -------
        """
        # Parse the RSS feed text
        parsed_feed = fp.parse(self.feed_url)
        msg = 'Parsing {} - {}'.format(self.feed_url, parsed_feed.feed.get('title', ''))
        logger.log_msg('main_log', msg, 'debug')
        # Get the current datetime stamp
        self.retr_time = get_datetime()
        for feed_entry in parsed_feed.entries:
            rss_text = feed_entry.get("description", "")
            # Remove any HTML/XML tags
            self.rss_text = self._scrub_tags(rss_text)
            # Get the product forecast/valid time from the parsed text
            self.prod_time = self.get_prod_time()
        self.gen_filepath()

    def get_prod_time(self):
        """
        Get the forecast/valid time of the product contained in the RSS feed.

        Parameters
        ----------
        None.

        Returns
        -------
        datetime object
        """
        if self.short_name == 'twdat' or self.short_name == 'twdep':
            prod_re = re.compile(r'KNHC (\d{2})(\d{4})')
        elif self.short_name == 'reprpd':
            prod_re = re.compile(r'VALID (\d{2})/(\d{4}Z)')
        elif self.short_name == 'spcmd' or self.short_name == 'spcac':
            prod_re = re.compile(r'Valid (\d{2})(\d{4}Z)')
        prod_dt = prod_re.search(self.parsed_text)
        try:
            prod_day  = prod_dt.group(1)
            prod_time = prod_dt.group(2)
        except:
            logger.log_msg('main_log', sys.exc_info()[0], 'error')
            logger.log_msg('main_log', 'Unable to parse prod time, using retr time.', 'warning')
            return self.retr_time
        # Construct the rest of the date for prod_date.
        # Problems can arise with for products issued late in the day when it
        # is already the proceeding day in UTC time but not local system time.
        prod_hr = int(prod_time[:2])
        prod_mn = int(prod_time[2:])
        prod_dt = self.retr_time.replace(hour=prod_hr, minute=prod_mn)
        if int(prod_day) != self.retr_time.day:
            prod_dt = prod_dt + timedelta(days=1)
        return prod_dt

    def to_file(self):
        """
        Write an instance to a json file.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        if self.file_path:
            logger.log_msg('main_log', 'Writing {}'.format(self.file_path), 'debug')
            with open(self.file_path, 'w') as outfile:
                json.dump(self.__dict__, outfile)
        else:
            logger.log_msg('main_log', 'Cannot parse json filename {}'.format(self.file_path), 'warning')

    def gen_filepath(self):
        """
        Generate the filename & path of the directory that the object will be serialized to.

        Parameters
        ---------
        None.

        Returns
        -------
        None.
        """
        datetime_stamp = self.prod_time.strftime('%Y%m%d_%H%M')
        self.file_name = '{}-{}.json'.format(self.short_name, datetime_stamp)
        self.file_path = os.path.join(Paths.rss, self.short_name, self.file_name)
