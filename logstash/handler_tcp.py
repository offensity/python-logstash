from logging.handlers import DatagramHandler, SocketHandler
from logstash import formatter


# Derive from object to force a new-style class and thus allow super() to work
# on Python 2.6
class TCPLogstashHandler(SocketHandler, object):
    """Python logging handler for Logstash. Sends events over TCP.
    :param host: The host of the logstash server.
    :param port: The port of the logstash server (default 5959).
    :param message_type: The type of the message (default logstash).
    :param fqdn; Indicates whether to show fully qualified domain name or not (default False).
    :param tags: list of tags for a logger (default is None).
    :param limit_stacktrace: limit characters for stacktraces
    :param limit_string_fields: limit characters for string fields
    :param limit_containers: limit length of containers (dict, list, set)
    """

    def __init__(self, host, port=5959, message_type='logstash', tags=None, fqdn=False,
                 limit_stacktrace=0, limit_string_fields=0, limit_containers=0):
        super(TCPLogstashHandler, self).__init__(host, port)

        self.formatter = formatter.LogstashFormatter(message_type, tags, fqdn, limit_stacktrace=limit_stacktrace,
                                                     limit_string_fields=limit_string_fields,
                                                     limit_containers=limit_containers)

    def makePickle(self, record):
        return self.formatter.format(record) + b'\n'
