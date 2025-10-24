import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from utility.config import LOGGING_CONFIG


RECORD_KEYS = {
    'args', 'created', 'exc_info', 'exc_text', 'filename', 'funcName',
    'levelname', 'levelno', 'lineno', 'module', 'msecs', 'msg', 'name',
    'pathname', 'relativeCreated', 'process', 'processName', 'stack_info',
    'taskName', 'thread', 'threadName',
}


class RecordFormatter(logging.Formatter):

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:

        data = dict(
            timestamp=datetime.fromtimestamp(
                timestamp=record.created,
                tz=timezone.utc,
            ).isoformat(),
            level=record.levelname,
            msg=record.msg,
        )

        extra = dict()
        for key, value in record.__dict__.items():
            if key not in RECORD_KEYS:
                extra[key] = value

        return json.dumps(dict(
            **data,
            **extra,
        ), ensure_ascii=False)


logger_config = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'formatter': {
            '()': RecordFormatter,
        },
    },

    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'level': LOGGING_CONFIG.level.value,
            'filters': [],
            'formatter': 'formatter',
        },
        'file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': LOGGING_CONFIG.level.value,
            'filename': Path.cwd() / '.log',
            'mode': 'a',
            'maxBytes': LOGGING_CONFIG.file_bytes,
            'backupCount': LOGGING_CONFIG.file_backups,
            'formatter': 'formatter',
        },
    },

    'loggers': {
        'app': {
            'level': logging.DEBUG,
            'handlers': ['stream_handler', 'file_handler'],
            'propagate': True,
        },
    },

}
