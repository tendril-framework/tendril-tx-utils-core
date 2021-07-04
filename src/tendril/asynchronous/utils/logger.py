

import io
import sys
from twisted import logger

from twisted.logger import globalLogPublisher
from twisted.logger import LogLevelFilterPredicate
from twisted.logger import FilteringLogObserver
from twisted.logger import textFileLogObserver


class TwistedLogObserverManager(object):
    def __init__(self):
        self._observers = {}

    @property
    def observers(self):
        return self._observers

    def init(self):
        for observer in globalLogPublisher._observers:
            print("Removing pre-installed log observer: ", observer)
            globalLogPublisher.removeObserver(observer)

    def add_observer(self, name, observer):
        if name not in self._observers.keys():
            self._observers[name] = observer
            print("Installing log observer: ", observer)
            globalLogPublisher.addObserver(observer)


manager = TwistedLogObserverManager()
manager.init()


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
        stdout_level = self.level
        if self.log_file:
            rv.append(
                ('file', FilteringLogObserver(
                    textFileLogObserver(io.open(self.log_file, 'a')),
                    predicates=[LogLevelFilterPredicate(logger.LogLevel.info)]
                ))
            )
            stdout_level = logger.LogLevel.warn
        rv.append(
            ('stdout', FilteringLogObserver(
                textFileLogObserver(sys.stdout),
                predicates=[LogLevelFilterPredicate(stdout_level)]
            ))
        )
        return rv

    def log_init(self):
        # TODO Fix what this does when you have multiple objects
        #      calling log_init()
        for observer in self.observers():
            manager.add_observer(*observer)

    @property
    def log(self):
        return self._log
