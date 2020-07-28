# Python 3.6
# Simple RSS feed parser utilizing the feedparser library.

import feedparser as fp
import re

import logger
from config import Feeds


class RssAggregator():
	"""
	RSS Aggregator class.
	"""
	feed_url = ''

	def __init__(self, rss_url):
		self.feed_url = rss_url
		self.parse()

	def parse(self):
		"""
		Parse the RSS feed using the feedparser.parse() function.

		Parameters
		----------
		None.

		Returns
		-------
		None.
		"""
		parsed_feed = fp.parse(self.feed_url)
		msg = 'Parsing {} - {}'.format(self.feed_url, parsed_feed.feed.get('title', ''))
		logger.log_msg('main_log', msg, 'debug')
		print(parsed_feed.feed.get('description', ''))
		pub_datetime = parsed_feed.feed.get('RSS text published', '')
		logger.log_msg('main_log','Published {}'.format(pub_datetime), 'debug')
		for feed_entry in parsed_feed.entries:
			rss_text = feed_entry.get("description", "")
			rss_text = self.scrub_tags(rss_text)
			print(rss_text)
			print('*' * 60)
			print('*' * 60)
			print('*' * 60)

	def scrub_tags(self, rss_text):
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
