from contextlib import contextmanager
from pathlib import Path
import os
import shutil
import tempfile
import uuid

import h5py
import numpy as np
from morphio import PointLevel, SectionType
from morphio.mut import Morphology


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


def create_simple_morph(directory, morph_name="test_morph.swc"):
    def _create_pointlevel(points, has_perimeters=False):
        if has_perimeters:
            return PointLevel(points, [1, 1, 1], [2 * np.pi, 2 * np.pi, 2 * np.pi])
        return PointLevel(points, [1, 1, 1])

    morpho = Morphology()
    morpho.soma.points = [[0, 0, 0]]
    morpho.soma.diameters = [0.5]
    add_perimeters = Path(morph_name).suffix == ".h5"
    section = morpho.append_root_section(
        _create_pointlevel([[10, 0, 0], [20, 0, 0], [30, 0, 0]], add_perimeters),
        SectionType.axon)  # (optional) perimeter of each point

    section.append_section(_create_pointlevel([[30, 0, 0], [40, 0, 0], [50, 0, 0]], add_perimeters))
    section.append_section(_create_pointlevel([[30, 0, 0], [35, 0, 0], [45, 0, 0]], add_perimeters))

    section = morpho.append_root_section(
        _create_pointlevel([[0, 10, 0], [0, 20, 0], [0, 30, 0]], add_perimeters),
        SectionType.basal_dendrite)  # (optional) perimeter of each point

    section.append_section(_create_pointlevel([[0, 30, 0], [0, 40, 0], [0, 50, 0]], add_perimeters))
    section.append_section(_create_pointlevel([[0, 30, 0], [0, 40, 0], [0, 50, 0]], add_perimeters))
    filepath = Path(directory, morph_name)
    morpho.write(filepath)
    return filepath


def create_node(dirpath, pop_name, pop_size, morph_name="test_morph"):
    filepath = Path(dirpath, "nodes.h5")
    option = "r+" if Path(filepath).exists() else "w"
    with h5py.File(filepath, option) as h5:
        pop_group = h5.create_group(f"nodes/{pop_name}")
        pop_group.create_dataset("node_type_id", data=[-1] * pop_size)
        prop = pop_group.create_group("0")
        string_dtype = h5py.special_dtype(vlen=str)
        prop.create_dataset('morphology', shape=(pop_size,), dtype=string_dtype)
        prop["morphology"][:] = np.full(pop_size, fill_value=morph_name)
        prop.create_dataset('x', data=np.full(pop_size, fill_value=10.), dtype=np.float32)
        prop.create_dataset('y', data=np.full(pop_size, fill_value=0.), dtype=np.float32)
        prop.create_dataset('z', data=np.full(pop_size, fill_value=0.), dtype=np.float32)
        prop.create_dataset('orientation_w', data=np.full(pop_size, fill_value=0), dtype=np.float32)
        prop.create_dataset('orientation_x', data=np.full(pop_size, fill_value=0), dtype=np.float32)
        prop.create_dataset('orientation_y', data=np.full(pop_size, fill_value=1), dtype=np.float32)
        prop.create_dataset('orientation_z', data=np.full(pop_size, fill_value=0), dtype=np.float32)
