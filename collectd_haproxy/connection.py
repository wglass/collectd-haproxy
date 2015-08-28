try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import errno
import socket


SOCKET_BUFFER_SIZE = 1024


class HAProxySocket(object):
    """
    Class used for interacting with an HAProxy control socket.

    Provides two methods for generating metrics, one for the "info" metrics
    that give process-wide details and the "stats" metrics for individual
    proxies/servers.
    """

    def __init__(self, collectd, socket_file_path):
        """
        The HAProxySocket constructor.

        Since the collectd module is only available when the plugin is running
        in collectd's python process we use some dependency injection here.

        :param collectd: The collectd module.
        :type collectd: module

        :param socket_file_path: Full path to HAProxy's socket file.
        :type socket_file_path: str
        """
        self.collectd = collectd
        self.socket_file_path = socket_file_path

    def send_command(self, command):
        """
        Sends a given command to the HAProxy socket.

        Collects the response (it can arrive in chunks) and then calls the
        `process_command_response` method on the result.

        :param command: The command to send, e.g. "show stat"
        :type command: str
        """
        self.collectd.debug("Connecting to socket %s" % self.socket_file_path)
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(self.socket_file_path)
        except IOError as e:
            if e.errno == errno.ECONNREFUSED:
                self.collectd.error("Connection refused.  Is HAProxy running?")
                return
            else:
                raise

        self.collectd.debug("Running command '%s'" % command)

        sock.sendall((command + "\n").encode())

        buff = StringIO()

        while True:
            try:
                chunk = sock.recv(SOCKET_BUFFER_SIZE)
                if chunk:
                    buff.write(chunk)
                else:
                    break
            except IOError as e:
                if e.errno not in (errno.EAGAIN, errno.EINTR):
                    raise

        sock.close()
        response = buff.getvalue()
        buff.close()

        return self.process_command_response(command, response)

    def process_command_response(self, command, response):
        """
        Takes an HAProxy socket command and its response and either raises
        an appropriate exception or returns the formatted response.

        :param command: The command that was run.
        :type command: str

        :param response: The full response string from running the command.
        :type response: str
        """
        if response.startswith(b"Unknown command."):
            self.collectd.error("Unknown HAProxy command: %s" % command)
            return ""
        if response == b"Permission denied.\n":
            self.collectd.error("Permission denied for command: %s" % command)
            return ""
        if response == b"No such backend.\n":
            self.collectd.error("No such server: '%s'" % command)
            return ""

        response = response.decode()
        return response.rstrip("\n")

    def gen_info(self):
        """
        Generator that yields (name, value) tuples for HAProxy info.

        These values represent stats for the whole HAProxy process.
        """
        info_response = self.send_command("show info")
        if not info_response:
            return

        for line in info_response.split("\n"):
            label, value = line.split(": ")
            yield (label, value)

    def gen_stats(self, include_frontends, include_backends, include_servers):
        """
        Generator that yields (name, values) for individual proxies.

        Each tuple has two items, the proxy and a dictionary mapping stat
        field names to their respective values.

        :param include_frontends: Whether or not to include FRONTEND aggregate
            stats.
        :type include_frontends: bool

        :param include_backends: Whether or not to include BACKEND aggregate
            stats.
        :type include_backends: bool

        :param include_servers: Whether or not to include individual server
            stats.
        :type include_servers: bool
        """
        # the "type filter" is the second param to "show stat", the values
        # are OR'ed together.
        type_filter = 0
        if include_frontends:
            type_filter += 1
        if include_backends:
            type_filter += 2
        if include_servers:
            type_filter += 4

        stats_response = self.send_command("show stat -1 %d -1" % type_filter)
        if not stats_response:
            return

        lines = stats_response.split("\n")
        fields = lines.pop(0).split(",")
        # the first field is the proxy name, which we key off of so
        # it's not included in individual instance records
        fields.pop(0)

        for line in lines:
            values = line.split(",")
            proxy_name = values.pop(0)

            yield (proxy_name, dict(zip(fields, values)))
