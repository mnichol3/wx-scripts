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
