import logging
import logging.config
import os
from logging.handlers import RotatingFileHandler


script_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_dir, 'log_app.log')


log_level = 'DEBUG'

console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s - %(funcName)s - %(lineno)d'
file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(pathname)s:%(lineno)d - %(funcName)s()\n\n'


handler_file = ['file']
handler_console = ['console']
handler_console_file = ['console', 'file']



LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console_formatter': {
            'format': console_format,
        },
        'file_formatter': {
            'format': file_format,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': log_level,
            'formatter': 'console_formatter', 
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_file_path,
            'maxBytes': 100000,  # max file size 100 KB - approx 1500 loggings
            'backupCount': 5,  # keep 5 backup log files
            'level': log_level,
            'formatter': 'file_formatter',  
        },
    },
    'root': {
        'handlers': handler_console_file,
        'level': 'DEBUG',
    },
}



logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)



def test_logger():
    """this function logs in every level to test the logger """

    number_loggers = 30 #can be changed based on result wanted
    for i in range(number_loggers):
        logger.debug(f"Log message DEBUG {i+1}")
    
    for i in range(number_loggers):
        logger.info(f"Log message INFO {i+1}")
    
    for i in range(number_loggers):
        logger.critical (f"Log message CRITICAL {i+1}")
    
    for i in range(number_loggers):
        logger.warning (f"Log message WARNING {i+1}")

    for _ in range(number_loggers):
        logger.info(f"isnt it eorking?")


    

