import logging
from datetime import datetime
import configparser
import os
from django.core.mail import send_mail


class AbstractLogger:
    def configure(self):
        pass

    def pre_action(self):
        pass

    def post_action(self):
        pass

    def log(self, level, message):
        pass


class EmailNotify:
    """
    Email notifier
    """
    def __init__(self):
        self.config_status = True
        self.sender = None
        self.receiver = None
        self.configure()

    def configure(self):
        try:
            email_conf = configparser.ConfigParser(allow_no_value=True)
            email_conf.read(os.path.abspath(os.path.join(os.path.dirname(__file__), 'logger.ini')))
            self.sender = email_conf.get('EmailNotify', 'sender')
            self.receiver = email_conf.get('EmailNotify', 'receiver')
        except Exception as e:
            self.config_status = False
            print(e)

    def send_mail(self, message):
        send_mail('AUTO-NOTIFY', message, self.sender, [self.receiver], fail_silently=False)


class ServerStatus(AbstractLogger):
    """
    Global Init, port, server, user, DB

    """
    pass


class AccessSession(AbstractLogger):
    """
    Include no <SYSTEM_KEY> + Insufficient Permission cases
    """
    pass


class GraphLogger(AbstractLogger):
    """
    Monitoring graph storage, graph capacity, graph grow, graph records....
    """
    pass


class BigDataLogger(AbstractLogger):
    """
    Monitoring bigdata storage....
    """
    pass


class KatalonLogger:
    def __init__(self):
        self.name = __name__
        self.level = logging.INFO

        # Init default logger
        self.default_logger = logging.getLogger(__name__)
        self.default_logger.setLevel(logging.INFO)
        # Init other loggers
        self.server_status = ServerStatus()
        self.access_session = AccessSession()
        self.graph_logger = GraphLogger()
        self.bigdata_logger = BigDataLogger()
        self.configure_loggers()

    def configure_loggers(self):
        self.server_status.configure()
        self.access_session.configure()
        self.graph_logger.configure()
        self.bigdata_logger.configure()

    def set_name(self, name=__name__):
        self.default_logger = logging.getLogger(name)

    def set_level(self, level=logging.INFO):
        self.default_logger.setLevel(level)

    def log(self, level, message):
        self.default_logger.log(level, message)

    def debug(self, message):
        self.default_logger.debug(message)

    def info(self, message):
        self.default_logger.debug(message)

    def warning(self, message):
        self.default_logger.warning(message)

    def error(self, message):
        self.default_logger.error(message)

    def fatal(self, message):
        self.default_logger.fatal(message)


def init_logger():
    global logger
    logger = logger if logger is None else KatalonLogger()
    return logger


logger = init_logger()
