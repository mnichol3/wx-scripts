"""
Python 3.6

Utility/common functions.

28 Jul 2020
"""
from datetime import datetime


def datetime_stamp():
    """
    Parse the datetime (UTC) string. Format: YYYYMMDD_HHMM.

    Parameters
    ----------
    None.

    Returns
    -------
    str : datatime string.
        Format: YYYYMMDD_HHMM
    """
    return datetime.utcnow().strftime('%Y%m%d_%H%M')


def is_nhc_feed(feed_url):
    """
    Determine whether an RSS feed is from the National Hurricane Center (NHC).

    Parameters
    ----------
    feed_url : str
        RSS feed URL.

    Returns
    -------
    bool
    """
    return ('nhc' in feed_url)
