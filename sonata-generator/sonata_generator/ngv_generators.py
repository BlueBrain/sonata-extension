# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from cached_property import cached_property

import h5py
from morphio import SectionType
import numpy as np
from vascpy import SectionVasculature

from sonata_generator.generators import NodeGenerator, EdgeGenerator
from sonata_generator.utils import load_morphology, get_surface_point, segment_lengths
from sonata_generator.exceptions import GeneratorError

ASTROCYTE_NEURITE_TYPE_MAP = {SectionType.soma: 0,
                              SectionType.axon: 1,
                              SectionType.basal_dendrite: 2,
                              SectionType.apical_dendrite: 3
                              }


class VasculatureGenerator(NodeGenerator):

    def __init__(self, info, property_config):
        super().__init__(info, property_config)
        input_path = info.morphologies_h5 / "vasculature_morphology.h5"
        self.vasc = SectionVasculature.load(input_path).as_point_graph()

    @property
    def _ok_types(self):
        return ["vasculature"]

    def create_data(self):
        """Create the data is not needed here for the vasculature.

        Everything is done in the loading and the save.
        """

    def save(self):
        """Full override of the save.

        Don t use the normal one and use vascpy instead.
        """
        self.vasc.save_sonata(self.info.filepath)
        with h5py.File(self.info.filepath, "r+") as h5:
            h5[f"nodes/{self.info.name}"] = h5["nodes/vasculature"]
            del h5["nodes/vasculature"]


class AstrocyteGenerator(NodeGenerator):
    UNIFORM_DATA = ["x", "y", "z", "radius"]

    # put the orientations in choice because it should be unitary matrix at the end. So considering
    # the current node config it forces the w = 1, and x,y,z = 0.
    CHOICE_DATA = ["region", "model_type", "mtype", "orientation_w", "orientation_x",
                   "orientation_y", "orientation_z"]

    @property
    def _ok_types(self):
        return ["astrocyte"]

    @cached_property
    def _templates(self):
        hocs = ["hoc:" + hoc.stem for hoc in self.info.biophysical_neuron_models_dir.glob("*.hoc")]
        return {"model_template": np.random.choice(hocs, size=self.info.size)}

    @cached_property
    def _morphologies(self):
        morphs = [morph.stem for morph in self.info.morphologies_h5.glob("*.h5")]
        return {"morphology": np.random.choice(morphs, size=self.info.size)}

    def _parse_cube(self):
        cylinder = self.info.morphologies_h5 / 'cube.obj'
        points = []
        triangles = []
        with open(cylinder) as fd:
            for line in fd:
                split = line.split(" ")
                if split[0] == "v":
                    points.append(split[1:])
                if split[0] == "f":
                    triangles.append(split[1:])
        return np.array(points, dtype=np.float32), np.array(triangles, dtype=np.int32)

    def _create_microdomains(self):
        """Creates the microdomains.

        Using a cube.obj file and swap the min max for each coordinates to create a rectangular
        mesh that includes the astrocyte morphology. The neighbors are set randomly because it
        is quite hard to have something ok due to the random positions of the astrocytes.
        """
        points = []
        triangle_data = []
        neighbors = []
        offsets = np.zeros((self.info.size, 3))

        ipoints, itriangles = self._parse_cube()
        for i in range(self.info.size):
            cpoints = ipoints.copy()

            if i != 0:
                offsets[i, :] = [len(cpoints) + offsets[i - 1, 0],
                                 len(itriangles) + offsets[i - 1, 1],
                                 self.info.size + offsets[i - 1, 2]]
            else:
                offsets[i, :] = [0, 0, 0]

            ctriangle_data = itriangles.copy() + offsets[i, 1]
            ctriangle_data = np.column_stack([np.arange(len(ctriangle_data)) + offsets[i, 1], ctriangle_data])

            morph = load_morphology(self.info, i, transform=True, morph_type=".h5")
            xmax = morph.points[:, 0].max()
            xmin = morph.points[:, 0].min()
            cpoints[cpoints[:, 0] == 1, 0] = xmax
            cpoints[cpoints[:, 0] == -1, 0] = xmin

            ymax = morph.points[:, 1].max()
            ymin = morph.points[:, 1].min()
            cpoints[cpoints[:, 1] == 1, 1] = ymax
            cpoints[cpoints[:, 1] == -1, 1] = ymin

            zmax = morph.points[:, 2].max()
            zmin = morph.points[:, 2].min()
            cpoints[cpoints[:, 2] == 1, 2] = zmax
            cpoints[cpoints[:, 2] == -1, 2] = zmin

            points.extend(cpoints)
            if len(triangle_data) == 0:
                triangle_data = ctriangle_data
            else:
                triangle_data = np.concatenate([triangle_data, ctriangle_data])

            neighbors.extend(np.random.randint(-1, self.info.size, size=len(cpoints)))

        dirpath = Path(self.info.filepath.parent / "microdomains")
        if not dirpath.exists():
            dirpath.mkdir()

        output_path = self.info.filepath.parent / "microdomains" / "microdomains.h5"
        with h5py.File(output_path, "w") as h5:
            data_group = h5.create_group("data")
            data_group.create_dataset("points", data=np.array(points).astype(np.float32))
            data_group.create_dataset("triangle_data", data=np.array(triangle_data).astype(np.int64))
            data_group.create_dataset("neighbors", data=np.array(neighbors).astype(np.int64))
            h5.create_dataset("offsets", data=np.array(offsets).astype(np.int64))

    def create_data(self):
        super().create_data()
        self.data.update(self._templates)
        self.data.update(self._morphologies)

    def save(self):
        super().save()
        self._create_microdomains()


class GlialGlialGenerator(EdgeGenerator):
    @property
    def _ok_source_types(self):
        return ["astrocyte"]

    @property
    def _ok_target_types(self):
        return ["astrocyte"]

    @property
    def _ok_types(self):
        return ["electrical", "glialglial"]

    @staticmethod
    def _add_touch_properties(population, node_id, prefix):
        """Create the touch properties for a given node id."""
        morph = load_morphology(population, node_id, transform=True, morph_type=".h5")
        section = np.random.randint(0, len(morph.sections))
        morph_section = morph.sections[section]
        segment = np.random.randint(0, len(morph_section.points) - 1)
        section_type = morph_section.type
        diameter = morph_section.diameters[segment]
        point_start = morph_section.points[segment]
        point_end = morph_section.points[segment + 1]
        vect = point_end - point_start
        ratio = np.random.random()
        offset = np.linalg.norm(vect) * ratio
        center_position = point_start + vect * ratio
        surface_position = get_surface_point(vect, center_position, diameter)

        section_lengths = segment_lengths(morph_section)
        pos = (section_lengths[:segment].sum() + offset) / section_lengths.sum()
        return {f"{prefix}_section_id": section,
                f"{prefix}_segment_id": segment,
                f"{prefix}_section_pos": pos,
                f"{prefix}_section_type": ASTROCYTE_NEURITE_TYPE_MAP[section_type],
                f"{prefix}_center_x": center_position[0],
                f"{prefix}_center_y": center_position[1],
                f"{prefix}_center_z": center_position[2],
                f"{prefix}_surface_x": surface_position[0],
                f"{prefix}_surface_y": surface_position[1],
                f"{prefix}_surface_z": surface_position[2],
                f"{prefix}_segment_offset": offset}

    def _add_electrical_synapses(self):
        if not self.topology:
            self._create_topology()

        targets = self.topology["target_node_id"]
        sources = self.topology["source_node_id"]

        for i, target in enumerate(targets):
            source = sources[i]
            self._append_to_data(self._add_touch_properties(self.info.source, source, "efferent"))
            self._append_to_data(self._add_touch_properties(self.info.target, target, "afferent"))

        afferent_points = np.array([self.data["afferent_surface_" + coord] for coord in
                                    ['x', 'y', 'z']]).T
        efferent_points = np.array([self.data["efferent_surface_" + coord] for coord in
                                    ['x', 'y', 'z']]).T
        self.data["spine_length"] = np.linalg.norm(afferent_points - efferent_points, axis=1)

    def create_data(self):
        super().create_data()
        self._add_electrical_synapses()


class NeuroGlialGenerator(EdgeGenerator):
    """Neuroglial generator."""

    def __init__(self, info, property_config):
        super().__init__(info, property_config)
        self._synapse_population = None

    @property
    def _ok_source_types(self):
        return ["astrocyte"]

    @property
    def _ok_target_types(self):
        return ["biophysical"]

    @property
    def _ok_types(self):
        return ["synapse_astrocyte"]

    def _check_synapse_connections(self):
        if self._synapse_population.size < self.info.size:
            raise GeneratorError(f"You cannot connect {self.info.size} "
                                 f"to {self._synapse_population.size} synapses.")

    def connect_synapse(self, all_edges):
        for edge in all_edges:
            if self.info.edge_connection == edge.name:
                self._synapse_population = edge
                self._check_synapse_connections()
                return

    def _get_target_ids(self, synapse_ids):
        """Get the target ids from the synapse_ids."""
        with h5py.File(self._synapse_population.filepath) as h5:
            return h5[f"/edges/{self._synapse_population.name}/target_node_id"][:][synapse_ids]

    def _create_topology(self):
        """Override the topology to link the synapses and the target nodes correctly."""
        if self._synapse_population is None:
            raise GeneratorError(f"No synapses are connected to the this "
                                 f"Neuroglial ({self.info.name}) edge.")
        size = self.info.size

        self.topology["source_node_id"] = np.random.choice(self.info.source.size, size).astype(
            np.int64)
        self.topology["synapse_id"] = np.random.choice(np.arange(self._synapse_population.size),
                                                       self.info.size, replace=False)
        self.topology["target_node_id"] = self._get_target_ids(self.topology["synapse_id"])

    def _add_synapse_properties(self):
        if not self.topology:
            self._create_topology()
        self.data["synapse_id"] = self.topology["synapse_id"]
        self.data["synapse_population"] = np.full(self.info.size,
                                                  fill_value=self._synapse_population.name)

    def _write_topology(self):
        super()._write_topology()
        with h5py.File(self.info.filepath, 'r+') as h5:
            pop_group = h5[f"/{self._population_type}/{self.info.name}"]
            pop_group["0/synapse_id"].attrs["edge_population"] = self.info.edge_connection

    @staticmethod
    def _get_process_properties(population, node_id):
        """Create the end process properties for a given node id."""
        morph = load_morphology(population, node_id, transform=True, morph_type=".h5")
        x, y, z = morph.soma.center
        section = np.random.randint(0, len(morph.sections))
        morph_section = morph.sections[section]
        segment = np.random.randint(0, len(morph_section.points) - 1)
        point_start = morph_section.points[segment]
        point_end = morph_section.points[segment + 1]
        vect = point_end - point_start
        offset = np.random.uniform(0, 1) * np.linalg.norm(vect)
        section_lengths = segment_lengths(morph_section)
        pos = (section_lengths[:segment].sum() + offset) / section_lengths.sum()
        return {"astrocyte_section_id": section,
                "astrocyte_segment_id": segment,
                "astrocyte_segment_offset": offset,
                "astrocyte_section_pos": pos,
                "astrocyte_center_x": x,
                "astrocyte_center_y": y,
                "astrocyte_center_z": z,
                }

    def _add_connections_properties(self):
        if not self.topology:
            self._create_topology()
        for node_id in self.topology["source_node_id"]:
            self._append_to_data(self._get_process_properties(self.info.source, node_id))

    def create_data(self):
        super().create_data()
        self._add_synapse_properties()
        self._add_connections_properties()


class EndfootGenerator(EdgeGenerator):
    UNIFORM_DATA = ["endfoot_compartment_length",
                    "endfoot_compartment_diameter",
                    "endfoot_compartment_perimeter"]

    @property
    def _ok_source_types(self):
        return ["vasculature"]

    @property
    def _ok_target_types(self):
        return ["astrocyte"]

    @property
    def _ok_types(self):
        return ["endfoot"]

    def _get_astrocyte_properties(self, target):
        morph = load_morphology(self.info.target, target, morph_type=".h5", transform=True)
        section = np.random.randint(0, len(morph.sections))
        return {"astrocyte_section_id": section}

    def _add_endfeet(self):
        if not self.topology:
            self._create_topology()

        targets = self.topology["target_node_id"]  # vasc
        sources = self.topology["source_node_id"]  # astro

        def _get(population, property_, node_ids):
            with h5py.File(population.filepath) as h5:
                return h5[f"/nodes/{population.name}/0/{property_}"][:][node_ids]

        for target in targets:
            self._append_to_data(self._get_astrocyte_properties(target))

        endfoot_surface_x = []
        endfoot_surface_y = []
        endfoot_surface_z = []

        for source in sources:
            start_x = _get(self.info.source, "start_x", source)
            start_y = _get(self.info.source, "start_y", source)
            start_z = _get(self.info.source, "start_z", source)
            start = np.array([start_x, start_y, start_z])

            end_x = _get(self.info.source, "end_x", source)
            end_y = _get(self.info.source, "end_y", source)
            end_z = _get(self.info.source, "end_z", source)
            end = np.array([end_x, end_y, end_z])

            start_diameter = _get(self.info.source, "start_diameter", source)
            end_diameter = _get(self.info.source, "end_diameter", source)
            diameter = (start_diameter + end_diameter) * 0.5
            vect = end - start
            ratio = np.random.random()
            point = start + vect * ratio
            endfoot_surface = get_surface_point(vect, point, diameter)
            endfoot_surface_x.append(endfoot_surface[0])
            endfoot_surface_y.append(endfoot_surface[1])
            endfoot_surface_z.append(endfoot_surface[2])

        endfoot_ids = np.arange(self.info.size)
        np.random.shuffle(endfoot_ids)
        self.data["endfoot_id"] = endfoot_ids
        self.data["endfoot_surface_x"] = np.asarray(endfoot_surface_x)
        self.data["endfoot_surface_y"] = np.asarray(endfoot_surface_y)
        self.data["endfoot_surface_z"] = np.asarray(endfoot_surface_z)
        self.data["vasculature_section_id"] = _get(self.info.source, "section_id", sources)
        self.data["vasculature_segment_id"] = _get(self.info.source, "segment_id", sources)

    def _parse_half_cylinder(self):
        cylinder = self.info.source.morphologies_h5 / 'cylinder.obj'
        points = []
        triangles = []
        with open(cylinder) as fd:
            for line in fd:
                split = line.split(" ")
                if split[0] == "v":
                    points.append(split[1:])
                if split[0] == "f":
                    triangles.append(split[1:])
        return np.array(points, dtype=np.float32), np.array(triangles, dtype=np.int64)

    def _create_endfeet_file(self):
        points, triangles = self._parse_half_cylinder()
        output_path = self.info.filepath.parent / "endfeet_areas.h5"
        with h5py.File(output_path, "w") as h5:
            attributes = h5.create_group("attributes")
            attributes.create_dataset("surface_area",
                                      data=np.random.uniform(100, 1000, size=self.info.size).astype(
                                          np.float32))
            attributes.create_dataset("surface_thickness",
                                      data=np.random.uniform(0.90, 1.2, size=self.info.size).astype(
                                          np.float32))
            attributes.create_dataset("unreduced_surface_area",
                                      data=np.random.uniform(100, 10000,
                                                             size=self.info.size).astype(
                                          np.float32))

            objects_group = h5.create_group("objects")
            for endfoot_id in self.data["endfoot_id"]:
                endfoot_group = objects_group.create_group(f"endfoot_{endfoot_id}")
                shift = np.array([self.data[f"endfoot_surface_{coord}"][endfoot_id]
                                  for coord in ["x", "y", "z"]]).astype(np.float32)
                endfoot_points = points + shift
                endfoot_group.create_dataset("points", data=endfoot_points.astype(np.float32))
                endfoot_group.create_dataset("triangles", data=triangles)

    def create_data(self):
        super().create_data()
        self._add_endfeet()
        self._create_endfeet_file()
