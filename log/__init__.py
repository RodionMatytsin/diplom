import logging
from logging.config import dictConfig
from log.main import LoggingMiddleware


class ConfigureLogger(object):
    logger = None
    DEBUG = False
    SERVICE_ID = '0'
    SERVICE_NAME = 'default'
    SERVICE_VERSION = '1.0.0'
    LEVEL_TO_NAME = {
        0: "NOTSET",
        10: "DEBUG",
        20: "INFO",
        30: "WARNING",
        40: "ERROR",
        50: "CRITICAL",
    }

    def __init__(self, service_name, service_version, service_id, debug):
        self.SERVICE_NAME = service_name
        self.SERVICE_VERSION = service_version
        self.SERVICE_ID = service_id
        self.DEBUG = debug

        self.LOG_CONFIG = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'json': {
                    '()': 'log.utils.JSONLogFormatter',
                },
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(levelprefix)s %(message)s",
                    "use_colors": True,
                },
                "access": {
                    "()": "uvicorn.logging.AccessFormatter",
                    "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
                    'use_colors': True
                }
            },
            'handlers': {
                # Используем AsyncLogDispatcher для асинхронного вывода потока.
                'json': {
                    'formatter': 'json',
                    'class': 'asynclog.AsyncLogDispatcher',
                    'func': 'log.utils.write_log',
                },
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                }
            },
            'loggers': {
                self.SERVICE_NAME: {
                    'handlers': ['json'],
                    'level': 'DEBUG' if self.DEBUG else 'INFO',
                    'propagate': False,
                },
                'uvicorn': {
                    'handlers': ['default'],
                    'level': 'INFO',
                    'propagate': False,
                },
                "uvicorn.error": {
                    "level": "INFO"
                },
                # Не даем стандартному логгеру fastapi работать по пустякам и замедлять работу сервиса
                'uvicorn.access': {
                    'handlers': ['access'],
                    'level': 'INFO',
                    'propagate': False,
                },
            },
        }

        dictConfig(self.LOG_CONFIG)
        self.logger = LoggingMiddleware(
            logger=logging.getLogger(self.SERVICE_NAME),
            service_id=self.SERVICE_ID,
            service_name=self.SERVICE_NAME,
            service_version=self.SERVICE_VERSION
        )

    def get_logger_middleware(self):
        return self.logger
