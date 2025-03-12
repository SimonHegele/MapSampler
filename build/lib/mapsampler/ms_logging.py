import logging

from sys import stdout

def logging_setup(log_level, logfile):

    match log_level:
        case "debug":
            level=logging.DEBUG
        case "info":
            level=logging.INFO
        case "warning":
            level=logging.WARNING
        case "error":
            level=logging.ERROR
        case "critical":
            level=logging.CRITICAL
    
    file_handler   = logging.FileHandler(filename=logfile)
    stdout_handler = logging.StreamHandler(stream=stdout)

    logging.basicConfig(level    = level,
                        format   = "%(asctime)s %(levelname)s %(message)s",
                        datefmt  = "%d-%m-%Y %H:%M:%S",
                        handlers=[file_handler, stdout_handler]
                        )