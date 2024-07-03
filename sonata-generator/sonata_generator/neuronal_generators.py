# SPDX-License-Identifier: Apache-2.0
from cached_property import cached_property

from morphio import SectionType
import numpy as np

from sonata_generator.generators import NodeGenerator, EdgeGenerator
from sonata_generator.utils import (load_morphology, segment_lengths, get_surface_point)
from sonata_generator.exceptions import GeneratorError

NEURITE_TYPE_MAP = {SectionType.soma: 0,
                    SectionType.axon: 1,
                    SectionType.basal_dendrite: 2,
                    SectionType.apical_dendrite: 3
                    }


class BiophysicalGenerator(NodeGenerator):
    UNIFORM_DATA = ["x", "y", "z", "orientation_w", "orientation_x", "orientation_y",
                    "orientation_z", "minis", "dynamics_params/threshold_current",
                    "dynamics_params/holding_current", "dynamics_params/AIS_scaler"]

    CHOICE_DATA = ["region", "model_type", "layer", "morph_class", "etype",
                   "mtype", "synapse_class", "region", "hemisphere"]

    @property
    def _ok_types(self):
        return ["biophysical"]

    @cached_property
    def _templates(self):
        hocs = ["hoc:" + hoc.stem for hoc in self.info.biophysical_neuron_models_dir.glob("*.hoc")]
        return {"model_template": np.random.choice(hocs, size=self.info.size)}

    @cached_property
    def _morphologies(self):
        morphs = [morph.stem for morph in self.info.morphologies_swc.glob("*.swc")]
        return {"morphology": np.random.choice(morphs, size=self.info.size)}

    def create_data(self):
        super().create_data()
        self.data.update(self._templates)
        self.data.update(self._morphologies)


class VirtualGenerator(NodeGenerator):
    CHOICE_DATA = ["model_type"]

    @property
    def _ok_types(self):
        return ["virtual"]

    @cached_property
    def _templates(self):
        return {"model_template": np.full((self.info.size), "")}

    def create_data(self):
        super().create_data()
        self.data.update(self._templates)


class ChemicalGenerator(EdgeGenerator):
    UNIFORM_DATA = ["conductance", "decay_time", "depression_time", "facilitation_time", "u_syn",
                    "n_rrp_vesicles", "conductance_scale_factor",
                    "u_hill_coefficient", "syn_type_id", "delay"]

    @property
    def _ok_source_types(self):
        return ["biophysical", "virtual"]

    @property
    def _ok_target_types(self):
        return ["biophysical"]

    @property
    def _ok_types(self):
        return ["chemical"]

    @staticmethod
    def _add_synapse_properties(population, node_id, prefix):
        """Create the synapse properties for a given node id."""
        morph = load_morphology(population, node_id, transform=True, morph_type=".swc")
        if prefix == "afferent":
            filter_ = [SectionType.basal_dendrite, SectionType.apical_dendrite]
        else:
            filter_ = [SectionType.axon]
        sections = [v.id for v in morph.sections if v.type in filter_]
        section = np.random.choice(sections, 1)[0]
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
                f"{prefix}_section_type": NEURITE_TYPE_MAP[section_type],
                f"{prefix}_center_x": center_position[0],
                f"{prefix}_center_y": center_position[1],
                f"{prefix}_center_z": center_position[2],
                f"{prefix}_surface_x": surface_position[0],
                f"{prefix}_surface_y": surface_position[1],
                f"{prefix}_surface_z": surface_position[2],
                f"{prefix}_segment_offset": offset}

    def _add_synapses(self):
        if not self.topology:
            self._create_topology()

        targets = self.topology["target_node_id"]
        sources = self.topology["source_node_id"]

        for i, target in enumerate(targets):
            source = sources[i]
            if self.info.source.type == "biophysical":
                self._append_to_data(
                    self._add_synapse_properties(self.info.source, source, "efferent"))
            elif self.info.source.type == "virtual":
                self._append_to_data({"efferent_section_type": NEURITE_TYPE_MAP[SectionType.axon]})
            self._append_to_data(self._add_synapse_properties(self.info.target, target, "afferent"))

        if self.info.source.type == "biophysical":
            # no spine length from what I understood from Joni for projections
            afferent_points = np.array([self.data["afferent_center_" + coord] for coord in
                                        ['x', 'y', 'z']]).T
            efferent_points = np.array([self.data["efferent_center_" + coord] for coord in
                                        ['x', 'y', 'z']]).T
            self.data["spine_length"] = np.linalg.norm(afferent_points - efferent_points, axis=1)

    def _check_missing_properties(self):
        """Overload of the missing properties to take projection into account."""
        required_properties = list(self.property_config)
        if self.info.source.type == "virtual":
            required_properties = {prop for prop in self.property_config if
                                   prop == "efferent_section_type" or  # keep this prop
                                   (not prop.startswith("efferent") and prop != "spine_length")}
        missing_properties = set(required_properties) - set(self.data)
        if missing_properties:
            raise GeneratorError(f"Missing property {missing_properties}")

    def create_data(self):
        super().create_data()
        self._add_synapses()
