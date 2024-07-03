# SPDX-License-Identifier: Apache-2.0
import os

import h5py
import numpy as np
import numpy.testing as npt
import shutil
import morphio


from unittest.mock import patch

import sonata_generator.report_generators as tested

from utils import get_from_library, tmp_file

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, "data")
SEED=2
np.random.seed(SEED)


def create_node(dirpath, pop_name, pop_size):
    filepath = os.path.join(dirpath, "nodes.h5")
    option = "r+" if os.path.exists(filepath) else "w"
    with h5py.File(filepath, option) as h5:
        pop_group = h5.create_group(f"nodes/{pop_name}")
        pop_group.create_dataset("node_type_id", data=[-1] * pop_size)
        prop = pop_group.create_group("0")
        string_dtype = h5py.special_dtype(vlen=str)
        morphlib = prop.create_dataset(
            '@library/morphology',
            data=["C270106C_-_Scale_x1.000_y1.050_z1.000", "sm100330b1-2_idB", "vd130423_idC"],
            dtype=string_dtype,
        )
        prop.create_dataset(
            'morphology',
            data=np.random.choice(range(len(morphlib)), pop_size),
            dtype=np.uint32,
        )


@patch('numpy.random.randint', return_value=3)
def test_create_frame_report(mock):
    dt = 0.1
    tstart = 0
    tend = 1
    spikes_count = 15
    name_a = "nodeA"
    name_b = "nodeB"
    name_c = "nodeC"
    node_a_size = 2
    node_b_size = 7
    morph_path = "morphologies"
    content = f"""
nodes:
  - filepath: nodes.h5
    populations:
      - name: {name_a}
        size: {node_a_size}
        type: biophysical
        morphologies_asc: dummy
        morphologies_swc:  {morph_path}
        biophysical_neuron_models_dir: dummy
      - name: {name_b}
        size: {node_b_size}
        type: biophysical
        morphologies_asc: dummy
        morphologies_swc: {morph_path}
        biophysical_neuron_models_dir: dummy
      - name: {name_c}
        size: 42
        type: not_biophysical

simulations:
  globals:
    output_dir: "reporting"
    tstart: {tstart}
    tstop: {tend}
    dt: {dt}
    spikes_file: "spikes.h5"
    spikes_sort_order: "by_time"
    spikes_count: {spikes_count}
    random_seed: 0

  reports:
    - name: "soma_report"
      cells: "node_set1"
      variable_name: "current_soma"
      sections: "soma"
      type: "compartment"
    - name: "compartment_report"
      cells: "node_set2"
      variable_name: "current_compart"
      sections: "all"
      type: "compartment"
"""
    with tmp_file(content, cleanup=True) as (dirpath, setup_file):
        shutil.copytree(os.path.join(TEST_DATA_DIR, morph_path), os.path.join(dirpath, morph_path))
        create_node(dirpath, name_a, node_a_size)
        create_node(dirpath, name_b, node_b_size)
        tested.create(setup_file, dirpath, dirpath, SEED)

        frame_count = int((tend - tstart)/dt)

        def check_soma_report(group, nb_frames, nb_nodes):
            assert group["data"].shape == (nb_frames, nb_nodes)
            assert set(group["mapping"]) == {"node_ids", "index_pointers", "element_ids", "time"}
            assert group["mapping/time"][:].tolist() == [tstart, tend, dt]
            npt.assert_equal(group["mapping/node_ids"][:], np.arange(nb_nodes))
            npt.assert_equal(group["mapping/element_ids"][:], np.zeros(nb_nodes))

        soma_path = os.path.join(dirpath, "reporting/soma_report.h5")
        with h5py.File(soma_path) as h5:
            check_soma_report(h5["report/nodeA"], frame_count, node_a_size)
            check_soma_report(h5["report/nodeB"], frame_count, node_b_size)

        def check_compartment_report(group, nb_frames, nb_nodes, nb_compartments):
            assert group["data"].shape == (nb_frames, sum(nb_compartments)*3)  # forcing randint to 3 in mock
            assert set(group["mapping"]) == {"node_ids", "index_pointers", "element_ids", "time"}
            assert group["mapping/time"][:].tolist() == [tstart, tend, dt]
            npt.assert_equal(group["mapping/node_ids"][:], np.arange(nb_nodes))
            element_ids = []
            for count in nb_compartments:
                # each section divided in 3 compartments --> [0, 0, 0, 1, 1, 1, 2, 2, 2, ...]
                element_ids.append(np.repeat(np.arange(count), 3))
            npt.assert_equal(group["mapping/element_ids"][:], np.concatenate(element_ids))

        def get_compartments_counts(pop_name):
            nb_compartments = []
            with h5py.File(os.path.join(dirpath, "nodes.h5")) as node_h5:
                morph_names = get_from_library(node_h5[f'nodes/{pop_name}/0'], 'morphology')
                morph_files = [os.path.join(dirpath, morph_path, morph_name + ".swc") for morph_name in morph_names]
                for morph_file in morph_files:
                    nb_compartments.append(len(morphio.Morphology(morph_file).sections))
            return nb_compartments

        compartments_counts_a = get_compartments_counts("nodeA")
        compartments_counts_b = get_compartments_counts("nodeB")
        compartment_path = os.path.join(dirpath, "reporting/compartment_report.h5")
        with h5py.File(compartment_path) as h5:
            check_compartment_report(h5["report/nodeA"], frame_count, node_a_size, compartments_counts_a)
            check_compartment_report(h5["report/nodeB"], frame_count, node_b_size, compartments_counts_b)
