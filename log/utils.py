from log.schema import BaseJsonLogSchema, Log
from log import ConfigureLogger
from log import logging
import traceback
import json


class JSONLogFormatter(logging.Formatter):
    """
    Кастомизированный класс-форматер для логов в формате json
    """
    def __init__(self):
        super(JSONLogFormatter).__init__()

    def format(self, record: logging.LogRecord, *args, **kwargs) -> str:
        """
        Преобразование объект журнала в json

        :param record: объект журнала
        :return: строка журнала в JSON формате
        """
        log_object: dict = self._format_log_object(record)
        return json.dumps(log_object, ensure_ascii=False)

    @staticmethod
    def _format_log_object(record: logging.LogRecord) -> dict:
        """
        Перевод записи объекта журнала
        в json формат с необходимым перечнем полей

        :param record: объект журнала
        :return: Словарь с объектами журнала
        """

        message = record.getMessage()

        # Инициализация тела журнала
        json_log_fields = BaseJsonLogSchema(
            log=Log(
                level=record.levelno,
                level_name=ConfigureLogger.LEVEL_TO_NAME[record.levelno],
                message=message,
                exceptions=None,
                thread=record.process
            )
        )

        if hasattr(record, 'props'):
            json_log_fields.props = record.props

        if record.exc_info:
            json_log_fields.log.exceptions = traceback.format_exception(*record.exc_info)

        elif record.exc_text:
            json_log_fields.exceptions = record.exc_text

        # Преобразование Pydantic объекта в словарь
        json_log_object = json_log_fields.dict(
            exclude_unset=True,
            by_alias=True,
        )

        # Соединение дополнительных полей логирования
        if hasattr(record, 'request_json_fields'):
            json_log_object.update(record.request_json_fields)
        return json_log_object


def write_log(msg):
    print(msg)
