"""
Python 3.6
Simple NOAA RSS feed parser utilizing the feedparser library.

17 Jul 2020
"""
import feedparser as fp
import re
import os
import sys

import logger
import parsed_rss
from config import Feeds, Paths
from utils import datetime_stamp, is_nhc_feed


class RssAggregator():
	"""
	RSS Aggregator class.
	"""
	feed_url  = ''
	feed_name = ''

	def __init__(self, rss_feed):
		self.feed_name = rss_feed
		self.feed_url  = Feeds[rss_feed].url
		self.parse()

	def parse(self, write=True):
		"""
		Parse the RSS feed using the feedparser.parse() function.

		Parameters
		----------
		write : bool, optional
			If True, the parsed RSS feed will be written to a text file.
			Default is True.

		Returns
		-------
		None.
		"""
		parsed_feed = fp.parse(self.feed_url)
		msg = 'Parsing {} - {}'.format(self.feed_url, parsed_feed.feed.get('title', ''))
		logger.log_msg('main_log', msg, 'debug')
		print(parsed_feed.feed.get('description', ''))
		pub_datetime = parsed_feed.feed.get('RSS text published', '')
		dt_stamp = datetime_stamp()
		logger.log_msg('main_log','Published {}'.format(pub_datetime), 'debug')
		for feed_entry in parsed_feed.entries:
			rss_text = feed_entry.get("description", "")
			rss_text = self._scrub_tags(rss_text)
			print(rss_text)
			print('============================================================')
			print('============================================================')
			print('============================================================')
			# if is_nhc_feed(self.feed_name):
			# 	prod_time = self._get_nhc_time(parsed_text)
			# else:
			# 	prod_time = dt_stamp
			# rss_obj = parsed_rss.ParsedRSS(dt_stamp, self.feed_url, self.feed_name,
			#                                prod_time, rss_text, self.get_pub_office())

	def to_file(self, parsed_text, overwrite=False):
		"""
		Write a parsed RSS feed to a txt file. If a file with the same filenam
		already exists, the file will only be overwritten
		Filename format: <rss_feed_name>-YYYYMMDD_HHMM.txt.

		Parameters
		----------
		parsed_text : str
			Parsed RSS text returned by parse().
		overwrite : bool, optional.
			Whether or not to overwrite a file with the same name that already
			exists. Default is to not overwrite the existing file.

		Returns
		-------
		str : Name of the file the parsed RSS feed was written to.
		"""
		if is_nhc_feed(self.feed_name):
			prod_time = self._get_nhc_time(parsed_text)
			fname = self.get_filename(utc_time=prod_time)
		else:
			fname = self.get_filename()
		f_path = os.path.join(Paths.raw_rss, self.feed_name, fname)
		if os.path.exists(f_path):
			# If the RSS file already exists, determine how we're going to proceed
			logger.log_msg('main_log', 'RSS file already exists {}'.format(f_path), 'debug')
			if not overwrite:
				logger.log_msg('main_log', 'RSS overwrite = False; returning'.format(f_path), 'debug')
				return f_path
		logger.log_msg('main_log', 'Writing parsed text to {}'.format(f_path), 'debug')
		with open (f_path, 'w') as rss_out:
			rss_out.write(parsed_text)
		return f_path

	def get_filename(self, utc_time=None):
		"""
		Construct the filename of parsed RSS feed text as its saved locally.

		Parameters
		----------
		utc_time : str, optional
			Forecast/valid time of the product discussed in the RSS feed. If given,
			this time will be used in the filename string instead of the current
			UTC time. Default is to use current UTC time.

		Returns
		-------
		str : Filename. Format: <feed_name>-YYYYMMDD_HHMM.txt
		"""
		t_stamp = datetime_stamp()
		if utc_time:
			date = t_stamp.split('_')[0]
			t_stamp = '{}_{}'.format(date, utc_time)
		fname = '{}-{}.txt'.format(self.feed_name, t_stamp)
		return fname

	def get_pub_office(self):
		"""
		Get the name of the office that published the RSS feed.

		Parameters
		----------
		None.

		Returns
		-------
		str : Office name.
		"""
		ofc_re = re.compile(r'www\.(\w+?)\.')
		office_abbrev = ofc_re.search(self.feed_url)
		if office:
			office = office_abbrev.group(1)
		else:
			logger.log_msg('main_log', 'Unable to parse publishing office for {}'.format(self.feed_url), 'error')
			office = ''
		return office

	def _get_nhc_time(self, rss_text):
		"""
		Get the forecast time of an NHC product RSS feed.

		Parameters
		----------
		rss_text : str
			Parsed RSS feed text.

		Return
		------
		str : Product's forecast time (HHMM, UTC)
			If regex parsing fails, None is returned.
		"""
		time_re = re.compile(r'KNHC \d{2}(\d{4})')
		ret_val = None
		try:
			prod_time = time_re.search(rss_text).group(1)
			if len(prod_time) == 4 and int(prod_time):   # Quick validation
				ret_val = prod_time
			else:
				logger.log_msg('main_log', 'Invalid NHC product time {}; using system time'.format(prod_time), 'warning')
		except:
			logger.log_msg('main_log', sys.exc_info()[0], 'error')
		return ret_val

	def _scrub_tags(self, rss_text):
		"""
		Remove XML/HTML tags from parsed RSS text.

		Parameters
		----------
		rss_text : str
			Parsed RSS text.

		Returns
		-------
		str : RSS text with tags removed
		"""
		import re
		tag_re = re.compile(r'<[^>]+>')
		scrubbed_txt = tag_re.sub('', rss_text)
		return scrubbed_txt
