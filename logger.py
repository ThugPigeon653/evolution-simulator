import logging

class MyLogger:
    def __init__(self, log_file:str):
        log_file="logs/"+log_file
        self.logger = logging.getLogger('my_logger')
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def log(self, message, level=logging.INFO):
        try:
            output=str(message)
        except Exception as e:
            level=logging.ERROR
            message=f"Unable to parse object of type {type(message)} to str"
        if level == logging.DEBUG:
            self.logger.debug(message)
        elif level == logging.INFO:
            self.logger.info(message)
        elif level == logging.WARNING:
            self.logger.warning(message)
        elif level == logging.ERROR:
            self.logger.error(message)
        elif level == logging.CRITICAL:
            self.logger.critical(message)
