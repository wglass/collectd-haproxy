try:
    import unittest2 as unittest
except ImportError:
    import unittest

from mock import Mock, patch, call

from collectd_haproxy.plugin import HAProxyPlugin


class HAProxyPluginTests(unittest.TestCase):

    def test_default_flags(self):
        collectd_module = Mock()

        p = HAProxyPlugin(collectd_module)

        self.assertEqual(p.collectd, collectd_module)

        self.assertEqual(p.include_info, True)
        self.assertEqual(p.include_stats, True)
        self.assertEqual(p.include_frontends, True)
        self.assertEqual(p.include_backends, True)
        self.assertEqual(p.include_servers, True)

    def test_register_callbacks(self):
        collectd = Mock()

        HAProxyPlugin.register(collectd)

        args, kwargs = collectd.register_config.call_args
        callback_method, = args

        self.assertIsInstance(callback_method.__self__, HAProxyPlugin)
        self.assertEqual(callback_method.__name__, "configure")

        self.assertEqual(kwargs, dict(name="haproxy"))

        args, kwargs = collectd.register_init.call_args
        callback_method, = args

        self.assertIsInstance(callback_method.__self__, HAProxyPlugin)
        self.assertEqual(callback_method.__name__, "initialize")

        self.assertEqual(kwargs, dict(name="haproxy"))

        args, kwargs = collectd.register_read.call_args
        callback_method, = args

        self.assertIsInstance(callback_method.__self__, HAProxyPlugin)
        self.assertEqual(callback_method.__name__, "read")

        self.assertEqual(kwargs, dict(name="haproxy"))

    def test_configure_sets_flags(self):
        collectd = Mock()

        config = Mock(
            children=[
                Mock(key="Socket", values=("/var/run/sock.sock",)),
                Mock(key="IncludeInfo", values=(False,)),
                Mock(key="IncludeStats", values=(True,)),
                Mock(key="IncludeFrontendStats", values=(True,)),
                Mock(key="IncludeBackendStats", values=(True,)),
                Mock(key="IncludeServerStats", values=(False,)),
            ]
        )

        p = HAProxyPlugin(collectd)

        p.configure(config)

        self.assertEqual(p.socket_file_path, "/var/run/sock.sock")

        self.assertEqual(p.include_info, False)
        self.assertEqual(p.include_stats, True)
        self.assertEqual(p.include_frontends, True)
        self.assertEqual(p.include_backends, True)
        self.assertEqual(p.include_servers, False)

    def test_configure_unknown_config_option(self):
        collectd = Mock()

        config = Mock(
            children=[
                Mock(key="Socket", values=("/var/run/sock.sock",)),
                Mock(key="FakeThing", values=("a_value",)),
            ]
        )

        p = HAProxyPlugin(collectd)

        p.configure(config)

        self.assertEqual(p.socket_file_path, "/var/run/sock.sock")

        self.assertEqual(p.include_info, True)
        self.assertEqual(p.include_stats, True)
        self.assertEqual(p.include_frontends, True)
        self.assertEqual(p.include_backends, True)
        self.assertEqual(p.include_servers, True)

        self.assertFalse(collectd.unregister_init.called)
        self.assertFalse(collectd.unregister_read.called)

    def test_configure_with_no_socket(self):
        collectd = Mock()

        config = Mock(
            children=[
                Mock(key="FakeThing", values=("a_value",)),
            ]
        )

        p = HAProxyPlugin(collectd)

        p.configure(config)

        self.assertEqual(p.socket_file_path, None)

        collectd.unregister_init.assert_called_once_with(p.initialize)
        collectd.unregister_read.assert_called_once_with(p.read)

    @patch("collectd_haproxy.plugin.HAProxySocket")
    def test_initialize_sets_socket_attribute(self, HAProxySocket):
        collectd = Mock()

        p = HAProxyPlugin(collectd)
        p.socket_file_path = "/var/run/asdf.sock"

        p.initialize()

        self.assertEqual(p.socket, HAProxySocket.return_value)
        HAProxySocket.assert_called_once_with(collectd, "/var/run/asdf.sock")

    @patch(
        "collectd_haproxy.plugin.METRIC_XREF",
        {
            "CurrConns": ("current_connections", "gauge"),
            "hrsp_5xx": ("http_response_5xx", "counter"),
        }
    )
    def test_initialize_sets_up_metrics(self):
        collectd = Mock()

        p = HAProxyPlugin(collectd)

        p.initialize()

        self.assertEqual(
            p.metrics,
            {
                "CurrConns": collectd.Values.return_value,
                "hrsp_5xx": collectd.Values.return_value,
            }
        )

        collectd.Values.assert_has_calls([
            call(
                plugin="haproxy",
                type="gauge", type_instance="current_connections"
            ),
            call(
                plugin="haproxy",
                type="counter", type_instance="http_response_5xx"
            ),
        ], any_order=True)

    @patch.object(HAProxyPlugin, "collect_stats")
    @patch.object(HAProxyPlugin, "collect_info")
    def test_read_collects_info_only_if_flag_set(self, info, stats):
        p = HAProxyPlugin(Mock())

        p.include_info = False

        p.read()

        self.assertFalse(info.called)

        p.include_info = True

        p.read()

        info.assert_called_once_with()

    @patch.object(HAProxyPlugin, "collect_stats")
    @patch.object(HAProxyPlugin, "collect_info")
    def test_read_collects_stats_only_if_flag_set(self, info, stats):
        p = HAProxyPlugin(Mock())

        p.include_stats = False

        p.read()

        self.assertFalse(stats.called)

        p.include_stats = True

        p.read()

        stats.assert_called_once_with()

    @patch("collectd_haproxy.plugin.HAProxySocket")
    def test_collect_info_skips_unknown_metrics(self, HAProxySocket):
        HAProxySocket.return_value.gen_info.return_value = [
            ("CurConns", 10),
            ("hrsp_5xx", 0),
            ("UpstreamErrors", 1),
        ]

        p = HAProxyPlugin(Mock())
        p.metrics = {"CurConns": Mock(), "hrsp_5xx": Mock(), "Fake": Mock()}

        p.socket = HAProxySocket.return_value

        p.collect_info()

        p.metrics["CurConns"].dispatch.assert_called_once_with(
            plugin_instance="haproxy", values=[10],
        )
        p.metrics["hrsp_5xx"].dispatch.assert_called_once_with(
            plugin_instance="haproxy", values=[0],
        )

    @patch("collectd_haproxy.plugin.HAProxySocket")
    def test_collect_stats(self, HAProxySocket):
        HAProxySocket.return_value.gen_stats.return_value = [
            (
                "app_servers",
                {
                    "svname": "app01",
                    "CurrConns": 15,
                    "hrsp_4xx": 3,
                    "MemMax": "120mb",
                    "FakeStatus": "ok",
                }
            ),
            (
                "app_servers",
                {
                    "svname": "app02",
                    "CurrConns": 8,
                    "hrsp_4xx": None,
                    "MemMax": "100mb",
                }
            )
        ]

        p = HAProxyPlugin(Mock())
        p.metrics = {"CurrConns": Mock(), "hrsp_4xx": Mock(), "MemMax": Mock()}

        p.socket = HAProxySocket.return_value

        p.collect_stats()

        p.metrics["CurrConns"].dispatch.assert_has_calls([
            call(plugin_instance="app_servers.app01", values=[15]),
            call(plugin_instance="app_servers.app02", values=[8]),
        ], any_order=True)

        p.metrics["hrsp_4xx"].dispatch.assert_has_calls([
            call(plugin_instance="app_servers.app01", values=[3]),
            call(plugin_instance="app_servers.app02", values=[0]),
        ], any_order=True)

        self.assertFalse(p.metrics["MemMax"].called)
