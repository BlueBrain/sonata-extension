import json
import os
import sys
from collections import namedtuple

import libsonata
import click
import h5py
import yaml
from loguru import logger

import sonata_generator.generators as generators
import sonata_generator.utils as utils
import sonata_generator.writer as writer


def create_config_file(populations_config, components_path, output_dir):
    ''' create a SONATA configuration file based on the populations_config
    '''
    config = {}
    config['version'] = 2
    config['networks'] = {'nodes': [], 'edges': []}
    for node_file in populations_config['nodes']:
        node_file_config = {
            'nodes_file': node_file['filepath'],
            'populations': {}
        }
        for population in node_file['populations']:

            node_file_config['populations'][population['name']] = {
                'type': population['type'],
            }
            if population['type'] == 'biophysical':
                pop_config = node_file_config['populations'][
                    population['name']]
                pop_config['morphologies_dir'] = os.path.join(
                    components_path, population['morphologies_swc'])
                pop_config['biophysical_neuron_models_dir'] = os.path.join(
                    components_path,
                    population['biophysical_neuron_models_dir'])
                pop_config['alternate_morphologies'] = {
                    'neurolucida-asc':
                    os.path.join(components_path,
                                 population['morphologies_asc'])
                }

        config['networks']['nodes'].append(node_file_config)
    for edge_file in populations_config['edges']:
        edge_file_config = {
            'edges_file': edge_file['filepath'],
            'populations': {}
        }
        for population in edge_file['populations']:
            population_name = utils.get_edge_population_name(population)
            edge_file_config['populations'][population_name] = {
                'type': population['type']
            }
        config['networks']['edges'].append(edge_file_config)

    with open(os.path.join(output_dir, 'sonata.json'), 'w') as f:
        json.dump(config, f, indent=4)


def create_nodes_files(nodes_config, populations_config, components_path,
                       output_dir):
    ''' create nodes files based on the populations_config with the datasets defined by nodes_config_file
    '''
    logger.info('create_nodes_files')
    all_population_values = {}
    for node_file in populations_config['nodes']:
        with h5py.File(os.path.join(output_dir, node_file['filepath']),
                       'w') as node_h5:
            for node_population_config in node_file['populations']:
                node_type_config = nodes_config[node_population_config['type']]

                generated_values = generators.generate_properties_dataset(
                    node_type_config, node_population_config, components_path)
                all_population_values[
                    node_population_config['name']] = generated_values

                writer.write_node_population(generated_values,
                                             node_population_config,
                                             node_type_config, node_h5)
    return all_population_values


IndexingProperties = namedtuple("IndexingProperties", ["filename", "population", "source_size", "target_size"])


def create_edges_files(edges_config, populations_config, node_values,
                       components_path, output_dir):
    ''' create edge files based on the populations_config with the datasets defined by edges_config_file
    '''
    logger.info('create_edges_files')
    indexing_properties = []
    for edge_file in populations_config['edges']:
        filepath = os.path.join(output_dir, edge_file['filepath'])
        with h5py.File(filepath, 'w') as edge_h5:
            for edge_population_config in edge_file['populations']:
                edge_type_config = edges_config[edge_population_config['type']]
                #TODO retrieve source and target morphology path
                source_population_name = edge_population_config['source']
                target_population_name = edge_population_config['target']
                source_population_node_config = utils.get_node_population_config(
                    source_population_name, populations_config)
                target_population_node_config = utils.get_node_population_config(
                    target_population_name, populations_config)
                generated_edge_values = generators.generate_edge_datasets(
                    edge_type_config, edge_population_config, node_values,
                    source_population_node_config,
                    target_population_node_config, components_path)

                writer.write_edge_population(generated_edge_values,
                                             edge_population_config,
                                             edge_type_config, edge_h5)

                indexing_properties.append(IndexingProperties(filepath,
                                                              utils.get_edge_population_name(edge_population_config),
                                                              source_population_node_config["size"],
                                                              target_population_node_config["size"]))

    for indexing in indexing_properties:
        libsonata.EdgePopulation.write_indices(
            indexing.filename,
            indexing.population,
            indexing.source_size,
            indexing.target_size,
        )


@click.command()
@click.argument('nodes_config_file', type=click.File('r'))
@click.argument('edges_config_file', type=click.File('r'))
@click.argument('populations_config_file', type=click.File('r'))
@click.argument('components_path', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path(dir_okay=True))
@click.option('-v', '--verbosity', default="ERROR")
def create_sample_data(nodes_config_file, edges_config_file,
                       populations_config_file, components_path, output_dir,
                       verbosity):
    ''' create sample data

    NODES_CONFIG_FILE is the yaml file defining properties of node files
    EDGES_CONFIG_FILE is the yaml file defining properties of edge files
    POPULATIONS_CONFIG_FILE the yaml file defining the populations to be created
    COMPONENTS_PATH is the root directory for externally created elements
    OUTPUT_DIR is where the generated data will be created
    '''
    logger.remove()
    format_string = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | " \
    "<level>{level: <8}</level> | " \
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    logger.add(sys.stderr,
               colorize=True,
               format=format_string,
               level=verbosity)

    logger.info(
        f"configuration is {nodes_config_file},{edges_config_file},{populations_config_file},{output_dir},{verbosity}"
    )
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    nodes_config = yaml.full_load(nodes_config_file)
    edges_config = yaml.full_load(edges_config_file)
    populations_config = yaml.full_load(populations_config_file)

    if not os.path.isabs(components_path):
        raise ValueError(f" {components_path} is not an absolute path")
    create_config_file(populations_config, components_path, output_dir)
    node_values = create_nodes_files(nodes_config, populations_config,
                                     components_path, output_dir)
    create_edges_files(edges_config, populations_config, node_values,
                       components_path, output_dir)
    logger.info(f"circuit generated in {output_dir}")


if __name__ == '__main__':
    create_sample_data()
