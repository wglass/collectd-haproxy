try:
    import collectd
    collectd.register_config
    collectd_present = True
except (ImportError, AttributeError):
    collectd_present = False

from .plugin import HAProxyPlugin

version_info = (1, 1, 1)

__version__ = ".".join(map(str, version_info))


if collectd_present:
    HAProxyPlugin.register(collectd)
