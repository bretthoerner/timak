from __future__ import absolute_import

import pkg_resources

from .timelines import Timeline


VERSION = tuple(map(int, pkg_resources.get_distribution('timak').version.split('.')))
__version__ = VERSION
