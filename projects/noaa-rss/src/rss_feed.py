"""
Python 3.6

Class to represent a NOAA RSS Feed.

30 Jul 2020
"""
import parsed_rss

class RSSFeed():

    def __init__(self, short_name, long_name, url, office):
        """
        Constructor.

        Parameters
        ----------
        short_name : str
            RSS product short name. Ex: 'twdat', 'twdep'.
        long_name : str
            RSS product long name. Ex: 'NHC Tropical Weather Discussion - Atlantic'.
        url : str
            RSS feed url.
        office : str
            Office that published the product contained in the RSS feed text.

        Attributes
        ----------
        See "Parameters".
        """
        self.short_name = short_name
        self.long_name  = long_name
        self.url        = url
        self.office     = office

    def parse(self):
        """
        Parse the RSS feed and return a ParsedRSS object.

        Parameters
        ----------
        None.

        Returns
        -------
        ParsedRSS object.

        Raises
        ------
        None.
        """
        return parsed_rss.ParsedRSS(self)

    def pretty_print(self):
        """
        Pretty print an RSSFeed instance.

        Parameters
        ----------
        None.

        Returns
        -------
        None.

        Raises
        ------
        None.
        """
        print('<--- RSS Feed Object --->')
        print('    {}'.format(self.short_name.upper()))
        print('    {}'.format(self.long_name))
        print('    {}\n'.format(self.url))

    def __repr__(self):
        return "<RSSFeed object - {} {}>".format(self.short_name, self.url)
