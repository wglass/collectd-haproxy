version_info = (0, 9, 0)

__version__ = ".".join(map(str, version_info))

import logging

try:
    import collectd
    collectd_present = True
except ImportError:
    collectd_present = False

from .plugin import HAProxyPlugin


if collectd_present:
    HAProxyPlugin.register(collectd)
else:
    logging.warn("No collectd module present.")
