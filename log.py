import logging

log_filename = 'bot.log'
info_level = logging.INFO
log_format = '%(asctime)s %(levelname)s: %(name)s: %(message)s'
handlers = [
    logging.FileHandler(log_filename, encoding='UTF-8'),
    logging.StreamHandler()
    ]
logging.basicConfig(level=info_level, format=log_format, handlers=handlers)
logging.getLogger('httpx').setLevel(logging.WARNING)


def info(message: str) -> None:
    logging.info(message)


def error(message: str) -> None:
    logging.error(message)


def print_loggers():
    logger_dict = logging.root.manager.loggerDict
    loggers = [logging.getLogger(name) for name in logger_dict]
    for log_name in loggers:
        print(log_name)


if __name__ == '__main__':
    print_loggers()
