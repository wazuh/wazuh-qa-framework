"""Custom logging module.

Classes:
  - Logger()
"""
import logging
import sys
import os
from abc import ABC

from wazuh_qa_framework.generic_modules.exceptions.exceptions import ValidationError


LOGGERS = {}
HANDLERS = ['sys_output', 'file']

LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

COLORS = {
    'CLEAR': '\033[0m',
    'BLUE': '\033[94m',
    'CYAN': '\033[96m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m'
}

LOG_COLORS = {
    'debug': COLORS['CYAN'],
    'info': COLORS['BLUE'],
    'warning': COLORS['YELLOW'],
    'error': COLORS['RED'],
    'critical': COLORS['RED']
}

FORMATERS = {
    'basic': logging.Formatter('%(asctime)s — %(levelname)s — %(message)s')
}


class BaseLogger(ABC):
    """Logger class to manage modules logging.

    Args:
        name (str): Logger name.
        level (str): Logging level.
        formatter (str): Formatter group.
        handlers (list(str)): Logging handlers.
        logging_file (str): File path were save the logging if the file handler has been specified.
        output_color (boolean): True for logging with output colors, False otherwise.

    Attributes:
        name (str): Logger name.
        logger (logging.Logger): Logger object.
        level (str): Logging level.
        formatter (str): Formatter group.
        handlers (list(str)): Logging handlers.
        logging_file (str): File path were save the logging if the file handler has been specified.
        output_color (boolean): True for logging with output colors, False otherwise.
    """
    def __init__(self, name, level='info', formatter='basic', handlers=None, logging_file=None,
                 output_color=True):
        self.name = name
        self.__logger = logging.getLogger(name)
        self.level = level
        self.formatter = formatter
        self.logging_file = logging_file
        self.handlers = handlers
        self.output_color = output_color

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_name):
        self.__name = new_name

    @property
    def logger(self):
        return self.__logger

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, new_level):
        if new_level.lower() in LEVELS.keys():
            self.__level = LEVELS[new_level.lower()]
            self.__logger.level = self.__level
        else:
            raise ValidationError(f"{new_level} is not an accepted level. Expected one of {list(LEVELS.keys())}")

    @property
    def formatter(self):
        return self.__formatter

    @formatter.setter
    def formatter(self, new_formatter):
        if new_formatter in FORMATERS.keys():
            self.__formatter = FORMATERS[new_formatter]
        else:
            self.__formatter = FORMATERS['basic']
            raise ValidationError(f"{new_formatter} is not an accepted formatter. Expected one of"
                                  f" {list(FORMATERS.keys())}")

    @property
    def logging_file(self):
        return self.__logging_file

    @logging_file.setter
    def logging_file(self, new_logging_file):
        if new_logging_file:
            if not os.path.exists(new_logging_file):
                raise ValidationError(f"File {new_logging_file} does not exist")

            # Check that the monitored file is a "file"
            if not os.path.isfile(new_logging_file):
                raise ValidationError(f"{new_logging_file} is not a file")

            # Check that the program can read or write in the file.
            if not os.access(new_logging_file, os.R_OK) or not os.access(new_logging_file, os.W_OK):
                raise ValidationError(f"{new_logging_file} is not readable")

        self.__logging_file = new_logging_file


    @property
    def handlers(self):
        return self.__handlers

    @handlers.setter
    def handlers(self, new_handlers):
        handlers = new_handlers if new_handlers is not None else ['sys_output']

        if type(handlers) != list:
            ValidationError(f"It was expected to receive a list of allowed handlers: f{HANDLERS}")

        # Set logger handlers
        for handler in handlers:
            if handler in HANDLERS:
                if handler == 'sys_output':
                    stream_handler = logging.StreamHandler(sys.stdout)
                    stream_handler.setFormatter(self.__formatter)
                    stream_handler.setLevel(self.__level)
                    self.__logger.addHandler(stream_handler)
                elif handler == 'file':
                    file_handler = logging.FileHandler(self.__logging_file)
                    file_handler.setFormatter(self.__formatter)
                    file_handler.setLevel(self.__level)
                    self.__logger.addHandler(file_handler)
                else:
                    ValidationError(f"{handler} not found")
            else:
                # Avoid default duplicated handlers.
                if not any(isinstance(_handler, logging.StreamHandler) for _handler in self.__logger.handlers):
                    stream_handler = logging.StreamHandler(sys.stdout)
                    stream_handler.setFormatter(self.__formatter)
                    stream_handler.setLevel(self.__level)
                    self.__logger.addHandler(stream_handler)
                    ValidationError(f"{handler} handler is not allowed")

        self.__handlers = handlers

    @property
    def output_color(self):
        return self.__output_color

    @output_color.setter
    def output_color(self, new_output_color):
        self.__output_color = new_output_color

    def debug(self, message):
        """DEBUG logging.

        Args:
            message (str): Logging message.
        """
        custom_message = f"{LOG_COLORS['debug']}{message}{COLORS['CLEAR']}" if self.output_color else message
        self.logger.debug(custom_message)

    def info(self, message):
        """INFO logging.

        Args:
            message (str): Logging message.
        """
        custom_message = f"{LOG_COLORS['info']}{message}{COLORS['CLEAR']}" if self.output_color else message
        self.logger.info(custom_message)

    def warning(self, message):
        """WARNING logging.

        Args:
            message (str): Logging message.
        """
        custom_message = f"{LOG_COLORS['warning']}{message}{COLORS['CLEAR']}" if self.output_color else message
        self.logger.warning(custom_message)

    def error(self, message):
        """ERROR logging.

        Args:
            message (str): Logging message.
        """
        custom_message = f"{LOG_COLORS['error']}{message}{COLORS['CLEAR']}" if self.output_color else message
        self.logger.error(custom_message)

    def critical(self, message):
        """CRITICAL logging.

        Args:
            message (str): Logging message.
        """
        custom_message = f"{LOG_COLORS['critical']}{message}{COLORS['CLEAR']}" if self.output_color else message
        self.logger.critical(custom_message)

    def __str__(self):
        """Redefine the logger object representation.

        Returns:
            str: Logger object representation.
        """
        return '{' + f"name: {self.name}, level={self.level}, formatter={self.formatter}, handlers={self.handlers}, " \
                     f" logging_file={self.logging_file}, output_color={self.output_color}" + '}'
