try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
import errno
import socket


SOCKET_BUFFER_SIZE = 1024


class HAProxySocket(object):

    def __init__(self, collectd, socket_file_path):
        self.collectd = collectd
        self.socket_file_path = socket_file_path

    def send_command(self, command):
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

        buff = StringIO.StringIO()

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
        info_response = self.send_command("show info")
        if not info_response:
            return

        for line in info_response.split("\n"):
            label, value = line.split(": ")
            yield (label, value)

    def gen_stats(self, include_frontends, include_backends, include_servers):
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
