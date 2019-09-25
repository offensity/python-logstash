import traceback
import logging
import socket
import sys
from datetime import datetime
try:
    import json
except ImportError:
    import simplejson as json


class LogstashFormatterBase(logging.Formatter):

    limit_stacktrace = 0

    def __init__(self, message_type='Logstash', tags=None, fqdn=False, limit_stacktrace=0, limit_string_fields=0, limit_containers=0):
        self.message_type = message_type
        self.tags = tags if tags is not None else []
        LogstashFormatterBase.limit_stacktrace = limit_stacktrace
        self.limit_string_fields = limit_string_fields
        self.limit_containers = limit_containers

        if fqdn:
            self.host = socket.getfqdn()
        else:
            self.host = socket.gethostname()

    def limit_string_field(self, value):
        if self.limit_string_fields == 0:
            return value
        return value[:self.limit_string_fields] + (value[self.limit_string_fields:] and '...Truncated...')

    def get_extra_fields(self, record, first=True):
        # The list contains all the attributes listed in
        # http://docs.python.org/library/logging.html#logrecord-attributes
        skip_list = (
            'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
            'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
            'msecs', 'msecs', 'message', 'msg', 'name', 'pathname', 'process',
            'processName', 'relativeCreated', 'thread', 'threadName', 'extra',
            'auth_token', 'password')

        if sys.version_info < (3, 0):
            easy_types = (basestring, bool, float, int, long, type(None))
        else:
            easy_types = (str, bool, float, int, type(None))
        containers = (dict, set, list)
        fields = {}
        if first:
            for key, value in record.__dict__.items():
                if key not in skip_list or not first:
                    if isinstance(value, containers):
                        fields[key] = self.get_extra_fields(value, first=False)
                    elif type(value) == str:
                        fields[key] = self.limit_string_field(value)
                    elif isinstance(value, easy_types):
                        fields[key] = value
                    else:
                        fields[key] = self.limit_string_field(repr(value))
        elif type(record) == dict:
            counter = 0
            for key, value in record.items():
                counter += 1
                if self.limit_containers != 0 and counter > self.limit_containers:
                    fields['WARNING'] = "...Truncated..."
                    break
                if isinstance(value, containers):
                    fields[key] = self.get_extra_fields(value, first=False)
                elif type(value) == str:
                    fields[key] = self.limit_string_field(value)
                elif isinstance(value, easy_types):
                    fields[key] = value
                else:
                    fields[key] = self.limit_string_field(repr(value))
        elif type(record) == list or type(record) == set:
            tmp = []
            counter = 0
            for value in record:
                counter += 1
                if self.limit_containers != 0 and counter > self.limit_containers:
                    tmp.append("...Truncated...")
                    break
                tmp.append(self.get_extra_fields(value, first=False))
            return tmp
        else:
            if type(record) == str:
                return self.limit_string_field(record)
            if isinstance(record, easy_types):
                return record
            else:
                return self.limit_string_field(repr(record))

        return fields

    def get_debug_fields(self, record):
        fields = {
            'stack_trace': self.format_exception(record.exc_info),
            'lineno': record.lineno,
            'process': record.process,
            'thread_name': record.threadName,
        }

        # funcName was added in 2.5
        if not getattr(record, 'funcName', None):
            fields['funcName'] = record.funcName

        # processName was added in 2.6
        if not getattr(record, 'processName', None):
            fields['processName'] = record.processName

        return fields

    @classmethod
    def format_source(cls, message_type, host, path):
        return "%s://%s/%s" % (message_type, host, path)

    @classmethod
    def format_timestamp(cls, time):
        tstamp = datetime.utcfromtimestamp(time)
        return tstamp.strftime("%Y-%m-%dT%H:%M:%S") + ".%03d" % (tstamp.microsecond / 1000) + "Z"

    @classmethod
    def format_exception(cls, exc_info):
        stacktrace = ''.join(traceback.format_exception(*exc_info)) if exc_info else ''
        if cls.limit_stacktrace == 0:
            return stacktrace
        return stacktrace[:cls.limit_stacktrace] + (stacktrace[cls.limit_stacktrace:] and '..')

    @classmethod
    def serialize(cls, message):
        if sys.version_info < (3, 0):
            return json.dumps(message)
        else:
            return bytes(json.dumps(message), 'utf-8')


class LogstashFormatter(LogstashFormatterBase):

    def format(self, record):
        # Create message dict
        message = {
            '@timestamp': self.format_timestamp(record.created),
            '@version': '1',
            'message': record.getMessage(),
            'host': self.host,
            'path': record.pathname,
            'tags': self.tags,
            'type': self.message_type,

            # Extra Fields
            'level': record.levelname,
            'logger_name': record.name,
        }

        # Add extra fields
        message.update(self.get_extra_fields(record))

        # If exception, add debug info
        if record.exc_info:
            message.update(self.get_debug_fields(record))

        return self.serialize(message)
