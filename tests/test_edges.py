import os
import tempfile

import numpy as np
import pytest
import sonata_generator.generators as generators
import sonata_generator.writer as writer
from morphio import PointLevel, SectionType

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, "data")
np.random.seed(1)


def create_simple_morph():
    import morphio.mut

    morpho = morphio.mut.Morphology()
    morpho.soma.points = [[0, 0, 0]]
    morpho.soma.diameters = [0.5]

    section = morpho.append_root_section(
        PointLevel(
            [[10, 0, 0], [20, 0, 0], [30, 0, 0]
             ],  # x, y, z coordinates of each point
            [1, 1, 1],  # diameter of each point
        ),
        SectionType.axon)  # (optional) perimeter of each point

    section.append_section(
        PointLevel(
            [[30, 0, 0], [40, 0, 0], [50, 0, 0]],
            [1, 1, 1],
        ))

    section = morpho.append_root_section(
        PointLevel(
            [[0, 10, 0], [0, 20, 0], [0, 30, 0]
             ],  # x, y, z coordinates of each point
            [1, 1, 1],  # diameter of each point
        ),
        SectionType.basal_dendrite)  # (optional) perimeter of each point

    child_section = section.append_section(
        PointLevel(
            [[0, 30, 0], [0, 40, 0], [0, 50, 0]],
            [1, 1, 1],
        ))
    temp_dir = tempfile.mkdtemp()
    morpho.write(os.path.join(temp_dir, "morph.h5"))
    import morphio
    m = morphio.Morphology(os.path.join(temp_dir, "morph.h5"))
    return m


def test_get_surface_point():
    point = np.array([.5, 0, 0])
    direction = np.array([1, 0, 0])
    distance = 1.0
    surface_point = generators.get_surface_point(direction, point, distance)
    assert (np.array_equal(surface_point, np.array([0.5, 1, 0])))


def test_create_synapse():
    m = create_simple_morph()
    pre_section_id, pre_segment_id, pre_point, pre_offset, pre_surface, pre_section_type = generators.create_synapse(
        m, "pre")
    assert (0 < pre_section_id < 3)
    assert (0 <= pre_segment_id < 3)
    # check surface point is at the surface based on next assert
    assert (np.linalg.norm(pre_point - pre_surface) == pytest.approx(0.5))
    assert (pre_point[1] == 0)
    assert (pre_point[2] == 0)
    assert (0 < pre_offset < 10.0)
    # check point is compatible with section / segment / offset
    assert (pre_point[0] == pytest.approx(10 + 10 * pre_segment_id + 20 *
                                          (pre_section_id - 1) + pre_offset))
    # check surface point orthogonal to segment
    assert (np.dot(np.array([10, 0, 0]) - pre_point,
                   pre_surface - pre_point) == pytest.approx(0))
    assert (pre_section_type == SectionType.axon)
    post_section_id, post_segment_id, post_point, post_offset, post_surface, post_section_type = generators.create_synapse(
        m, "post")
    assert (2 < post_section_id < 5)
    assert (0 <= post_segment_id < 3)
    assert (0 < post_offset < 10.0)
    assert (post_point[0] == 0)
    # check point is compatible with section / segment / offset
    assert (post_point[1] == pytest.approx(10 + 10 * post_segment_id + 20 *
                                           (post_section_id - 3) +
                                           post_offset))
    assert (post_point[2] == 0)
    # check surface point is at the surface based on next assert
    assert (np.linalg.norm(post_point - post_surface) == pytest.approx(0.5))
    # check surface point orthogonal to segment
    assert (np.dot(
        np.array([0, 10, 0]) - post_point,
        post_surface - post_point) == pytest.approx(0))
    assert (post_section_type == SectionType.basal_dendrite)


def test_generate_edge_datasets():
    edge_type_config = {
        "propInt": {
            "type": "int",
            "values": [1, 9]
        },
        "propFloat": {
            "type": "float",
            "values": [1.0, 9.0]
        },
        "propText": {
            "type": "text",
            "values": ["A", "B", "C"]
        },
        "propEnum": {
            "type": "enum",
            "values": ["A", "B", "C"]
        },
        "propDerived": {
            "type": "float",
            "values": "derived"
        },
        "source_node_id": {
            "type": "int",
            "values": "derived"
        },
        "target_node_id": {
            "type": "int",
            "values": "derived"
        },
        "edge_type_id": {
            "type": "int",
            "values": "derived"
        }
    }
    edge_population_config = {
        "size": 4,
        "source": "node_source",
        "target": "node_target",
    }
    node_properties_config = {
        "x": {
            "type": "float",
            "values": [1, 9]
        },
        "y": {
            "type": "float",
            "values": [1, 9]
        },
        "z": {
            "type": "float",
            "values": [1, 9]
        },
        "orientation_x": {
            "type": "float",
            "values": [1, 9]
        },
        "orientation_w": {
            "type": "float",
            "values": [1, 9]
        },
        "orientation_y": {
            "type": "float",
            "values": [1, 9]
        },
        "orientation_z": {
            "type": "float",
            "values": [1, 9]
        },
        "propFloat": {
            "type": "float",
            "values": [1.0, 9.0]
        },
        "propText": {
            "type": "text",
            "values": ["A", "B", "C"]
        },
        "propEnum": {
            "type": "enum",
            "values": ["A", "B", "C"]
        },
        "propDerived": {
            "type": "float",
            "values": "derived"
        },
        "morphology": {
            "type": "text",
            "values": "morphology"
        }
    }
    source_population_node_config = {
        'name': '',
        'morphologies_swc': "morphologies",
        'type': 'biophysical',
        'size': 2
    }
    target_population_node_config = {
        'name': '',
        'morphologies_swc': "morphologies",
        'type': 'biophysical',
        'size': 2
    }

    components_path = TEST_DATA_DIR
    node_values = {}
    node_values["node_source"] = generators.generate_properties_dataset(
        node_properties_config, source_population_node_config, components_path)
    node_values["node_target"] = generators.generate_properties_dataset(
        node_properties_config, target_population_node_config, components_path)

    edge_values = generators.generate_edge_datasets(
        edge_type_config, edge_population_config, node_values,
        source_population_node_config, target_population_node_config,
        components_path)
    for prop in [
            'efferent_center_x',
            'efferent_center_y',
            'efferent_center_z',
            'afferent_center_x',
            'afferent_center_y',
            'afferent_center_z',
            'efferent_section_id',
            'afferent_section_id',
            'efferent_segment_offset',
            'afferent_segment_offset',
            'efferent_surface_x',
            'efferent_surface_y',
            'efferent_surface_z',
            'afferent_surface_x',
            'afferent_surface_y',
            'afferent_surface_z',
            'efferent_section_type',
            'afferent_section_type',
            'source_node_id',
            'target_node_id',
            'edge_type_id',
    ]:
        assert (len(edge_values[prop]) == 4)
