import errno
import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from mock import patch, Mock

from collectd_haproxy.connection import HAProxySocket


class HAProxySocketTests(unittest.TestCase):

    def setUp(self):
        super(HAProxySocketTests, self).setUp()

        self.connected_to = None
        self.response_chunks = []

        def get_next_response_chunk(*args):
            chunk = self.response_chunks.pop(0)
            if isinstance(chunk, Exception):
                raise chunk
            else:
                return chunk

        socket_patcher = patch("collectd_haproxy.connection.socket")

        mock_socket = socket_patcher.start()
        self.addCleanup(socket_patcher.stop)

        self.socket = mock_socket.socket.return_value

        self.socket.recv.side_effect = get_next_response_chunk

    def test_send_command_connection_refused(self):
        collectd = Mock()

        self.socket.connect.side_effect = IOError(errno.ECONNREFUSED, "")

        s = HAProxySocket(collectd, "/var/run/sock.sock")

        result = s.send_command("a command")

        self.socket.connect.assert_called_once_with("/var/run/sock.sock")
        self.assertEqual(result, None)

        collectd.error.assert_called_once_with(
            "Connection refused.  Is HAProxy running?"
        )

    def test_send_command_othererror_connecting(self):
        collectd = Mock()

        self.socket.connect.side_effect = IOError(errno.ENETUNREACH)

        s = HAProxySocket(collectd, "/var/run/sock.sock")

        with self.assertRaises(IOError):
            s.send_command("a command")

    def test_send_command_unreliable_network(self):
        collectd = Mock()

        self.response_chunks = [
            IOError(errno.EAGAIN, ""),
            b"this is\n",
            b"a\n",
            IOError(errno.EINTR, ""),
            b" fake response\n\n",
            None
        ]

        s = HAProxySocket(collectd, "/var/run/sock.sock")

        result = s.send_command("a command")

        self.socket.sendall.assert_called_once_with(b"a command\n")

        self.assertEqual(
            result,
            """this is
a
 fake response"""
        )

    def test_send_command_error_when_sending(self):
        collectd = Mock()

        self.response_chunks = [
            IOError(errno.ECONNREFUSED, ""),
        ]

        s = HAProxySocket(collectd, "/var/run/sock.sock")

        with self.assertRaises(IOError):
            s.send_command("a command")

    def test_send_command_unknown_command(self):
        collectd = Mock()

        self.response_chunks = [b"Unknown command.\n", None]

        s = HAProxySocket(collectd, "/var/run/sock.sock")

        result = s.send_command("a command")

        self.assertEqual(result, "")

        collectd.error.assert_called_once_with(
            "Unknown HAProxy command: a command"
        )

    def test_send_command_permission_denied(self):
        collectd = Mock()

        self.response_chunks = [b"Permission denied.\n", None]

        s = HAProxySocket(collectd, "/var/run/sock.sock")

        result = s.send_command("other command")

        self.assertEqual(result, "")

        collectd.error.assert_called_once_with(
            "Permission denied for command: other command"
        )

    def test_send_command_unknown_backend(self):
        collectd = Mock()

        self.response_chunks = [b"No such backend.\n", None]

        s = HAProxySocket(collectd, "/var/run/sock.sock")

        result = s.send_command("restart app09")

        self.assertEqual(result, "")

        collectd.error.assert_called_once_with(
            "No such server: 'restart app09'"
        )

    @patch.object(HAProxySocket, "send_command")
    def test_gen_info(self, send_command):
        send_command.return_value = """Version: 1.6.6
CurrConns: 20
OtherInfo: ok"""

        s = HAProxySocket(Mock(), "/var/run/sock.sock")

        self.assertEqual(
            list(s.gen_info()),
            [
                ("Version", "1.6.6"),
                ("CurrConns", "20"),
                ("OtherInfo", "ok"),
            ]
        )

        send_command.assert_called_once_with("show info")

    @patch.object(HAProxySocket, "send_command")
    def test_gen_info_no_legit_response(self, send_command):
        send_command.return_value = None

        s = HAProxySocket(Mock(), "/var/run/sock.sock")

        self.assertEqual(list(s.gen_info()), [])

    @patch.object(HAProxySocket, "send_command")
    def test_gen_stats_no_legit_response(self, send_command):
        send_command.return_value = None

        s = HAProxySocket(Mock(), "/var/run/sock.sock")

        result = s.gen_stats(
            include_frontends=True,
            include_backends=True,
            include_servers=True
        )

        self.assertEqual(list(result), [])

    @patch.object(HAProxySocket, "send_command")
    def test_gen_stats__frontend_backend_server(self, send_command):
        send_command.return_value = None

        s = HAProxySocket(Mock(), "/var/run/sock.sock")

        result = s.gen_stats(
            include_frontends=True,
            include_backends=True,
            include_servers=True
        )

        list(result)

        send_command.assert_called_once_with("show stat -1 7 -1")

    @patch.object(HAProxySocket, "send_command")
    def test_gen_stats__backend_server(self, send_command):
        send_command.return_value = None

        s = HAProxySocket(Mock(), "/var/run/sock.sock")

        result = s.gen_stats(
            include_frontends=False,
            include_backends=True,
            include_servers=True
        )

        list(result)

        send_command.assert_called_once_with("show stat -1 6 -1")

    @patch.object(HAProxySocket, "send_command")
    def test_gen_stats__frontend_server(self, send_command):
        send_command.return_value = None

        s = HAProxySocket(Mock(), "/var/run/sock.sock")

        result = s.gen_stats(
            include_frontends=True,
            include_backends=False,
            include_servers=True
        )

        list(result)

        send_command.assert_called_once_with("show stat -1 5 -1")

    @patch.object(HAProxySocket, "send_command")
    def test_gen_stats__frontend_backend(self, send_command):
        send_command.return_value = None

        s = HAProxySocket(Mock(), "/var/run/sock.sock")

        result = s.gen_stats(
            include_frontends=True,
            include_backends=True,
            include_servers=False
        )

        list(result)

        send_command.assert_called_once_with("show stat -1 3 -1")

    @patch.object(HAProxySocket, "send_command")
    def test_gen_stats__frontend(self, send_command):
        send_command.return_value = None

        s = HAProxySocket(Mock(), "/var/run/sock.sock")

        result = s.gen_stats(
            include_frontends=True,
            include_backends=False,
            include_servers=False
        )

        list(result)

        send_command.assert_called_once_with("show stat -1 1 -1")

    @patch.object(HAProxySocket, "send_command")
    def test_gen_stats__backend(self, send_command):
        send_command.return_value = None

        s = HAProxySocket(Mock(), "/var/run/sock.sock")

        result = s.gen_stats(
            include_frontends=False,
            include_backends=True,
            include_servers=False
        )

        list(result)

        send_command.assert_called_once_with("show stat -1 2 -1")

    @patch.object(HAProxySocket, "send_command")
    def test_gen_stats__servers(self, send_command):
        send_command.return_value = None

        s = HAProxySocket(Mock(), "/var/run/sock.sock")

        result = s.gen_stats(
            include_frontends=False,
            include_backends=False,
            include_servers=True
        )

        list(result)

        send_command.assert_called_once_with("show stat -1 4 -1")

    @patch.object(HAProxySocket, "send_command")
    def test_gen_stats(self, send_command):
        example_stats = None
        example_stats_file = os.path.join(
            os.path.dirname(__file__), "./example_stats.csv"
        )

        with open(example_stats_file, "r") as fd:
            example_stats = fd.read()

        send_command.return_value = example_stats.rstrip("\n")

        s = HAProxySocket(Mock(), "/var/run/sock.sock")

        result = s.gen_stats(
            include_frontends=True,
            include_backends=True,
            include_servers=True
        )

        result = list(result)

        proxy_name, values = result[0]

        self.assertEqual(proxy_name, "frontend")

        self.assertEqual(
            values,
            {
                "": "",
                "act": "",
                "bck": "",
                "bin": "16099928579",
                "bout": "10523206007",
                "check_code": "",
                "check_duration": "",
                "check_status": "",
                "chkdown": "",
                "chkfail": "",
                "cli_abrt": "",
                "comp_byp": "0",
                "comp_in": "0",
                "comp_out": "0",
                "comp_rsp": "0",
                "ctime": "",
                "downtime": "",
                "dreq": "0",
                "dresp": "0",
                "econ": "",
                "ereq": "44092",
                "eresp": "",
                "hanafail": "",
                "hrsp_1xx": "0",
                "hrsp_2xx": "1793812",
                "hrsp_3xx": "677495",
                "hrsp_4xx": "59183",
                "hrsp_5xx": "1495",
                "hrsp_other": "224",
                "iid": "2",
                "last_agt": "",
                "last_chk": "",
                "lastchg": "",
                "lastsess": "",
                "lbtot": "",
                "pid": "1",
                "qcur": "",
                "qlimit": "",
                "qmax": "",
                "qtime": "",
                "rate": "18",
                "rate_lim": "0",
                "rate_max": "64",
                "req_rate": "20",
                "req_rate_max": "62",
                "req_tot": "2532219",
                "rtime": "",
                "scur": "41",
                "sid": "0",
                "slim": "50000",
                "smax": "103",
                "srv_abrt": "",
                "status": "OPEN",
                "stot": "2532247",
                "svname": "FRONTEND",
                "throttle": "",
                "tracked": "",
                "ttime": "",
                "type": "0",
                "weight": "",
                "wredis": "",
                "wretr": "",
            }
        )
