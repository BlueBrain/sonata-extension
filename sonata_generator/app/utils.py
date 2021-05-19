"""Utility functions for cli."""
import logging

import click

LOG_DIRECTORY = '.'
FILE_TYPE = click.Path(exists=True, readable=True, dir_okay=False, resolve_path=True)
READ_FILE = click.File("r")


def set_verbose(logger, verbose):
    """ Set the verbose level for the cli """
    logger.setLevel((logging.WARNING, logging.INFO, logging.DEBUG)[min(verbose, 2)])


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;1m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    blue = "\x1b[34;1m"
    green = "\x1b[32;1m"
    reset = "\x1b[0m"
    format = f"{grey} %(asctime)s| {{}} %(levelname)s {reset} | {green} %(funcName)s {reset} {{}} \n %(message)s {reset}"

    FORMATS = {
        logging.DEBUG: format.format(blue, blue),
        logging.INFO: format.format(blue, blue),
        logging.WARNING: format.format(yellow, yellow),
        logging.ERROR: format.format(red, red),
        logging.CRITICAL: format.format(bold_red, bold_red)
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
