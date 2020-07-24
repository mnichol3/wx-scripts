# Python 3.6
# Simple RSS feed parser utilizing the feedparser library.

import feedparser as fp
import logging


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
		print('Parsing {} - {}'.format(self.feed_url, parsed_feed.feed.get('title', '')))
		print(parsed_feed.feed.get('description', ''))
		pub_datetime = parsed_feed.feed.get('published', '')
		print('Published {}'.format(pub_datetime))
		#print(parsed_feed)

		for feed_entry in parsed_feed.entries:
			the_text = feed_entry.get("description", "").replace('<br />', '')
			print(the_text)


def main():
	url = 'https://w1.weather.gov/xml/current_obs/KMRY.rss'
	rss_obj = RssAggregator(Feeds.twdat)


if __name__ == '__main__':
	main()
