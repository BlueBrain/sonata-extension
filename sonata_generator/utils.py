import glob
import os

from morphio import Morphology


def get_morphologies_name(component_path, path_to_morphologies):
    ''' list the available morphology files
    '''
    filenames = glob.glob(
        os.path.join(component_path, path_to_morphologies, '*.swc'))
    if not filenames:
        raise ValueError(
            f'empty list of morphologies for {component_path} / {path_to_morphologies}'
        )
    return [os.path.basename(filename)[:-4] for filename in filenames]


def get_emodels_values(component_path, path_to_hoc_files):
    ''' get the possible hoc emodels name '''
    filenames = glob.glob(
        os.path.join(component_path, path_to_hoc_files, '*.hoc'))
    if not filenames:
        raise ValueError(
            'empty list of emodels for {component_path} / {path_to_hoc_files}')
    return ["hoc:" + os.path.basename(filename)[:-4] for filename in filenames]


def get_edge_population_name(population_config):
    source = population_config['source']
    target = population_config['target']
    type_ = population_config['type']
    return f"{source}__{target}__{type_}"


def get_morphology(component_path, path_to_morphology, morphology_name):
    ''' return a morphio object for a swc file '''
    morph = Morphology(
        os.path.join(component_path, path_to_morphology,
                     morphology_name + '.swc'))
    return morph


def get_node_population_config(node_population_name, populations_config):
    node_file_configs = populations_config['nodes']
    node_population_config = [nfc['populations'] for nfc in node_file_configs]
    flatten_node_population_config = [
        c for elem in node_population_config for c in elem
    ]
    node_config = [
        npc for npc in flatten_node_population_config
        if npc['name'] == node_population_name
    ]
    if len(node_config) != 1:
        raise ValueError(
            f"invalid number of node configuration for {node_population_name}")
    return node_config[0]
