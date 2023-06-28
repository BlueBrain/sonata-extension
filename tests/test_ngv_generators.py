from pathlib import Path
import shutil
import logging

import h5py
import numpy as np
import numpy.testing as npt
import yaml

from sonata_generator.utils import collect_node_populations, collect_edge_populations
import sonata_generator.ngv_generators as tested

from utils import tmp_file, create_simple_morph, create_node

TEST_DIR = Path(__file__).resolve().parent
TEST_DATA_DIR = TEST_DIR / 'data'

L =logging.Logger(__name__)


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


def test_vasculature_generator():
    name_a = "nodeA"
    # this node_size will not be used in the final version due to the mesh and only the full morphology will be used
    node_a_size = 6
    type_ = "vasculature"
    component_global_path = "component"
    morph_h5_relative_path = "vasculature"
    content = f"""
nodes:
  - filepath: vasculature.h5
    populations:
      - name: {name_a}
        type: {type_}
        size: {node_a_size}
        morphologies_h5: {morph_h5_relative_path}
"""

    test_vasculature_config_yaml = """
vasculature:
  start_x:
    type: float
    values: [ -1000.0, 1000.0 ]
  start_y:
    type: float
    values: [ -1000.0, 1000.0 ]
  start_z:
    type: float
    values: [ -1000.0, 1000.0 ]
  end_x:
    type: float
    values: [ -1000.0, 1000.0 ]
  end_y:
    type: float
    values: [ -1000.0, 1000.0 ]
  end_z:
    type: float
    values: [ -1000.0, 1000.0 ]
  start_diameter:
    type: float
    values: [ 15., 30. ]
  end_diameter:
    type: float
    values: [ 15., 30. ]
  start_node_id:
    type: int
    values: derivated
  end_node_id:
    type: int
    values: derivated
  type:
    type: int
    values: [ 0, 1, 2, 3 ]
  section_id:
    type: int
    values: derivated
  segment_id:
    type: int
    values: derivated
"""
    with tmp_file(content, cleanup=True) as (dirpath, setup_file):
        shutil.copytree(Path(TEST_DATA_DIR, "vasculature"), Path(dirpath, component_global_path, morph_h5_relative_path))
        tested_obj = _generate_sample(setup_file, test_vasculature_config_yaml, dirpath, Path(dirpath, component_global_path), tested.VasculatureGenerator, type_)
        with h5py.File(tested_obj.info.filepath) as h5:
            assert set(h5[f"nodes/{name_a}/"]) == {'0', 'node_type_id'}
            assert len(h5[f"nodes/{name_a}/node_type_id"]) == 587  # from a fixed morpho
            assert np.unique(h5[f"nodes/{name_a}/node_type_id"]) == np.array([-1])

            observed = set(h5[f"nodes/{name_a}/0"])
            conf_dict = yaml.full_load(test_vasculature_config_yaml)
            for key in conf_dict["vasculature"].keys():
                if key not in observed:
                    L.warning("%s not in the final file" % key)


def test_astrocyte_generator():
    name_a = "nodeA"
    node_a_size = 2
    component_global_path = "component"
    morph_h5_relative_path = "h5"
    bio_path = "hoc"
    type_ = "astrocyte"
    content = f"""
nodes:
  - filepath: nodes.h5
    populations:
      - name: {name_a}
        size: {node_a_size}
        type: {type_}
        morphologies_asc: dummy
        morphologies_swc: dummy
        morphologies_h5: {morph_h5_relative_path}
        biophysical_neuron_models_dir: {bio_path}
"""
    test_node_config_yaml = """
astrocyte:
  x:
    type: float
    values: [ -1000.0, 1000 ]
  y:
    type: float
    values: [ -1000.0, 1000 ]
  z:
    type: float
    values: [ -1000.0, 1000 ]
  radius:
    type: float
    values: [ 4, 6 ]
  mtype:
    type: text
    values: [ 'L5_ASTRO', 'L4_ASTRO', 'L3_ASTRO' ]
  orientation_w:
    type: float
    values: [ 1 ]
  orientation_x:
    type: float
    values: [ 0 ]
  orientation_y:
    type: float
    values: [ 0 ]
  orientation_z:
    type: float
    values: [ 0 ]
  morphology:
    type: text
    values: derivated
  model_template:
    type: text
    values: derivated
  region:
    type: text
    values: [ 'RA', 'RB' ]
  model_type:
    type: text
    values: [ "astrocyte" ]
"""
    with tmp_file(content, cleanup=True) as (dirpath, setup_file):
        shutil.copytree(Path(TEST_DATA_DIR, "astrocytes_morphologies"), Path(dirpath, component_global_path, morph_h5_relative_path))
        shutil.copytree(Path(TEST_DATA_DIR, "hoc"), Path(dirpath, component_global_path, bio_path))
        tested_obj = _generate_sample(setup_file, test_node_config_yaml, dirpath, Path(dirpath, component_global_path),
                                      tested.AstrocyteGenerator, type_)

        with h5py.File(tested_obj.info.filepath) as h5:
            assert set(h5[f"nodes/{name_a}/"]) == {'0', 'node_type_id'}
            assert len(h5[f"nodes/{name_a}/node_type_id"]) == node_a_size
            assert np.unique(h5[f"nodes/{name_a}/node_type_id"]) == np.array([-1])

            observed = set(h5[f"nodes/{name_a}/0"])
            assert "morphology" in observed
            assert "model_template" in observed

            # other values are tested in the normal generator tests (uniform or choice variables)
            assert np.all(np.isin(h5[f"nodes/{name_a}/0/model_template"].asstr()[:], ["hoc:cADpyr_L2TPC", "hoc:cNAC_L23BTC"]))
            assert np.all(np.isin(h5[f"nodes/{name_a}/0/morphology"].asstr()[:], ["GLIA_0000000000000", "GLIA_0000000000001"]))


ELECTRICAL = """
electrical:
  afferent_center_x:
    type: float
    values: derived
  afferent_center_y:
    type: float
    values: derived
  afferent_center_z:
    type: float
    values: derived
  afferent_surface_x:
    type: float
    values: derived
  afferent_surface_y:
    type: float
    values: derived
  afferent_surface_z:
    type: float
    values: derived
  afferent_section_id:
    type: int
    values: derived
  afferent_section_pos:
    type: float
    values: derived
  afferent_section_type:
    type: int
    values: derived
  afferent_segment_id:
    type: int
    values: derived
  afferent_segment_offset:
    type: float
    values: derived
  efferent_center_x:
    type: float
    values: derived
  efferent_center_y:
    type: float
    values: derived
  efferent_center_z:
    type: float
    values: derived
  efferent_surface_x:
    type: float
    values: derived
  efferent_surface_y:
    type: float
    values: derived
  efferent_surface_z:
    type: float
    values: derived
  efferent_section_id:
    type: int
    values: derived
  efferent_section_pos:
    type: float
    values: derived
  efferent_section_type:
    type: int
    values: derived
  efferent_segment_id:
    type: int
    values: derived
  efferent_segment_offset:
    type: float
    values: derived
  spine_length:
    type: float
    values: [ 0.1, 10000 ]
"""


def test_electrical_synapse_edge_generator():
    source_name = "astrocyteA"
    target_name = "astrocyteA"
    target_size = 2
    source_size = 2
    morph_global_path = "morphologies"
    morph_h5_relative_path = "h5"
    type_ = "electrical"
    edge_a_size = 4
    content = f"""
nodes:
  - filepath: nodes.h5
    populations:
      - name: {target_name}
        size: {target_size}
        type: astrocyte
        morphologies_asc: dummy
        morphologies_swc: dummy
        morphologies_h5: {morph_h5_relative_path}
        biophysical_neuron_models_dir: dummy

edges:
  - filepath: edges.h5
    populations:
      - source: {source_name}
        target: {target_name}
        type: {type_}
        size: {edge_a_size}
"""
    with tmp_file(content, cleanup=True) as (dirpath, setup_file):
        Path(dirpath, morph_global_path, morph_h5_relative_path).mkdir(parents=True)
        create_simple_morph(Path(dirpath, morph_global_path, morph_h5_relative_path),
                            morph_name="test_morph.h5")
        create_node(dirpath, target_name, target_size)
        tested_obj = _generate_sample(setup_file, ELECTRICAL, dirpath,
                                      str(Path(dirpath, morph_global_path)),
                                      tested.GlialGlialGenerator, type_)
        expected_name = f"{source_name}__{target_name}__{type_}"
        assert tested_obj.info.name == expected_name
        with h5py.File(tested_obj.info.filepath) as h5:
            name_edge = expected_name
            assert set(h5[f"edges/{name_edge}/"]) == {
                '0', 'edge_type_id', 'indices', 'source_node_id', 'target_node_id'
            }
            assert len(h5[f"edges/{name_edge}/edge_type_id"]) == edge_a_size
            assert np.unique(h5[f"edges/{name_edge}/edge_type_id"]) == np.array([-1])

            assert np.all((h5[f"edges/{name_edge}/source_node_id"][:] < source_size))
            assert np.all((h5[f"edges/{name_edge}/target_node_id"][:] < target_size))

            assert h5[f"edges/{name_edge}/target_node_id"].attrs["node_population"] == target_name
            assert h5[f"edges/{name_edge}/source_node_id"].attrs["node_population"] == source_name

            couples = np.column_stack([h5[f"edges/{name_edge}/source_node_id"][:],
                                       h5[f"edges/{name_edge}/target_node_id"][:]])
            # source node and target nodes are the same population so we should not have the source - target == 0
            diff = couples[:, 0] - couples[:, 1]
            assert np.all(diff != 0)

            assert np.all(h5[f"edges/{name_edge}/0/afferent_section_id"][:] < 6)
            assert np.all((h5[f"edges/{name_edge}/0/afferent_segment_id"][:] < 3))
            assert np.all((h5[f"edges/{name_edge}/0/afferent_section_pos"][:] <= 1))
            assert np.all(np.isin(h5[f"edges/{name_edge}/0/afferent_section_type"][:], [1, 2, 3]))
            assert np.all(h5[f"edges/{name_edge}/0/afferent_segment_offset"][:] <= 100)

            assert np.all((h5[f"edges/{name_edge}/0/efferent_section_id"][:] < 6))
            assert np.all((h5[f"edges/{name_edge}/0/efferent_segment_id"][:] < 3))
            assert np.all((h5[f"edges/{name_edge}/0/efferent_section_pos"][:] <= 1))
            assert np.all(h5[f"edges/{name_edge}/0/efferent_section_type"][:] < 4)
            assert np.all(h5[f"edges/{name_edge}/0/efferent_segment_offset"][:] <= 10)

            cx = h5[f"edges/{name_edge}/0/afferent_center_x"][0]
            cy = h5[f"edges/{name_edge}/0/afferent_center_y"][0]
            cz = h5[f"edges/{name_edge}/0/afferent_center_z"][0]
            cpoint = np.array([cx, cy, cz])

            sx = h5[f"edges/{name_edge}/0/afferent_surface_x"][0]
            sy = h5[f"edges/{name_edge}/0/afferent_surface_y"][0]
            sz = h5[f"edges/{name_edge}/0/afferent_surface_z"][0]
            spoint = np.array([sx, sy, sz])

            npt.assert_almost_equal(np.linalg.norm(cpoint - spoint), 1)
