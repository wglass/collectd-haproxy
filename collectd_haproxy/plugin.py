from .metrics import METRIC_XREF
from .connection import HAProxySocket
from .compat import iteritems, coerce_long


class HAProxyPlugin(object):
    """
    The plugin class, workhorse that liasons between collectd and HAProxy.

    Rather than being instantiated directly, the `register()` method should
    be used to make a plugin, since it both creates an instance *and* takes
    care of the proper callback registration.
    """

    name = "haproxy"

    def __init__(self, collectd):
        """
        HAProxy Plugin constructor

        Since the collectd module is only available when the plugin is running
        in collectd's python process we use some dependency injection here.

        :param collectd: The collectd module.
        :type collectd: module
        """
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
        """
        Registers the plugin's callbacks with the given collectd module.

        Since the collectd module is only available when the plugin is running
        in collectd's python process we use some dependency injection here.

        :param collectd: The collectd module.
        :type collectd: module
        """
        instance = cls(collectd)

        collectd.register_config(instance.configure, name=cls.name)
        collectd.register_init(instance.initialize, name=cls.name)
        collectd.register_read(instance.read, name=cls.name)

    def configure(self, config):
        """
        The 'configure' collectd callback for the plugin.

        Iterates over the config object's `children` attribute and sets any
        applicable attributes on the plugin instance.

        :param config: The collectd Config instance.  Passed in automatically
            by collectd itself.
        :type config: collect.Config
        """
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

        if not self.socket_file_path:
            self.collectd.error("No HAProxy socket path configured!")
            self.collectd.unregister_init(self.initialize)
            self.collectd.unregister_read(self.read)

    def initialize(self):
        """
        The 'initialize' collectd callback for the plugin.

        This callback fires after the 'config' one but before the 'read' one
        gets added to the loop.

        Instantiates a `collectd.Values` for each known metric (these are used
        to dispatch actual values to collectd) as well as sets up the
        `HAProxySocket` for fetching the values.
        """
        self.collectd.debug("initializing")
        self.metrics = {
            metric_name: self.collectd.Values(
                plugin=self.name, type=xref[1], type_instance=xref[0]
            )
            for metric_name, xref in iteritems(METRIC_XREF)
        }

        self.socket = HAProxySocket(self.collectd, self.socket_file_path)

        self.collectd.info("Using socket path '%s'" % self.socket_file_path)

    def read(self):
        """
        The 'read' collectd callback for the plugin.

        Simple method that calls `collect_info()` and/or `collect_stats()`
        based on the configuration.
        """
        if self.include_info:
            self.collect_info()
        if self.include_stats:
            self.collect_stats()

    def collect_info(self):
        """
        Method for sending HAProxy "info" metrics to collectd.

        Iterates over the metric names and values provided by the socket and
        dispatches each known one to collectd.
        """
        self.collectd.debug("reading info")
        for label, value in self.socket.gen_info():
            if label not in self.metrics:
                continue

            self.metrics[label].dispatch(
                plugin_instance=self.name, values=[value]
            )

    def collect_stats(self):
        """
        Method for sending HAProxy "info" metrics to collectd.

        Iterates over the metric names and values provided by the socket,
        checking that the metric is a known one and taking care of numeric
        coercion before dispatching to collectd.
        """
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
