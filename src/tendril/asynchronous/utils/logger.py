

import io
import sys
from twisted import logger

from twisted.logger import globalLogPublisher
from twisted.logger import LogLevelFilterPredicate
from twisted.logger import FilteringLogObserver
from twisted.logger import textFileLogObserver


class TwistedLoggerMixin(object):
    def __init__(self, *args, **kwargs):
        super(TwistedLoggerMixin, self).__init__(*args, **kwargs)
        self._log_file = None
        self._log = logger.Logger(namespace=self.__class__.__name__,
                                  source=self)
        self._log_level = logger.LogLevel.info

    @property
    def log_file(self):
        return self._log_file

    @property
    def level(self):
        return self._log_level

    @level.setter
    def level(self, value):
        self._log_level = value

    def observers(self):
        rv = []
        stdout_level = logger.LogLevel.info
        if self.log_file:
            rv.append(
                FilteringLogObserver(
                    textFileLogObserver(io.open(self.log_file, 'a')),
                    predicates=[LogLevelFilterPredicate(logger.LogLevel.info)]
                ),
            )
            stdout_level = logger.LogLevel.warn
        rv.append(
            FilteringLogObserver(
                textFileLogObserver(sys.stdout),
                predicates=[LogLevelFilterPredicate(stdout_level)]
            ),
        )
        return rv

    def log_init(self):
        for observer in self.observers():
            globalLogPublisher.addObserver(observer)

    @property
    def log(self):
        return self._log
