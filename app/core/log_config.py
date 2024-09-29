import logging.config

from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    LOGGER_NAME: str = "finalyzr_logger"
    LOG_FORMAT: str = "%(levelname)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {}
    handlers: dict = {
        "console": {
            "formatter": "json",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {  # Rotating file log
            "formatter": "detailed",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "app.log",
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
            "level": "DEBUG",
        },
    }
    loggers: dict = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.formatters = {
            "default": {
                "format": self.LOG_FORMAT,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },

            "detailed": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },

            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            },
        }

        self.loggers = {
            self.LOGGER_NAME: {
                "handlers": ["console", "file"],
                "level": self.LOG_LEVEL,
                "propagate": False,
            },

            # The bcrypt library has a known issue (https://github.com/pyca/bcrypt/issues/684)
            # with passlib import warning. Use this to suppress it in the logs and only show error-level.
            "passlib": {
                "handlers": ["console"],
                "level": "ERROR",
                "propagate": False,
            },
        }

        self.setup()

    def setup(self):
        """Apply the logging configuration."""
        logging.config.dictConfig(self.model_dump())


logging_settings = LoggingSettings()
