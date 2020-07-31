"""
Python 3.6

This file contains a class to hold project paths.

Moved from config.py due to circular import issues.

31 Jul 2020
"""
import os
from pathlib import Path

import logger
import utils

def get_proj_root():
    """
    Get the project root directory.

    Parameters
    ----------
    None.

    Returns
    -------
    str : Absolute path of project root directory.

    Raises
    ------
    None.
    """
    root = str(Path(os.path.abspath(__file__)).parents[1])
    return root

class Paths():
    """
    Class to hold local paths.

    * root_path : Project's root path.
    * logs : Absolute path of the directory where logs are written.
    * rss  : Absolute path of the directory where parsed RSS json files are written.
    """
    root_path = get_proj_root()
    logs = os.path.join(root_path, 'logs')
    rss  = os.path.join(root_path, 'parsed_rss')
