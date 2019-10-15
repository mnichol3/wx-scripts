"""
Author: Matt Nicholson

This file holds utility functions for date/time manipulation and calculation
"""
import datetime



def calc_date_chunks(start, end):
    """
    Creates 6-hr time chunks

    Parameters
    ----------
    start : str
        Format: 'MM-DD-YYYY-HH:MM'
    end : str
        Format: 'MM-DD-YYYY-HH:MM'

    Returns
    --------
    chunks : list of tuples of (str, str)

    Dependencies
    -------------
    > datetime
    """
    chunks = []

    start = datetime.datetime.strptime(start, '%m-%d-%Y-%H:%M')
    prev = start
    end = datetime.datetime.strptime(end, '%m-%d-%Y-%H:%M')

    while (prev <= end):
        # Increment 6 hours
        curr = prev + datetime.timedelta(seconds=21600)

        chunks.append((prev.strftime('%m-%d-%Y-%H:%M'), curr.strftime('%m-%d-%Y-%H:%M')))
        prev = curr

    """
    Adjust the last tuple incase the time period doesnt divide evenly into
    6-hr periods

    Ex
    ---
    Unadjusted:
        in:  calc_date_chunks('09-01-2019-15:00', '09-06-2019-13:00')[-1]
        out: ('09-06-2019-09:00', '09-06-2019-15:00')

    Adjusted:
        in:  calc_date_chunks('09-01-2019-15:00', '09-06-2019-13:00')[-1]
        out: ('09-06-2019-09:00', '09-06-2019-13:00')

    """
    if (datetime.datetime.strptime(chunks[-1][1], '%m-%d-%Y-%H:%M') > end):
        chunks = chunks[:-1]
        prev = prev - datetime.timedelta(seconds=21600)
        chunks.append((prev.strftime('%m-%d-%Y-%H:%M'), end.strftime('%m-%d-%Y-%H:%M')))

    return chunks
