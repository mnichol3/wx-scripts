"""
Python 3.6

This file contains functions to initialize new logger(s) for RSS parsing and
dissemination.

24 Jul 2020
"""
import logging
import os
from datetime import datetime

def init_logger(log_dir, log_name, log_level='debug'):
    """
    Initialize a new logger.

    Log filename is its timestamp (YYYYMMDD_HHMM). The log is written to
    the sundirectory within the log_dir directory corresponding to its RSS
    feed type.
    Ex: the log for a TWDAT RSS feed parsing on 1030z 24 Jul 2020 is written to:
        /log_dir/twdat/20200724_1030.log

    Parameters
    ----------
    log_dir : str
        Path of the log directory.
    log_name : str
        Name of the logger object. Will also be used as the log file name.
    log_level : str, optional
        Logging level. Default is 'debug'.

    Returns
    -------
    logger : logging.Logger instance
    """
    log_levels = {'debug': logging.DEBUG,
                  'info' : logging.INFO,
                  'warn' : logging.WARNING,
                  'error': logging.ERROR,
                  'critical': logging.CRITICAL
                 }

    if not is.path.isdir(log_dir):
        os.mkdir(log_dir)
    timestamp = parse_log_datetime()
    log_fname = timestamp + '.log'
    log_path = os.path.join(log_dir, log_name, log_fname)
    log_format = logging.Formatter("%(asctime)s %(levelname)6s: %(message)s", "%Y-%m-%d %H:%M:%S")
    handler = logging.FileHandler(log_path)
    handler.setFormatter(log_format)
    logger = logging.getLogger(log_name)
    logger.setLevel(log_levels[level])
    logger.addHandler(handler)
    logger.info("Log created!\n")
    return logger

def remove_old_logs(log_dir):
    """
    Walk through the RSS log subdirectories and delete log files that are
    older than 30 days.

    Parameters
    ----------
    log_dir : str
        Path to the log directory.

    Returns
    -------
    None.
    """
    now = datetime.now()
    subdirs = [d for d in os.listdir(log_dir) if os.path.isdir(d)]
    for subdir in subdirs:
        curr_dir = os.path.join(log_dir, subdir)
        log_files = [f for f in os.listdir(curr_dir) if os.path.isfile(os.path.join(curr_dir, f))]
        for log_file in log_files:
            curr_file = os.path.join(curr_dir, log_file)
            c_time = os.path.getctime(curr_file)
            if (now - c_time) // (24 * 3600) >= 30:
                os.remove(curr_file)

def parse_log_datetime():
    """
    Parse the datetime (UTC) string to be included in the log filename.

    Parameters
    ----------
    None.

    Returns
    -------
    str : datatime string.
        Format: YYYYMMDD_HHMM
    """
    return datetime.utcnow().strftime('%Y%m%d_%H%M')
