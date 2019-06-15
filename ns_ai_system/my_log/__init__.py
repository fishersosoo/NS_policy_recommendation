import os
import logging
import time
from logging.handlers import TimedRotatingFileHandler
from read_config import ConfigLoader

basedir = os.path.abspath(os.path.dirname(__file__))
config = ConfigLoader()


class InfoFilter(logging.Filter):
    def filter(self, record):
        """only use INFO
        筛选, 只需要 INFO 级别的log
        :param record:
        :return:
        """
        if logging.DEBUG <= record.levelno < logging.WARNING:
            # 已经是INFO级别了
            # 然后利用父类, 返回 1
            return super().filter(record)
        else:
            return 0


class SafeRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False, maxBytes=0):
        """ This is just a combination of TimedRotatingFileHandler and RotatingFileHandler (adds maxBytes to TimedRotatingFileHandler)  """
        logging.handlers.TimedRotatingFileHandler.__init__(self, filename, when, interval, backupCount, encoding, delay, utc)
        self.maxBytes=maxBytes
    """
    Override doRollover
    lines commanded by "##" is changed by cc
    """

    def shouldRollover(self, record):
        """
        Determine if rollover should occur.

        Basically, see if the supplied record would cause the file to exceed
        the size limit we have.

        we are also comparing times
        """
        if self.stream is None:  # delay was set...
            self.stream = self._open()
        t = int(time.time())
        if t >= self.rolloverAt:
            return 1
        if self.maxBytes > 0:  # are we rolling over?
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  # due to non-posix-compliant Windows feature
            if self.stream.tell() + len(msg) >= self.maxBytes:
                with open(self.baseFilename, 'r') as f:
                    size = os.path.getsize(self.baseFilename)
                    f.seek(size // 2)
                    half_content = f.read()
                with open(self.baseFilename, 'w') as f:
                    f.write(half_content)
                return 0
        # print "No need to rollover: %d, %d" % (t, self.rolloverAt)
        return 0

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.

        Override,   1. if dfn not exist then do rename
                    2. _open with "a" model
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        ##        if os.path.exists(dfn):
        ##            os.remove(dfn)

        # Issue 18940: A file may not have been created if delay is True.
        ##        if os.path.exists(self.baseFilename):
        if not os.path.exists(dfn) and os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.mode = "a"
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt

class Loggers:
    SECRET_KEY = 'hard to guess string'
    # SSL_DISABLE = False
    # SQLALCHEMY_RECORD_QUERIES = True

    LOG_FILE_MAX_BYTES = int(config.get('my_log', 'max_bytes'))
    LOG_FILE_BACKUP_COUNT = int(config.get('my_log', 'backup_count'))
    LOG_FILE_WHEN = config.get('my_log', 'when')
    LOG_FILE_INTERVAL = int(config.get('my_log', 'interval'))

    @classmethod
    def init_app(cls,type,app):
        config_path = type+'_log_path'
        LOG_PATH = os.path.join(basedir, config.get('my_log', config_path))
        if not os.path.isdir(LOG_PATH):
            os.makedirs(LOG_PATH)
        LOG_PATH_WARNING = os.path.join(LOG_PATH, 'warning.log')
        LOG_PATH_INFO = os.path.join(LOG_PATH, 'debug.log')

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(process)d %(thread)d '
            '%(pathname)s %(lineno)s %(message)s')

        # FileHandler Info
        file_handler_debug = SafeRotatingFileHandler(filename=LOG_PATH_INFO,backupCount=cls.LOG_FILE_BACKUP_COUNT,
                                                     when=cls.LOG_FILE_WHEN,interval=cls.LOG_FILE_INTERVAL,
                                                     maxBytes=cls.LOG_FILE_MAX_BYTES)
        # file_handler_debug.suffix = "%Y%m%d%H%M%S.log"
        # file_handler_debug = RotatingFileHandler(filename=LOG_PATH_INFO,maxBytes=cls.LOG_FILE_MAX_BYTES,backupCount=cls.LOG_FILE_BACKUP_COUNT)
        file_handler_debug.setFormatter(formatter)
        file_handler_debug.setLevel(logging.DEBUG)
        info_filter = InfoFilter()
        file_handler_debug.addFilter(info_filter)
        app.addHandler(file_handler_debug)

        # FileHandler Error
        file_handler_warning = SafeRotatingFileHandler(filename=LOG_PATH_WARNING,backupCount=cls.LOG_FILE_BACKUP_COUNT,
                                                       when=cls.LOG_FILE_WHEN, interval=cls.LOG_FILE_INTERVAL,
                                                       maxBytes=cls.LOG_FILE_MAX_BYTES)
        # file_handler_warning.suffix = "%Y%m%d%H%M%S.log"
        # file_handler_warning = RotatingFileHandler(filename=LOG_PATH_WARNING,maxBytes=cls.LOG_FILE_MAX_BYTES,backupCount=cls.LOG_FILE_BACKUP_COUNT)
        file_handler_warning.setFormatter(formatter)
        file_handler_warning.setLevel(logging.WARNING)
        app.addHandler(file_handler_warning)
