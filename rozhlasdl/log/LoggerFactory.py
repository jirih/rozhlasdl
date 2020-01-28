import logging
import os
from logging.handlers import RotatingFileHandler
from os.path import basename
from zipfile import ZipFile, ZIP_DEFLATED
from zlib import Z_BEST_COMPRESSION

from log.MyLogFormatter import MyLogFormatter
from log.Singleton import Singleton

LOG_MAX_BYTES = 1024 * 1024
LOG_BACKUP_COUNT = 10


def namer(name):
    return name + ".zip"


def rotator(source, dest):
    with ZipFile(dest, mode='w', compression=ZIP_DEFLATED, compresslevel=Z_BEST_COMPRESSION) as myzip:
        myzip.write(source, arcname=basename(source))
    os.remove(source)


class LoggerFactory(metaclass=Singleton):
    logging_handler = None
    default_log_level = logging.NOTSET

    @staticmethod
    def set(log_file=None, default_log_level=logging.INFO):
        # print("setting")
        if LoggerFactory.logging_handler is not None:
            LoggerFactory.get(__name__).error("LoggerFactory already set.")
            return
        if log_file is None:
            LoggerFactory.logging_handler = logging.StreamHandler()
            formatter = MyLogFormatter(fmt='%(asctime)s [%(levelname).1s] %(name).12s: %(message)s',
                                       datefmt='%H:%M:%S')
        else:
            LoggerFactory.logging_handler = RotatingFileHandler(log_file, encoding='utf-8',
                                                                maxBytes=LOG_MAX_BYTES,
                                                                backupCount=LOG_BACKUP_COUNT,
                                                                delay=True)
            LoggerFactory.logging_handler.rotator = rotator
            LoggerFactory.logging_handler.namer = namer
            formatter = MyLogFormatter(fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        formatter.default_msec_format = '%s.%03d'
        LoggerFactory.logging_handler.setFormatter(formatter)
        LoggerFactory.logging_handler.setLevel(logging.DEBUG)

        LoggerFactory.default_log_level = default_log_level
        # print("LoggerFactory.default_log_level: %d" % LoggerFactory.default_log_level)

    @staticmethod
    def get(name="root", log_level=None):
        # print("getting %s" % name)
        if log_level is None:
            log_level = LoggerFactory.default_log_level

        if LoggerFactory.logging_handler is None:
            LoggerFactory()
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        if LoggerFactory.default_log_level == logging.NOTSET:
            rescue_handler = get_rescue_handler()
            logger.addHandler(rescue_handler)
            logger.error("LoggerFactory not set yet.")
        else:
            logger.addHandler(LoggerFactory.logging_handler)
        return logger


def get_rescue_handler():
    rescue_handler = logging.StreamHandler()
    rescue_handler.setLevel(logging.DEBUG)
    formatter = MyLogFormatter(fmt='%(asctime)s [%(levelname).1s] %(name).12s: %(message)s',
                               datefmt='%H:%M:%S')
    formatter.default_msec_format = '%s.%03d'
    rescue_handler.setFormatter(formatter)
    return rescue_handler
