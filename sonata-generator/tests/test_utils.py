# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import yaml
import numpy.testing as npt

import sonata_generator.utils as tested

from utils import tmp_file, create_simple_morph, create_node

TEST_DIR = Path(__file__).resolve().parent
TEST_DATA_DIR = TEST_DIR / 'data'


def test_collect_populations():
    test_yaml = '''
    nodes:
      - filepath: nodes.h5
        populations:
          - name: CircuitA
            type: biophysical
            size: 2
            morphologies_asc: CircuitA/morphologies/asc
            morphologies_swc: CircuitA/morphologies/swc
            biophysical_neuron_models_dir: CircuitA/hoc
          - name: VirtualPopA
            type: virtual
            size: 2

    edges:
      - filepath: edges.h5
        populations:
          - source: CircuitA
            target: CircuitA
            type: chemical
            size: 4
      - filepath: projections.h5
        populations:
          - source: VirtualPopA
            target: CircuitA
            type: chemical
            size: 4
    '''
    with tmp_file(test_yaml, cleanup=True) as (dirpath, setup_file):
        config = yaml.full_load(open(setup_file))
        observed = tested.collect_node_populations(config, dirpath, components_path="dummy")
        assert len(observed) == 2
        observed = tested.collect_node_populations(config, dirpath, components_path="dummy",
                                                   filter_types="biophysical")
        assert len(observed) == 1
        observed = observed[0]
        assert observed.name == "CircuitA"
        assert observed.size == 2
        assert observed.morphologies_asc == Path("dummy/CircuitA/morphologies/asc")
        assert observed.morphologies_swc == Path("dummy/CircuitA/morphologies/swc")
        assert observed.morphologies_h5 is None

        observed = tested.collect_edge_populations(config, dirpath, components_path="dummy")
        assert len(observed) == 2
        observed = observed[1]
        assert observed.name == "VirtualPopA__CircuitA__chemical"
        assert observed.source.name == "VirtualPopA"
        assert observed.target.name == "CircuitA"
        assert observed.target.filepath == Path(dirpath) / "nodes.h5"


def test_load_morphology():
    name_a = "nodeA"
    node_a_size = 2
    morph_global_path = "morphologies"
    morph_swc_relative_path = "swc"

    content = f"""
    nodes:
      - filepath: nodes.h5
        populations:
          - name: {name_a}
            size: {node_a_size}
            type: biophysical
            morphologies_asc: dummy
            morphologies_swc:  {morph_swc_relative_path}
            biophysical_neuron_models_dir: dummy
"""
    with tmp_file(content, cleanup=True) as (dirpath, setup_file):
        Path(dirpath, morph_global_path, morph_swc_relative_path).mkdir(parents=True)
        create_simple_morph(Path(dirpath, morph_global_path, morph_swc_relative_path))
        create_node(dirpath, name_a, node_a_size)
        config = yaml.full_load(open(setup_file))
        info = tested.collect_node_populations(config, dirpath, components_path=str(
            Path(dirpath, morph_global_path)))[0]
        morph = tested.load_morphology(info, 1)
        assert len(morph.sections) == 6
        npt.assert_allclose(morph.sections[0].points[0], [10, 0, 0])

        morph = tested.load_morphology(info, 1, transform=True)
        assert len(morph.sections) == 6
        # 10 shift along x
        npt.assert_allclose(morph.soma.points[0], [10, 0, 0])
        # rot 180 deg y + 10 shift along x
        npt.assert_allclose(morph.sections[0].points[0], [0, 0, 0])
