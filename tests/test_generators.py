from pathlib import Path

import h5py
import numpy as np
import yaml
import pytest

from sonata_generator.utils import collect_node_populations, collect_edge_populations
import sonata_generator.generators as tested
from sonata_generator.exceptions import GeneratorError

from utils import tmp_file

TEST_DIR = Path(__file__).resolve().parent
TEST_DATA_DIR = TEST_DIR / 'data'


class CustomNodeGenerator(tested.NodeGenerator):
    UNIFORM_DATA = ["a", "b", "c"]
    CHOICE_DATA = ["d"]

    @property
    def _ok_types(self):
        return ["tested"]


class UniformNodeGenerator(tested.NodeGenerator):
    UNIFORM_DATA = ["a"]

    @property
    def _ok_types(self):
        return ["tested"]


class CustomEdgeGenerator(tested.EdgeGenerator):
    UNIFORM_DATA = ["a", "b", "c"]
    CHOICE_DATA = ["d"]

    @property
    def _ok_source_types(self):
        return ["tested"]

    @property
    def _ok_target_types(self):
        return ["tested"]

    @property
    def _ok_types(self):
        return ["edge_tested"]


def _generate_sample(setup_file, config_yaml, output_path, morph_path, cls, type_):
    use_case = yaml.full_load(open(setup_file))
    config = yaml.full_load(config_yaml)
    if cls.__base__ is tested.NodeGenerator:
        info = collect_node_populations(use_case, output_path, components_path=morph_path,
                                        filter_types=type_)[0]
    else:
        info = collect_edge_populations(use_case, output_path, components_path=morph_path,
                                        filter_types=type_)[0]
    tested_obj = cls(info, config)
    tested_obj.create_data()
    tested_obj.save()
    return tested_obj


def test_node_generator():
    name_a = "nodeA"
    node_a_size = 2
    morph_path = "morphologies"
    type_ = "tested"
    content = f"""
nodes:
  - filepath: nodes.h5
    populations:
      - name: {name_a}
        size: {node_a_size}
        type: {type_}
        morphologies_asc: dummy
        morphologies_swc:  {morph_path}
        biophysical_neuron_models_dir: dummy
"""
    test_node_config_yaml = """
tested:
  a:
    type: int
    values: [10, 15]
  b:
    type: float
    values: [1.0, 10.0]
  c:
    type: float
    values: [1.0, 10.0]
  d:
    type: text
    values: ["v1", "v2", "v3"]
"""
    with tmp_file(content, cleanup=True) as (dirpath, setup_file):
        tested_obj = _generate_sample(setup_file, test_node_config_yaml, dirpath, morph_path,
                                      CustomNodeGenerator, type_)
        with h5py.File(tested_obj.info.filepath) as h5:
            assert list(h5[f"nodes/{name_a}/"]) == ['0', 'node_type_id']
            assert len(h5[f"nodes/{name_a}/node_type_id"]) == node_a_size
            assert np.unique(h5[f"nodes/{name_a}/node_type_id"]) == np.array([-1])

            observed = list(h5[f"nodes/{name_a}/0"])
            assert observed == ['a', 'b', 'c', 'd']
            assert h5[f"nodes/{name_a}/0/a"].dtype == np.int64
            assert h5[f"nodes/{name_a}/0/b"].dtype == np.float32
            assert h5[f"nodes/{name_a}/0/c"].dtype == np.float32
            assert h5[f"nodes/{name_a}/0/d"].asstr()[:].dtype == object

            assert len(h5[f"nodes/{name_a}/0/a"]) == node_a_size
            assert len(h5[f"nodes/{name_a}/0/b"]) == node_a_size
            assert len(h5[f"nodes/{name_a}/0/c"]) == node_a_size
            assert len(h5[f"nodes/{name_a}/0/d"]) == node_a_size

            assert np.all((h5[f"nodes/{name_a}/0/a"][:] >= 10)
                          & (h5[f"nodes/{name_a}/0/a"][:] <= 15))

            assert np.all((h5[f"nodes/{name_a}/0/b"][:] >= 1.0)
                          & (h5[f"nodes/{name_a}/0/b"][:] <= 10.0))

            assert np.all(np.isin(h5[f"nodes/{name_a}/0/d"].asstr()[:], ["v1", "v2", "v3"]))


def test_bad_properties():
    name_a = "nodeA"
    content = f"""
    nodes:
      - filepath: nodes.h5
        populations:
          - name: {name_a}
            size: 2
            type: tested
            morphologies_asc: dummy
            morphologies_swc: morpho
            biophysical_neuron_models_dir: dummy
"""
    with tmp_file(content, cleanup=True) as (dirpath, setup_file):
        def _assert_error_at_creation(node_config):
            with pytest.raises(GeneratorError):
                _generate_sample(setup_file, node_config, dirpath, 'dummy', UniformNodeGenerator,
                                 'tested')

        triple_uniform = """
        tested:
          a:
            type: int
            values: [10, 15, 11]
        """
        _assert_error_at_creation(triple_uniform)

        text_uniform = """
        tested:
          a:
            type: text
            values: ["v1", "v2"]
        """
        _assert_error_at_creation(text_uniform)

        extra_value = """
        tested:
          a:
            type: int
            values: [1, 2]
          b:
            type: int
            values: [1, 2]
        """
        _assert_error_at_creation(extra_value)  # the UniformGenerator contains only "a" as uniform

        unknown_type = """
        tested:
          a:
            type: unknown
            values: [1, 2]
        """
        _assert_error_at_creation(unknown_type)


def test_edge_generator():
    source_name_a = "nodeA"
    target_name_a = "nodeB"
    edge_a_size = 2
    morph_path = "morphologies"
    type_ = "edge_tested"
    content = f"""
nodes:
  - filepath: nodes.h5
    populations:
      - name: {source_name_a}
        size: 2
        type: tested
        morphologies_asc: dummy
        morphologies_swc: morpho
        biophysical_neuron_models_dir: dummy
      - name: {target_name_a}
        size: 15
        type: tested
        morphologies_asc: dummy
        morphologies_swc: morpho
        biophysical_neuron_models_dir: dummy
edges:
  - filepath: edges.h5
    populations:
      - source: {source_name_a}
        target: {target_name_a}
        size: {edge_a_size}
        type: {type_}
"""
    test_node_config_yaml = """
edge_tested:
  a:
    type: int
    values: [10, 15]
  b:
    type: float
    values: [1.0, 10.0]
  c:
    type: float
    values: [1.0, 10.0]
  d:
    type: text
    values: ["v1", "v2", "v3"]
"""
    with tmp_file(content, cleanup=True) as (dirpath, setup_file):
        tested_obj = _generate_sample(setup_file, test_node_config_yaml, dirpath, morph_path,
                                      CustomEdgeGenerator, type_)
        expected_name = f"{source_name_a}__{target_name_a}__{type_}"
        assert tested_obj.info.name == expected_name
        with h5py.File(tested_obj.info.filepath) as h5:
            name_a = expected_name
            assert list(h5[f"edges/{name_a}/"]) == ['0', 'edge_type_id', 'indices',
                                                    'source_node_id', 'target_node_id']
            assert len(h5[f"edges/{name_a}/edge_type_id"]) == edge_a_size
            assert np.unique(h5[f"edges/{name_a}/edge_type_id"]) == np.array([-1])

            assert np.all((h5[f"edges/{name_a}/source_node_id"][:] < 2))
            assert np.all((h5[f"edges/{name_a}/target_node_id"][:] < 15))
            assert h5[f"edges/{name_a}/target_node_id"].attrs["node_population"] == target_name_a
            assert h5[f"edges/{name_a}/source_node_id"].attrs["node_population"] == source_name_a

            observed = list(h5[f"edges/{name_a}/0"])
            assert observed == ['a', 'b', 'c', 'd']
            assert h5[f"edges/{name_a}/0/a"].dtype == np.int64
            assert h5[f"edges/{name_a}/0/b"].dtype == np.float32
            assert h5[f"edges/{name_a}/0/c"].dtype == np.float32
            assert h5[f"edges/{name_a}/0/d"].asstr()[:].dtype == object

            assert len(h5[f"edges/{name_a}/0/a"]) == edge_a_size
            assert len(h5[f"edges/{name_a}/0/b"]) == edge_a_size
            assert len(h5[f"edges/{name_a}/0/c"]) == edge_a_size
            assert len(h5[f"edges/{name_a}/0/d"]) == edge_a_size

            assert np.all((h5[f"edges/{name_a}/0/a"][:] >= 10)
                          & (h5[f"edges/{name_a}/0/a"][:] <= 15))

            assert np.all((h5[f"edges/{name_a}/0/b"][:] >= 1.0)
                          & (h5[f"edges/{name_a}/0/b"][:] <= 10.0))

            assert np.all(np.isin(h5[f"edges/{name_a}/0/d"].asstr()[:], ["v1", "v2", "v3"]))
