import logging


class Logger:
    def __init__(self, level: int = logging.DEBUG):
        self.logger = logging.getLogger("car_scanner")
        self.logger.setLevel(level)
        self.file_handler = logging.FileHandler("car_scanner.log")
        self.file_handler.setLevel(level)
        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)s: %(levelname)s - %(message)s"
        )
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        self.logger.info("Logger initialized")
        self.logger.debug("Debugging enabled")
        self.logger.info("Info enabled")
        self.logger.warning("Warning enabled")
        self.logger.error("Error enabled")
        self.logger.critical("Critical enabled")

    def info(self, message):
        self.logger.info(message)
        self.file_handler.flush()

    def debug(self, message):
        self.logger.debug(message)
        self.file_handler.flush()

    def warning(self, message):
        self.logger.warning(message)
        self.file_handler.flush()

    def error(self, message):
        self.logger.error(message)
        self.file_handler.flush()

    def critical(self, message):
        self.logger.critical(message)
        self.file_handler.flush()

    def close(self):
        self.file_handler.close()
        logging.shutdown()
        self.logger.info("Logger closed")
        self.logger.debug("Debugging disabled")
        self.logger.info("Info disabled")
        self.logger.warning("Warning disabled")
        self.logger.error("Error disabled")
        self.logger.critical("Critical disabled")
