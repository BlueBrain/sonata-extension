from collections import namedtuple
from pathlib import Path

import h5py
import numpy as np
from morphio.mut import Morphology
from morph_tool.transform import transform as transformation
from scipy.spatial.transform import Rotation

NodePopulationInfo = namedtuple('NodePopulationInfo', ["filepath", "name", "type", "size",
                                                       "morphologies_asc", "morphologies_swc",
                                                       "morphologies_h5",
                                                       "biophysical_neuron_models_dir"])

EdgePopulationInfo = namedtuple('EdgePopulationInfo', ["filepath", "name", "type", "size",
                                                       "source", "target", "edge_connection"])


def collect_node_populations(usecase_config, output_dir, components_path=None, filter_types=None):
    """Collection information from the usecase config and reformat it in a more usable class.

    The paths are absolute and adds the output directory as the base directory.
    """

    def get_component(property_name):
        value = population.get(property_name)
        return value if value is None else components_path / value

    output_dir = Path(output_dir)
    if components_path:
        components_path = Path(components_path)
    node_populations = []
    for file in usecase_config["nodes"]:
        for population in file['populations']:
            type_ = population["type"]
            if filter_types and type_ != filter_types:
                continue
            filepath = output_dir / file["filepath"]
            name = population["name"]
            size = population.get("size")
            morphologies_asc = get_component("morphologies_asc")
            morphologies_swc = get_component("morphologies_swc")
            morphologies_h5 = get_component("morphologies_h5")
            biophysical_neuron_models_dir = get_component("biophysical_neuron_models_dir")
            node = NodePopulationInfo(filepath, name, type_, size,
                                      morphologies_asc, morphologies_swc, morphologies_h5,
                                      biophysical_neuron_models_dir)
            node_populations.append(node)
    return node_populations


def collect_edge_populations(usecase_config, output_dir, components_path=None, filter_types=None):
    """Collection information from the usecase config and reformat it in a more usable class.

    The paths are absolute and adds the output directory as the base directory.
    """

    def get_component(property_name):  # keep it if needed in the future
        value = population.get(property_name)
        return value if value is None else components_path / value

    output_dir = Path(output_dir)
    if components_path:
        components_path = Path(components_path)
    edge_populations = []
    node_populations = collect_node_populations(usecase_config, output_dir,
                                                components_path=components_path)
    node_populations = {node_population.name: node_population for node_population in
                        node_populations}
    for file in usecase_config["edges"]:
        for population in file['populations']:
            type_ = population["type"]
            if filter_types and type_ != filter_types:
                continue
            filepath = output_dir / file["filepath"]
            name = f'{population["source"]}__{population["target"]}__{type_}'
            size = population["size"]
            source = node_populations[population["source"]]
            target = node_populations[population["target"]]
            edge_connection = population.get("edge_connection")
            node = EdgePopulationInfo(filepath, name, type_, size, source, target, edge_connection)
            edge_populations.append(node)
    return edge_populations


def load_morphology(node_population, node_id, morph_type=".swc", transform=False):
    """Load a morphology for a given node id from a given population.

    Args:
        node_population(NodePopulationInfos): a NodePopulationInfos containing the
            information about the population.
        node_id(int): the node id you want to access.
        morph_type(str): the morphology type
        transform(bool): apply the transformation rotation + translation of the morphology

    Returns:
        morphio.Morphology: A morphio immutable morphology.
    """

    def _get(prop):
        return h5[f'nodes/{node_population.name}/0/{prop}'][node_id]

    dispath = {
        ".asc": node_population.morphologies_asc,
        ".swc": node_population.morphologies_swc,
        ".h5": node_population.morphologies_h5,
    }

    with h5py.File(node_population.filepath, "r") as h5:
        if f"nodes/{node_population.name}/0/@library/morphology" in h5:
            morph_lib = h5[f"nodes/{node_population.name}/0/@library/morphology"].asstr()
            morph_name = morph_lib[h5[f"nodes/{node_population.name}/0/morphology"][node_id]]
        else:
            morph_name = h5[f"nodes/{node_population.name}/0/morphology"].asstr()[node_id]

        filename = morph_name + morph_type
        filepath = Path(dispath[morph_type], filename)
        morph = Morphology(filepath)
        if transform:
            x = _get("x")
            y = _get("y")
            z = _get("z")
            qw = _get("orientation_w")
            qx = _get("orientation_x")
            qy = _get("orientation_y")
            qz = _get("orientation_z")
            T = np.eye(4)
            T[:3, :3] = Rotation.from_quat([qx, qy, qz, qw]).as_matrix()
            T[:3, 3] = np.array([x, y, z])
            transformation(morph, T)
        return morph.as_immutable()


def segment_lengths(section):
    """Find segment lengths."""
    return np.linalg.norm(np.diff(section.points, axis=0), axis=1)


def section_length(section):
    """Find section lengths."""
    return segment_lengths(section).sum()


def get_surface_point(direction, point, distance):
    """Get a point orthogonal to a line defined by (direction, point) at a distance of point."""
    a, b, c = direction
    orth_direction = np.array([-b, a, 0])
    surface_point = point + orth_direction * distance / np.linalg.norm(orth_direction)
    return surface_point


def get_edge_population_name(population_config):
    source = population_config['source']
    target = population_config['target']
    type_ = population_config['type']
    return f"{source}__{target}__{type_}"
