from logging import NullHandler

import requests
from requests.auth import HTTPBasicAuth

from logstash import formatter



class HTTPLogstashHandler(NullHandler, object):
    """Python logging handler for Logstash. Sends events over HTTP.
    :param host: The host of the logstash server.
    :param port: The port of the logstash server (default 80).
    :param ssl: Use SSL for logstash server (default False).
    :param message_type: The type of the message (default logstash).
    :param fqdn; Indicates whether to show fully qualified domain name or not (default False).
    :param tags: list of tags for a logger (default is None).
    :param verify: verify ssl (default is True)
    :param username: basic_auth user (default is None)
    :param password: basic_auth user (default is None)
    :param limit_stacktrace: limit characters for stacktraces
    :param limit_string_fields: limit characters for string fields
    :param limit_containers: limit length of containers (dict, list, set)
    """

    def __init__(self, host, port=80, ssl=False, message_type='logstash', tags=None, fqdn=False, verify=True,
                 username=None, password=None, limit_stacktrace=0, limit_string_fields=0, limit_containers=0):
        super(NullHandler, self).__init__()

        self.formatter = formatter.LogstashFormatter(message_type, tags, fqdn, limit_stacktrace=limit_stacktrace,
                                                     limit_string_fields=limit_string_fields,
                                                     limit_containers=limit_containers)

        if username and password:
            self.auth = HTTPBasicAuth(username, password)
        else:
            self.auth = None
        self.ssl = ssl
        self.verify = verify
        self.host = host
        self.port = port

    def emit(self, record):
        if type(record) == bytes:
            record = record.decode("UTF-8")
        scheme = "http"
        if self.ssl:
            scheme = "https"
        url = "{}://{}:{}".format(scheme, self.host, self.port)
        try:
            headers = {'Content-type': 'application/json'}
            r = requests.post(url, auth=self.auth, data=record, verify=self.verify, headers=headers)
            print(r)
        except Exception:
            self.handleError(record)

    def handle(self, record):
        rv = self.filter(record)
        if rv:
            self.acquire()
            try:
                self.emit(self.formatter.format(record))
            finally:
                self.release()
        return rv



