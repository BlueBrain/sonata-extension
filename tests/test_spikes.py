import os
import tempfile
import uuid

import h5py
import numpy as np
import numpy.testing as npt
import shutil
from contextlib import contextmanager

import pytest

import sonata_generator.report_generator as tested


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, "data")
np.random.seed(1)


@contextmanager
def setup_tempdir(cleanup=True):
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        if cleanup:
            shutil.rmtree(temp_dir)


@contextmanager
def tmp_file(content, cleanup=True):
    with setup_tempdir(cleanup=cleanup) as dirpath:
        _, filepath = tempfile.mkstemp(suffix=".yaml", prefix=str(uuid.uuid4()), dir=dirpath)
        with open(filepath, "r+") as fd:
            fd.write(content)
        try:
            yield dirpath, filepath
        finally:
            if cleanup:
                os.remove(filepath)


def test_spike_generator():
    spike_count, pop_size, tstart, tstop, dt = 15, 3, 0., 1., 0.1
    times, nodes = tested.spike_generator(spike_count, pop_size, tstart, tstop, dt)
    assert len(times) == len(nodes) == spike_count

    spike_count = 30
    times, nodes = tested.spike_generator(spike_count, pop_size, tstart, tstop, dt)
    assert len(times) == len(nodes) == spike_count

    with pytest.raises(RuntimeError):
        spike_count_fail = 31
        # cannot populate 31 spikes with population of 3 nodes and only 10 possible timesteps
        tested.spike_generator(spike_count_fail, pop_size, tstart, tstop, dt)


def test_create_spikes_report():
    dt = 0.1
    spikes_count = 15
    name_a = "nodeA"
    name_b = "nodeB"
    node_a_size = 2
    node_b_size = 25
    content = f"""
nodes:
  - filepath: nodes.h5
    populations:
      - name: {name_a}
        size: 2
      - name: {name_b}
        size: 3

simulations:
  globals:
    output_dir: "reporting"
    tstart: 0
    tstop: 1.0
    dt: {dt}
    spikes_file: "spikes.h5"
    spikes_sort_order: "time"
    spikes_count: {spikes_count}
"""
    with tmp_file(content, cleanup=True) as (dirpath, setup_file):
        tested.create(setup_file, dirpath, "")
        with h5py.File(os.path.join(dirpath, "reporting", "spikes.h5")) as h5:
            assert set(pop for pop in h5["spikes"]) == {name_a, name_b}
            time_a = h5["spikes/nodeA/timestamps"][:]
            time_b = h5["spikes/nodeB/timestamps"][:]
            node_a = h5["spikes/nodeA/node_ids"][:]
            node_b = h5["spikes/nodeB/node_ids"][:]
            assert len(time_a) == spikes_count
            assert len(time_b) == spikes_count
            assert len(node_a) == spikes_count
            assert len(node_b) == spikes_count
            times = time_a / dt
            npt.assert_allclose(times, times.astype(np.int32))
            times = time_b / dt
            npt.assert_allclose(times, times.astype(np.int32))
            assert np.all(np.in1d(node_a, np.arange(node_a_size)))
            assert np.all(np.in1d(node_b, np.arange(node_b_size)))
