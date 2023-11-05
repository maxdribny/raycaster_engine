# /src/logging/logger.py

class Logger:
    def __init__(self, debug_mode: bool = True):
        """
        Initialize the logger.

        :param debug_mode: If true, debug messages will be printed. Otherwise, they will be ignored.
        """
        self.debug_mode = debug_mode

    def log(self, message: str):
        """
        Log a message with the 'LOG' level.

        :param message: The message to be logged.
        """
        self._print_message("LOG", message)

    def debug(self, message: str):
        """
        Log a message with the 'DEBUG' level.

        :param message: The message to be logged.
        """
        if self.debug_mode:
            self._print_message("DEBUG", message)

    def _print_message(self, level: str, message: str):  # noqa
        """
        Print a message to the console.

        :param level: The level of the message.
        :param message: The message to be printed.
        """
        print(f"{level}: {message}")
