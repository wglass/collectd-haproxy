from .metrics import METRIC_XREF
from .connection import HAProxySocket
from .compat import iteritems, coerce_long


class HAProxyPlugin(object):

    def __init__(self, collectd):
        self.collectd = collectd

        self.socket_file_path = None

        self.include_info = True
        self.include_stats = True
        self.include_frontends = True
        self.include_backends = True
        self.include_servers = True

        self.socket = None
        self.metrics = {}
        self.stats_type_mask = 0

    @classmethod
    def register(cls, collectd):
        instance = cls(collectd)

        collectd.register_config(instance.configure)
        collectd.register_init(instance.initialize)
        collectd.register_read(instance.read)

    def configure(self, config):
        self.collectd.debug("configuring")
        for node in config.children:
            if node.key == "Socket":
                self.socket_file_path = node.values[0]
            elif node.key == "IncludeInfo":
                self.include_info = bool(node.values[0])
            elif node.key == "IncludeStats":
                self.include_stats = bool(node.values[0])
            elif node.key == "IncludeFrontendStats":
                self.include_frontends = bool(node.values[0])
            elif node.key == "IncludeBackendStats":
                self.include_backends = bool(node.values[0])
            elif node.key == "IncludeServerStats":
                self.include_servers = bool(node.values[0])
            else:
                self.collectd.warn("Unknown config option: '%s'" % node.key)

    def initialize(self):
        self.collectd.debug("initializing")
        self.metrics = {
            metric_name: self.collectd.Values(
                plugin="haproxy", type=xref[1], type_instance=xref[0]
            )
            for metric_name, xref in iteritems(METRIC_XREF)
        }

        self.socket = HAProxySocket(self.socket_file_path)

        self.collectd.info("Using socket path '%s'" % self.socket_file_path)

    def read(self):
        if self.include_info:
            self.collect_info()
        if self.include_stats:
            self.collect_stats()

    def collect_info(self):
            self.collectd.debug("reading info")
            for label, value in self.socket.gen_info():
                if label not in self.metrics:
                    continue

                self.metrics[label].dispatch(
                    plugin_instance="haproxy", values=[value]
                )

    def collect_stats(self):
        self.collectd.debug("reading stats")

        stats = self.socket.gen_stats(
            self.include_frontends, self.include_backends, self.include_servers
        )
        for proxy_name, values in stats:
            server_name = values.pop("svname")
            plugin_instance = ".".join([proxy_name, server_name])

            for label, value in iteritems(values):
                if label not in self.metrics:
                    continue
                if not value:
                    value = 0

                try:
                    value = coerce_long(value)
                except (TypeError, ValueError):
                    continue

                self.metrics[label].dispatch(
                    plugin_instance=plugin_instance, values=[value]
                )
