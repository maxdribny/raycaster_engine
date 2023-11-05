# /src/logging/logger.py

class Logger:
    def __init__(self, debug_mode: bool = True):
        """
        Initialize the logger.

        :param debug_mode: If true, debug messages will be printed. Otherwise, they will be ignored.
        """
        self.debug_mode = debug_mode
