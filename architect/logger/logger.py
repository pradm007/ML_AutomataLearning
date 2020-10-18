from architect.logger.logger_manager import LoggerManager


class Logger:

    def __init__(self, logger_name='architect'):
        self._logger_name = logger_name
        self._lm = LoggerManager(logger_name)

    def get_logger(self):
        return self._lm.get_logger(self._logger_name)
