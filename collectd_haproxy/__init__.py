try:
    import collectd
    collectd.register_config  # pragma: no cover
    collectd_present = True  # pragma: no cover
except (ImportError, AttributeError):
    collectd_present = False

from .plugin import HAProxyPlugin

version_info = (1, 2, 0)

__version__ = ".".join(map(str, version_info))


if collectd_present:
    HAProxyPlugin.register(collectd)  # pragma: no cover
