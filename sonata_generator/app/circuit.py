"""CLI for the Circuit creation."""
import logging

import click

from sonata_generator.circuit_generator import create as create_circuit
from sonata_generator.app.utils import set_verbose, READ_FILE

L = logging.getLogger("Circuit")


@click.group()
@click.option('-v', '--verbose', count=True)
def app(verbose):
    """Run the different sonata circuit creation CLI."""
    set_verbose(L, verbose)


@app.command()
@click.argument('nodes_config_file', type=READ_FILE)
@click.argument('edges_config_file', type=READ_FILE)
@click.argument('usecase_config', type=READ_FILE)
@click.argument('components_path', type=click.Path(dir_okay=True))
@click.argument('output_dir', type=str)
@click.option('-s', '--seed', type=int, default=0)
def create(nodes_config_file, edges_config_file, usecase_config, components_path, output_dir, seed):
    """create circuit sample data

    NODES_CONFIG_FILE is the yaml file defining properties of node files
    EDGES_CONFIG_FILE is the yaml file defining properties of edge files
    USECASE_CONFIG_FILE the yaml file defining the populations to be created
    COMPONENTS_PATH is the root directory for externally created elements
    OUTPUT_DIR is where the generated data will be created
    """
    create_circuit(nodes_config_file, edges_config_file, usecase_config, components_path, output_dir, seed)
