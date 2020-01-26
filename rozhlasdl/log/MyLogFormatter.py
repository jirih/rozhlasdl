import logging
import time


class MyLogFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt is not None:
            t = time.strftime(datefmt, ct)
            s = self.default_msec_format % (t, record.msecs)
        else:
            t = time.strftime(self.default_time_format, ct)
            s = self.default_msec_format % (t, record.msecs)
        return s
