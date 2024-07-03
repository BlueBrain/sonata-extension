"""CLI for the Report creation."""
# SPDX-License-Identifier: Apache-2.0
import logging

import click

from sonata_generator.report_generators import create as create_reports
from sonata_generator.app.utils import set_verbose, FILE_TYPE


L = logging.getLogger("Reports")


@click.group()
@click.option('-v', '--verbose', count=True)
def app(verbose):
    """Run the different sonata reports creation CLI."""
    set_verbose(L, verbose)


@app.command()
@click.argument('usecase_config', type=FILE_TYPE)
@click.argument('components_path', type=click.Path(dir_okay=True))
@click.argument('output_dir', type=str)
@click.option('-s', '--seed', type=int, default=0)
def create(usecase_config, components_path, output_dir, seed):
    """create report sample data

    USECASE_CONFIG_FILE the yaml file defining the populations to be created
    COMPONENTS_PATH is the root directory for externally created elements
    OUTPUT_DIR is where the generated data will be created
    """
    create_reports(usecase_config, components_path, output_dir, seed=seed)
