version_info = (1, 0, 0)

__version__ = ".".join(map(str, version_info))

try:
    import collectd
    collectd_present = True
except ImportError:
    collectd_present = False

from .plugin import HAProxyPlugin


if collectd_present:
    HAProxyPlugin.register(collectd)
