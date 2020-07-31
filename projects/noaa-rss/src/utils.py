"""
Python 3.6

Utility/common functions.

28 Jul 2020
"""
import calendar
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

    Raises
    ------
    None.
    """
    return datetime.utcnow().strftime('%Y%m%d_%H%M')


def get_datetime():
    """
    Get the current datetime (UTC) as a datetime object.

    Parameters
    ----------
    None.

    Returns
    -------
    Datetime object

    Raises
    ------
    None.
    """
    return datetime.utcnow()


def last_day_of_month(dt_obj):
    """
    Determine if the day of the given datetime object is the last day in the
    respective month.

    Parameters
    ----------
    dt_obj : Datetime object

    Returns
    -------
    bool

    Raises
    ------
    None.
    """
    num_days = calendar.monthrange(dt_obj.year, dt_obj.month)[1]
    return num_days == dt_obj.day
