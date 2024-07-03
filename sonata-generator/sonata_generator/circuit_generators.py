# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
import json
import logging
import os

import numpy as np
import yaml

from sonata_generator.neuronal_generators import (BiophysicalGenerator, VirtualGenerator,
                                                  ChemicalGenerator)
from sonata_generator.ngv_generators import (AstrocyteGenerator, VasculatureGenerator,
                                             GlialGlialGenerator, NeuroGlialGenerator,
                                             EndfootGenerator)

from sonata_generator.utils import (collect_edge_populations, collect_node_populations,
                                    get_edge_population_name)

L = logging.getLogger("Circuit")

NODE_GENERATOR_DISPATCH = {
    "biophysical": BiophysicalGenerator,
    "virtual": VirtualGenerator,
    "vasculature": VasculatureGenerator,
    "astrocyte": AstrocyteGenerator,
}

EDGE_GENERATOR_DISPATCH = {
    "chemical": ChemicalGenerator,
    "electrical": GlialGlialGenerator,
    "glialglial": GlialGlialGenerator,
    "synapse_astrocyte": NeuroGlialGenerator,
    "endfoot": EndfootGenerator
}


def create_config_file(populations_config, components_path, output_dir):
    """Create a SONATA configuration file based on the populations_config."""
    config = {'version': 2, 'networks': {'nodes': [], 'edges': []}}
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
            elif population['type'] == 'astrocyte':
                pop_config = node_file_config['populations'][
                    population['name']]
                pop_config['morphologies_dir'] = os.path.join(
                    components_path, population['morphologies_h5'])
                pop_config['biophysical_neuron_models_dir'] = os.path.join(
                    components_path,
                    population['biophysical_neuron_models_dir'])
                pop_config['microdomains_file'] = os.path.join(
                    os.path.abspath(output_dir), "microdomains", "microdomains.h5")

            elif population['type'] == 'vasculature':
                pop_config = node_file_config['populations'][
                    population['name']]
                pop_config['vasculature_file'] = os.path.join(
                    components_path, population['morphologies_h5'], "vasculature_morphology.h5")

                pop_config['vasculature_mesh'] = os.path.join(
                    components_path, population['morphologies_h5'], "vasculature_mesh.obj")

        config['networks']['nodes'].append(node_file_config)
    for edge_file in populations_config['edges']:
        edge_file_config = {
            'edges_file': edge_file['filepath'],
            'populations': {}
        }
        for population in edge_file['populations']:
            population_name = get_edge_population_name(population)
            edge_file_config['populations'][population_name] = {
                'type': population['type']
            }
        config['networks']['edges'].append(edge_file_config)

    with open(os.path.join(output_dir, 'circuit_sonata.json'), 'w') as f:
        json.dump(config, f, indent=4)


def _filter_population(population_list, type_):
    return [pop for pop in population_list if pop.type == type_]


def _create_node_populations(all_nodes, configuration, type_):
    filtered = _filter_population(all_nodes, type_)
    if filtered:
        L.info(f"Creating {type_} nodes.")
    for pop in filtered:
        pop_gen = NODE_GENERATOR_DISPATCH[type_](pop, configuration)
        pop_gen.create_data()
        pop_gen.save()


def _create_edge_populations(all_edges, configuration, type_):
    filtered = _filter_population(all_edges, type_)
    if filtered:
        L.info(f"Creating {type_} edges.")
    for pop in filtered:
        pop_gen = EDGE_GENERATOR_DISPATCH[type_](pop, configuration)
        if type_ == "synapse_astrocyte":
            pop_gen.connect_synapse(all_edges)
        pop_gen.create_data()
        pop_gen.save()


def create(nodes_config_file, edges_config_file, usecase_config, components_path, output_dir,
           seed=0):
    L.info(
        f"configuration is {nodes_config_file},{edges_config_file},{usecase_config},{output_dir}")
    np.random.seed(seed)

    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    nodes_config = yaml.full_load(open(nodes_config_file))
    edges_config = yaml.full_load(open(edges_config_file))
    usecase_config = yaml.full_load(open(usecase_config))

    create_config_file(usecase_config, components_path, output_dir)

    all_nodes = collect_node_populations(usecase_config, output_dir,
                                         components_path=components_path)
    for type_ in nodes_config.keys():
        _create_node_populations(all_nodes, nodes_config, type_)

    all_edges = collect_edge_populations(usecase_config, output_dir,
                                         components_path=components_path)
    for type_ in edges_config.keys():
        _create_edge_populations(all_edges, edges_config, type_)
