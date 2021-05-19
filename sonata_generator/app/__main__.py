"""Collection of CLI tools for sonata generators."""

import logging
import click

from sonata_generator.app import circuit, reports
from sonata_generator.version import VERSION
from sonata_generator.app.utils import CustomFormatter


def _initialize_logging(logger_name):
    logger = logging.getLogger(logger_name)
    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)


def main():
    """Collection of tools for sonata-generator."""
    _initialize_logging("Circuit")
    _initialize_logging("Reports")
    app = click.Group(
        'sonata_generator',
        {
            'circuit': circuit.app,
            'reports': reports.app,
        },
    )
    app = click.version_option(VERSION)(app)
    app()


if __name__ == '__main__':
    main()
