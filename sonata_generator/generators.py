import numpy as np
from loguru import logger
from morphio import SectionType

import sonata_generator.utils as utils


def generate_properties_dataset(
    properties_config,
    population_config,
    components_path=None,
):
    ''' generate properties for a population config
    "derived" values are ignored as they are generated as a post process
    "morphology", "emodel" values have their own specific generator.
    the rest is randomly generated based on the range given by "values" property
    '''
    logger.debug(
        f"properties_config: {properties_config}, population_config: {population_config}, components_path: {components_path}"
    )
    ret_values = {}
    values = None
    pop_size = population_config['size']
    for prop_name, prop_definition in properties_config.items():
        logger.debug(f" generate dataset for {prop_name} {prop_definition}")
        if prop_definition['values'] == 'derived':
            continue
        if prop_definition['values'] == 'morphology':
            morphologies = utils.get_morphologies_name(
                components_path, population_config['morphologies_swc'])
            values = np.random.choice(morphologies, size=pop_size)
        elif prop_definition['values'] == 'emodel':
            emodels = utils.get_emodels_values(
                components_path,
                population_config['biophysical_neuron_models_dir'])
            values = np.random.choice(emodels, size=pop_size)
        elif prop_definition['type'] == 'float':
            values = np.random.uniform(prop_definition['values'][0],
                                       prop_definition['values'][1],
                                       size=pop_size)
        elif prop_definition['type'] == 'int':
            values = np.random.randint(prop_definition['values'][0],
                                       prop_definition['values'][1],
                                       size=pop_size)
        elif prop_definition['type'] in ['text', 'enum']:
            values = np.random.choice(prop_definition['values'], size=pop_size)
        else:
            raise ValueError(f"unknown type: {prop_definition['type']}")

        ret_values[prop_name] = values
    return ret_values


def get_surface_point(direction, point, distance):
    ''' get a point orthogonal to a line defined by (direction, point) at a distance of point '''
    a, b, c = direction
    orth_direction = np.array([-b, a, 0])
    # TODO check non collinear
    surface_point = point + orth_direction * distance / np.linalg.norm(
        orth_direction)
    return surface_point


def create_synapse(morph, pre_or_post="pre"):
    ''' create  a random synapse on morph.
    "pre" will be placed on "axon"
    "post" will be placed on basal or apical dendrite
    section_id, segment_id, point_position, offset and surface contact.
    '''
    filter_ = [SectionType.axon]
    if pre_or_post == "post":
        filter_ = [SectionType.basal_dendrite, SectionType.apical_dendrite]
    sections = [v for v in morph.sections if v.type in filter_]
    selected_section = np.random.choice(sections)
    segment_id = np.random.randint(0, len(selected_section.points) - 1)
    diameter = selected_section.diameters[segment_id]
    point_1 = selected_section.points[segment_id]
    point_2 = selected_section.points[segment_id + 1]
    direction = point_2 - point_1
    segment_length = np.linalg.norm(direction)
    offset = np.random.uniform(0, segment_length)
    ratio = offset / segment_length
    final_point = point_1 + ratio * direction
    surface_point = get_surface_point(direction, final_point, diameter / 2)

    return selected_section.id + 1, segment_id, final_point, offset, surface_point


def get_point_space_position(point, x, y, z, o_x, o_y, o_z, o_w):
    ''' get the position of a morphology point knowing the soma position (x,y,z)
    and the rotation defined by a quaternion o_x, o_y, o_z, o_w'''
    from scipy.spatial.transform import Rotation as R
    r = R.from_quat([o_x, o_y, o_z, o_w])
    rotated_point = r.apply(point)
    return rotated_point + [x, y, z]


def generate_synapse_data(node_values,
                          node_id,
                          morphology_path,
                          components_path,
                          pre_or_post="pre"):
    logger.debug(
        f"{node_values}, {node_id}, {morphology_path}, {components_path}, {pre_or_post}"
    )
    morph = utils.get_morphology(components_path, morphology_path,
                                 node_values['morphology'][node_id])
    section_id, segment_id, point, offset, surface_point = create_synapse(
        morph, pre_or_post)

    point_position = get_point_space_position(
        point, node_values['x'][node_id], node_values['y'][node_id],
        node_values['z'][node_id], node_values['orientation_x'][node_id],
        node_values['orientation_y'][node_id],
        node_values['orientation_z'][node_id],
        node_values['orientation_w'][node_id])
    surface_point_position = get_point_space_position(
        surface_point, node_values['x'][node_id], node_values['y'][node_id],
        node_values['z'][node_id], node_values['orientation_x'][node_id],
        node_values['orientation_y'][node_id],
        node_values['orientation_z'][node_id],
        node_values['orientation_w'][node_id])
    return {
        "section_id": section_id,
        "segment_id": segment_id,
        "offset": offset,
        "point_position": point_position,
        "surface_point_position": surface_point_position
    }


def generate_source_target_ids(edge_population_config,
                               source_node_population_config,
                               target_node_population_config):

    source_node_size = source_node_population_config['size']
    target_node_size = target_node_population_config['size']

    source_node_ids = np.random.randint(0, source_node_size,
                                        edge_population_config['size'])
    target_node_ids = np.random.randint(0, target_node_size,
                                        edge_population_config['size'])
    #TODO group nodes properly (by efferent iirc)
    return source_node_ids, target_node_ids


# efferent: source, pre_synaptic
# afferent: target, post_synaptic


def generate_computed_properties_dataset(edge_config, population_config,
                                         source_node_ids, target_node_ids,
                                         node_values,
                                         source_population_node_config,
                                         target_population_node_config,
                                         components_path):
    ''' post processing function to add computed properties on edges
    '''
    #TODO manage edge_config and virtual nodes and so on
    from collections import defaultdict
    synapse_data = defaultdict(list)
    if source_population_node_config['type'] == 'biophysical':
        for node_id in source_node_ids:
            efferent_data = generate_synapse_data(
                node_values[population_config['source']], node_id,
                source_population_node_config['morphologies_swc'],
                components_path, "pre")
            synapse_data['efferent_section_id'].append(
                efferent_data['section_id'])
            synapse_data['efferent_segment_id'].append(
                efferent_data['segment_id'])
            synapse_data['efferent_center_x'].append(
                efferent_data['point_position'][0])
            synapse_data['efferent_center_y'].append(
                efferent_data['point_position'][1])
            synapse_data['efferent_center_z'].append(
                efferent_data['point_position'][2])
            synapse_data['efferent_surface_x'].append(
                efferent_data['surface_point_position'][0])
            synapse_data['efferent_surface_y'].append(
                efferent_data['surface_point_position'][1])
            synapse_data['efferent_surface_z'].append(
                efferent_data['surface_point_position'][2])
            #TODO manage section type
            synapse_data['efferent_section_type'] = 3
            #TODO efferent_section_pos
            synapse_data['efferent_segment_offset'].append(
                efferent_data['offset'])

    for node_id in target_node_ids:
        afferent_data = generate_synapse_data(
            node_values[population_config['target']], node_id,
            target_population_node_config['morphologies_swc'], components_path,
            "post")
        synapse_data['afferent_section_id'].append(afferent_data['section_id'])
        synapse_data['afferent_segment_id'].append(afferent_data['segment_id'])
        synapse_data['afferent_center_x'].append(
            afferent_data['point_position'][0])
        synapse_data['afferent_center_y'].append(
            afferent_data['point_position'][1])
        synapse_data['afferent_center_z'].append(
            afferent_data['point_position'][2])
        synapse_data['afferent_surface_x'].append(
            afferent_data['surface_point_position'][0])
        synapse_data['afferent_surface_y'].append(
            afferent_data['surface_point_position'][1])
        synapse_data['afferent_surface_z'].append(
            afferent_data['surface_point_position'][2])
        #TODO use morphio type ?
        synapse_data['afferent_section_type'].append(2)
        #TODO afferent_section_pos
        synapse_data['afferent_segment_offset'].append(afferent_data['offset'])
    synapse_data['source_node_id'] = source_node_ids
    synapse_data['target_node_id'] = target_node_ids
    synapse_data['edge_type_id'] = [-1] * len(source_node_ids)
    return {k: np.array(v) for (k, v) in synapse_data.items()}


def generate_edge_datasets(edge_type_config, edge_population_config,
                           node_values, source_population_node_config,
                           target_population_node_config, components_path):
    ''' generate a dict of dataset for each element of edge_type_config '''
    generated_dataset = generate_properties_dataset(edge_type_config,
                                                    edge_population_config)
    source_node_ids, target_node_ids = generate_source_target_ids(
        edge_population_config, source_population_node_config,
        target_population_node_config)
    synapse_data = generate_computed_properties_dataset(
        edge_type_config, edge_population_config, source_node_ids,
        target_node_ids, node_values, source_population_node_config,
        target_population_node_config, components_path)

    return {**generated_dataset, **synapse_data}
