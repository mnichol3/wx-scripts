"""
Python 3.6

Main file for the NOAA RSS scripts.

27 Jul 2020
"""
import argparse

import logger
import parser
from config import Feeds, Paths


def init_args():
    """
    Initialize a new argparse parser.

    Parameters
    ----------
    None.

    Returns
    -------
    argparse.ArgumentParser object

    Args
    ----
    -f, --feed; str or list of str
        RSS feeds to retrieve and parse.
        Currently availible feeds:
            * 'twdat'  - NHC Tropical Weather Discussion - Atlantic
        	* 'twdep'  - NHC Tropical Weather Discussion - EastPac
        	* 'reprpd' - NHC Weather Recon Flights Plan of the Day
        	* 'spcmd'  - SPC Mesoscale Discussions
        	* 'spcac'  - SPC Convective Outlooks
    -l, --log_lvl; optional str
        Sets the logging log level. Valid args: 'debug', 'info', 'warn', 'error', 'critical'.
    """
    parse_desc = """Retrieve NOAA RSS feeds for NHC, SPC, and AWC text products."""

    parser = argparse.ArgumentParser(description=parse_desc)

    parser.add_argument('-f', '--feed', dest='feeds', required=True,
                        action='store', nargs='+', help='<Required> RSS feeds to parse.')

    parser.add_argument('-l', '--log_lvl', dest='log_level', required=False,
                        action='store', type=str, default='debug',
                        help=('<Optional> Set the logging level. Options are "debug",'
                              '"info", "warning", "error", "critical". Default level is "debug"'))
    return parser


def main():
    # Initialize cmd arg parser and parse args
    args = init_args()
    args = args.parse_args()
    # Initialize main log
    log = logger.init_logger(Paths.logs, 'main_log', args.log_level)
    logger.log_msg('main_log', 'Log created.', 'debug')
    # Iterate over the list of rss feed args and parse each one
    for feed in args.feeds:
        feed_url = getattr(Feeds, feed)
        parser.RssAggregator(feed_url)


if __name__ == '__main__':
    main()
