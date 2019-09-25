import logging
import logstash
import sys

host = 'localhost'

test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
# test_logger.addHandler(logstash.LogstashHandler(host, 5959, version=1))
test_logger.addHandler(logstash.TCPLogstashHandler(host, 5959, limit_containers=6, limit_stacktrace=10000,
                                                   limit_string_fields=1000))

test_logger.error('python-logstash: test logstash error message.')
test_logger.info('python-logstash: test logstash info message.')
test_logger.warning('python-logstash: test logstash warning message.')

# add extra field to logstash message
extra = {
    'test_string': 'python version: ' + repr(sys.version_info),
    'test_boolean': True,
    'test_dict': {'a': 1, 'b': set(['a'])},
    'test_float': 1.23,
    'test_integer': 123,
    'test_list': [1, 2, 3, 4, 5, 6, 7, 8 ],
}
test_logger.info('python-logstash: test extra fields', extra=extra)

extra['test_string'] = "A" * 2000
extra['test_dict'].update({
    'c': 3,
    'd': 4,
    'e': 5,
    'f': 6,
    'g': 7,
    'h': 8
})
test_logger.info('python-logstash: test extra fields 2', extra=extra)

