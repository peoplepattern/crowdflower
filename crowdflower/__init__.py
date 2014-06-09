import os
# here is the directory containing this __init__.py file
here = os.path.dirname(__file__) or os.curdir
# root is the directory containing `here`, i.e., the directory containing setup.py
root = os.path.dirname(os.path.abspath(here))


import pkg_resources
__version__ = pkg_resources.get_distribution('crowdflower').version


import logging
logger = logging.getLogger('crowdflower')


# import helper
from connection import Connection
