from pathlib import Path
import shutil

import h5py
import numpy as np
import numpy.testing as npt
import yaml

from sonata_generator.utils import collect_node_populations, collect_edge_populations
import sonata_generator.neuronal_generators as tested

from utils import tmp_file, create_simple_morph, create_node

TEST_DIR = Path(__file__).resolve().parent
TEST_DATA_DIR = TEST_DIR / 'data'


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


def test_biophysical_generator():
    name_a = "nodeA"
    node_a_size = 2
    component_global_path = "component"
    morph_swc_relative_path = "swc"
    bio_path = "hoc"
    type_ = "biophysical"
    content = f"""
nodes:
  - filepath: nodes.h5
    populations:
      - name: {name_a}
        size: {node_a_size}
        type: {type_}
        morphologies_asc: dummy
        morphologies_swc: {morph_swc_relative_path}
        biophysical_neuron_models_dir: {bio_path}
"""
    test_node_config_yaml = """
biophysical:
  x:
    type: float
    values: [ -1000.0, 1000 ]
  y:
    type: float
    values: [ -1000.0, 1000 ]
  z:
    type: float
    values: [ -1000.0, 1000 ]
  orientation_w:
    type: float
    values: [ -1.0, 1.0 ]
  orientation_x:
    type: float
    values: [ -1.0, 1.0 ]
  orientation_y:
    type: float
    values: [ -1.0, 1.0 ]
  orientation_z:
    type: float
    values: [ -1.0, 1.0 ]
  morphology:
    type: text
    values: morphology
  model_template:
    type: text
    values: emodel
  layer:
    type: text
    values: [ 'LA', 'LB', 'LC' ]
  model_type:
    type: text
    values: [ 'biophysical' ]
  morph_class:
    type: text
    values: [ "PYR", "INT" ]
  etype:
    type: text
    values: [ "dNAC", "dSTUT" ]
  mtype:
    type: text
    values: [ 'L5_PC', 'L4_PC', 'L4_MC' ]
  synapse_class:
    type: text
    values: [ "EXC", "INH" ]
  region:
    type: text
    values: [ 'RA', 'RB' ]
  dynamics_params/threshold_current:
    type: float
    values: [ 1.0, 2.0 ]
  dynamics_params/holding_current:
    type: float
    values: [ 1.0, 2.0 ]
  dynamics_params/AIS_scaler:
    type: float
    values: [ 1.0, 2.0 ]
  minis:
    type: float
    values: [ 0, 100 ]
  hemisphere:
    type: text
    values: [ 'left', 'right' ]
"""
    with tmp_file(content, cleanup=True) as (dirpath, setup_file):
        shutil.copytree(Path(TEST_DATA_DIR, "morphologies"), Path(dirpath, component_global_path, morph_swc_relative_path))
        shutil.copytree(Path(TEST_DATA_DIR, "hoc"), Path(dirpath, component_global_path, bio_path))
        tested_obj = _generate_sample(setup_file, test_node_config_yaml, dirpath, Path(dirpath, component_global_path),
                                      tested.BiophysicalGenerator, type_)

        with h5py.File(tested_obj.info.filepath) as h5:
            assert set(h5[f"nodes/{name_a}/"]) == {'0', 'node_type_id'}
            assert len(h5[f"nodes/{name_a}/node_type_id"]) == node_a_size
            assert np.unique(h5[f"nodes/{name_a}/node_type_id"]) == np.array([-1])

            observed = set(h5[f"nodes/{name_a}/0"])
            assert "morphology" in observed
            assert "model_template" in observed

            # other values are tested in the normal generator tests (uniform or choice variables)
            assert np.all(np.isin(h5[f"nodes/{name_a}/0/model_template"].asstr()[:], ["hoc:cADpyr_L2TPC", "hoc:cNAC_L23BTC"]))
            assert np.all(np.isin(h5[f"nodes/{name_a}/0/morphology"].asstr()[:], ["C270106C_-_Scale_x1.000_y1.050_z1.000", "sm100330b1-2_idB", "vd130423_idC"]))


def test_virtual_node_generator():
    name_a = "nodeA"
    node_a_size = 2
    component_global_path = "component"
    morph_swc_relative_path = "swc"
    bio_path = "hoc"
    type_ = "virtual"
    content = f"""
nodes:
  - filepath: nodes.h5
    populations:
      - name: {name_a}
        size: {node_a_size}
        type: {type_}
"""
    test_node_config_yaml = """
virtual:
  model_type:
    type: text
    values: [ 'virtual' ]
  model_template:
    type: text
    values: null
"""
    with tmp_file(content, cleanup=True) as (dirpath, setup_file):
        shutil.copytree(Path(TEST_DATA_DIR, "morphologies"), Path(dirpath, component_global_path, morph_swc_relative_path))
        shutil.copytree(Path(TEST_DATA_DIR, "hoc"), Path(dirpath, component_global_path, bio_path))
        tested_obj = _generate_sample(setup_file, test_node_config_yaml, dirpath, Path(dirpath, component_global_path),
                                      tested.VirtualGenerator, type_)

        with h5py.File(tested_obj.info.filepath) as h5:
            assert set(h5[f"nodes/{name_a}/"]) == {'0', 'node_type_id'}
            assert len(h5[f"nodes/{name_a}/node_type_id"]) == node_a_size
            assert np.unique(h5[f"nodes/{name_a}/node_type_id"]) == np.array([-1])

            observed = set(h5[f"nodes/{name_a}/0"])
            assert "model_type" in observed
            assert "model_template" in observed

            # other values are tested in the normal generator tests (uniform or choice variables)
            npt.assert_array_equal(h5[f"nodes/{name_a}/0/model_type"].asstr()[:], ["virtual", "virtual"])
            npt.assert_array_equal(h5[f"nodes/{name_a}/0/model_template"].asstr()[:], ["", ""])


CONFIG_CHEMICAL = """chemical:
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
    type: uint32
    values: derived
  afferent_section_pos:
    type: float
    values: derived
  afferent_section_type:
    type: uint32
    values: derived
  afferent_segment_id:
    type: uint32
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
    type: uint32
    values: derived
  efferent_section_pos:
    type: float
    values: derived
  efferent_section_type:
    type: uint32
    values: derived
  efferent_segment_id:
    type: uint32
    values: derived
  efferent_segment_offset:
    type: float
    values: derived
  conductance:
    type: float
    values: [0.10, 0.5]
  decay_time:
    type: float
    values: [1.5, 2.0]
  depression_time:
    type: float
    values: [600.0, 700.0]
  facilitation_time:
    type: float
    values: [5.0, 25.0]
  u_syn:
    type: float
    values: [0.5, 0.55]
  n_rrp_vesicles:
    type: uint32
    values: [1, 5]
  spine_length:
    type: float
    values: [0.1, 10000]
  conductance_scale_factor:
    type: float
    values: [0.1, 1.0]
  u_hill_coefficient:
    type: float
    values: [1.0, 2.0]
  syn_type_id:
    type: uint32
    values: [0, 120]
  delay:
    type: float
    values: [0, 10.0]
"""


def test_chemical_edge_generator():
    name_a = "nodeA"
    node_a_size = 2
    morph_global_path = "morphologies"
    morph_swc_relative_path = "swc"
    type_ = "chemical"
    edge_a_size = 4
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

edges:
  - filepath: edges.h5
    populations:
      - source: {name_a}
        target: {name_a}
        type: {type_}
        size: {edge_a_size}
"""
    with tmp_file(content, cleanup=True) as (dirpath, setup_file):
        Path(dirpath, morph_global_path, morph_swc_relative_path).mkdir(parents=True)
        create_simple_morph(Path(dirpath, morph_global_path, morph_swc_relative_path))
        create_node(dirpath, name_a, node_a_size)
        tested_obj = _generate_sample(setup_file, CONFIG_CHEMICAL, dirpath, str(Path(dirpath, morph_global_path)),
                         tested.ChemicalGenerator, "chemical")
        expected_name = f"{name_a}__{name_a}__{type_}"
        assert tested_obj.info.name == expected_name
        with h5py.File(tested_obj.info.filepath) as h5:
            name_edge = expected_name
            assert set(h5[f"edges/{name_edge}/"]) == {
                '0', 'edge_type_id', 'indices', 'source_node_id', 'target_node_id'
            }
            assert len(h5[f"edges/{name_edge}/edge_type_id"]) == edge_a_size
            assert h5[f"edges/{name_edge}/edge_type_id"].dtype.name == "int64"
            assert np.unique(h5[f"edges/{name_edge}/edge_type_id"]) == np.array([-1])

            assert np.all((h5[f"edges/{name_edge}/source_node_id"][:] < node_a_size))
            assert h5[f"edges/{name_edge}/source_node_id"].dtype.name == "uint64"
            assert np.all((h5[f"edges/{name_edge}/target_node_id"][:] < node_a_size))
            assert h5[f"edges/{name_edge}/target_node_id"].dtype.name == "uint64"

            assert h5[f"edges/{name_edge}/target_node_id"].attrs["node_population"] == name_a
            assert h5[f"edges/{name_edge}/source_node_id"].attrs["node_population"] == name_a

            couples = np.column_stack([h5[f"edges/{name_edge}/source_node_id"][:], h5[f"edges/{name_edge}/target_node_id"][:]])
            # source node and target nodes are the same population so we should not have the source - target == 0
            diff = couples[:, 0] - couples[:, 1]
            assert np.all(diff != 0)

            assert np.all((h5[f"edges/{name_edge}/0/afferent_section_id"][:] >= 3) & (h5[f"edges/{name_edge}/0/afferent_section_id"][:] < 6))
            assert np.all((h5[f"edges/{name_edge}/0/afferent_segment_id"][:] < 3))
            assert np.all((h5[f"edges/{name_edge}/0/afferent_section_pos"][:] <= 1))
            assert np.all(np.isin(h5[f"edges/{name_edge}/0/afferent_section_type"][:], [2, 3]))
            assert np.all(h5[f"edges/{name_edge}/0/afferent_segment_offset"][:] <= 100)

            assert np.all((h5[f"edges/{name_edge}/0/efferent_section_id"][:] < 3))
            assert np.all((h5[f"edges/{name_edge}/0/efferent_segment_id"][:] < 3))
            assert np.all((h5[f"edges/{name_edge}/0/efferent_section_pos"][:] <= 1))
            assert np.all(h5[f"edges/{name_edge}/0/efferent_section_type"][:] == 1)
            assert np.all(h5[f"edges/{name_edge}/0/efferent_segment_offset"][:] <= 10)

            # Test a few of the uint32 types
            int_types = {h5[f"edges/{name_edge}/0/{prop}"].dtype.name for prop in (
                "afferent_section_type",
                "afferent_section_id",
                "afferent_segment_id",
                "efferent_section_type",
                "efferent_section_id",
                "efferent_segment_id",
            )}
            assert int_types == {'uint32'}

            cx = h5[f"edges/{name_edge}/0/afferent_center_x"][0]
            cy = h5[f"edges/{name_edge}/0/afferent_center_y"][0]
            cz = h5[f"edges/{name_edge}/0/afferent_center_z"][0]
            cpoint = np.array([cx, cy, cz])

            sx = h5[f"edges/{name_edge}/0/afferent_surface_x"][0]
            sy = h5[f"edges/{name_edge}/0/afferent_surface_y"][0]
            sz = h5[f"edges/{name_edge}/0/afferent_surface_z"][0]
            spoint = np.array([sx, sy, sz])

            npt.assert_almost_equal(np.linalg.norm(cpoint - spoint), 1)


def test_chemical_projection_edge_generator():
    source_name = "virtualNodeA"
    target_name = "nodeA"
    target_size = 2
    source_size = 15
    morph_global_path = "morphologies"
    morph_swc_relative_path = "swc"
    type_ = "chemical"
    edge_a_size = 4
    content = f"""
nodes:
  - filepath: nodes.h5
    populations:
      - name: {target_name}
        size: {target_size}
        type: biophysical
        morphologies_asc: dummy
        morphologies_swc:  {morph_swc_relative_path}
        biophysical_neuron_models_dir: dummy
      - name: {source_name}
        size: {source_size}
        type: virtual

edges:
  - filepath: edges.h5
    populations:
      - source: {source_name}
        target: {target_name}
        type: {type_}
        size: {edge_a_size}
"""
    with tmp_file(content, cleanup=True) as (dirpath, setup_file):
        Path(dirpath, morph_global_path, morph_swc_relative_path).mkdir(parents=True)
        create_simple_morph(Path(dirpath, morph_global_path, morph_swc_relative_path))
        create_node(dirpath, target_name, target_size)
        tested_obj = _generate_sample(setup_file, CONFIG_CHEMICAL, dirpath,
                                      str(Path(dirpath, morph_global_path)),
                                      tested.ChemicalGenerator, "chemical")
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

            for prop in h5[f"edges/{name_edge}/0/"]:
                assert not prop.startswith("efferent") or prop == "efferent_section_type"
                assert prop != "spine_length"
