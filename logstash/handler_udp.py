from logging.handlers import DatagramHandler, SocketHandler
from logstash.handler_tcp import TCPLogstashHandler
from logstash import formatter


class UDPLogstashHandler(TCPLogstashHandler, DatagramHandler):
    """Python logging handler for Logstash. Sends events over UDP.
    :param host: The host of the logstash server.
    :param port: The port of the logstash server (default 5959).
    :param message_type: The type of the message (default logstash).
    :param fqdn; Indicates whether to show fully qualified domain name or not (default False).
    :param tags: list of tags for a logger (default is None).
    :param limit_stacktrace: limit characters for stacktraces
    :param limit_string_fields: limit characters for string fields
    :param limit_containers: limit length of containers (dict, list, set)
    """

    def makePickle(self, record):
        return self.formatter.format(record)


# For backward compatibility
LogstashHandler = UDPLogstashHandler

