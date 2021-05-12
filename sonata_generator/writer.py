import h5py
import numpy as np
from loguru import logger

import sonata_generator.utils as utils


def write_properties_datasets(group, properties_config, prop_values):
    ''' write the generated datasets into the h5 file
    '''
    for prop_name, prop_definition in properties_config.items():
        if prop_name not in prop_values:
            logger.debug(f"{prop_name} not present in input values. Ignored")
            continue

        if prop_definition['type'] in ['int', 'float']:
            values = prop_values[prop_name]
            dtype = values.dtype
        elif prop_definition['type'] == 'text':
            values = np.array([
                v.encode('UTF-8') for v in prop_values[prop_name]
            ]).astype(object)
            dtype = h5py.special_dtype(vlen=str)
        elif prop_definition['type'] == 'enum':
            unique_values, indices = np.unique(prop_values[prop_name],
                                               return_inverse=True)
            values = indices.astype(np.uint32)
            dtype = values.dtype
            group.create_dataset('@library/' + prop_name,
                                 data=unique_values.astype(object),
                                 dtype=h5py.special_dtype(vlen=str))
        else:
            raise ValueError(f"unknown type: {prop_definition['type']}")

        group.create_dataset(prop_name, data=values, dtype=dtype)


def write_node_population(node_values, population_config, node_config,
                          node_h5):
    ''' write a particular node population defined by population_config
    in node_h5 with the values from node_values.
    '''
    root = node_h5.create_group('/nodes/%s' % population_config['name'])
    group_0 = root.create_group('0')
    pop_size = population_config['size']
    root.create_dataset('node_type_id', data=np.full(pop_size, -1))
    write_properties_datasets(group_0, node_config, node_values)


def write_edge_population(edge_values, population_config, edge_config, edge_file):
    population_name = utils.get_edge_population_name(population_config)
    source_name = population_config['source']
    target_name = population_config['target']
    pop_group = edge_file.create_group('/edges/%s' % population_name)

    pop_group.create_dataset("source_node_id", data=edge_values['source_node_id'], dtype=np.uint64)
    pop_group['source_node_id'].attrs['node_population'] = source_name

    pop_group.create_dataset("target_node_id",data=edge_values['target_node_id'],  dtype=np.uint64)
    pop_group['target_node_id'].attrs['node_population'] = target_name

    pop_group.create_dataset("edge_type_id", data=edge_values['edge_type_id'], dtype=np.int64)

    property_group = pop_group.create_group('0')
    write_properties_datasets(property_group, edge_config, edge_values)
