try:
    import collectd
    collectd_present = True
except ImportError:
    collectd_present = False

from .plugin import HAProxyPlugin

version_info = (1, 0, 1)

__version__ = ".".join(map(str, version_info))


if collectd_present:
    HAProxyPlugin.register(collectd)
