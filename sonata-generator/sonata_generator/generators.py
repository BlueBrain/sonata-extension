# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import h5py
import libsonata
import numpy as np

from sonata_generator.exceptions import GeneratorError
LIBRARY = "@library"

TYPE_DISPATCH = {
    "float": np.float32,
    "int": np.int64,
    "uint32": np.uint32,
    "uint64": np.uint64,
    "text": h5py.string_dtype(encoding='utf-8'),
}


class Generator:
    UNIFORM_DATA = []
    CHOICE_DATA = []

    def __init__(self, info, property_config):
        self.info = info
        self.data = {}
        self._check_type()
        self.property_config = property_config[self.info.type]

    @property
    def _ok_types(self):
        """List of accepted types for this generator."""
        raise NotImplementedError

    @property
    def _population_type(self):
        """Can be nodes or edges."""
        raise NotImplementedError

    def _check_type(self):
        """Check if the types are correct for this generator."""
        if self.info.type not in self._ok_types:
            raise GeneratorError(f"Wrong generator {self.__class__} for {self.info.type} config.")

    def _create_uniform_data(self):
        for property_name in self.UNIFORM_DATA:
            default = self.property_config[property_name]["values"]
            type_ = self.property_config[property_name]["type"]
            if len(default) > 2:
                raise GeneratorError(f"Uniform data should have only two values. Found "
                                     f": '{default}' for '{property_name}' in '{self.info.type}'")
            if type_ == "float":
                values = np.random.uniform(low=default[0], high=default[1], size=self.info.size)
            elif type_ in ("int", "uint32"):
                values = np.random.choice(np.arange(int(default[0]), int(default[1])),
                                          size=self.info.size)
            else:
                raise GeneratorError(f"Cannot create a uniform distribution for '{type_}' "
                                     f"variables from '{self.info.type}'.")
            self.data[property_name] = values

    def _create_choice_data(self):
        for property_name in self.CHOICE_DATA:
            default = self.property_config[property_name]["values"]
            values = np.random.choice(default, size=self.info.size)
            self.data[property_name] = values

    def _append_to_data(self, added):
        for key, value in added.items():
            if key not in self.data:
                self.data[key] = [value]
            else:
                self.data[key].append(value)

    def create_data(self):
        self._create_uniform_data()
        self._create_choice_data()

    def _check_missing_properties(self):
        missing_properties = set(self.property_config) - set(self.data)
        if missing_properties:
            raise GeneratorError(f"Missing property {missing_properties}")

    def save(self):
        self._check_missing_properties()
        mod = "w"
        if Path(self.info.filepath).exists():
            mod = "r+"

        with h5py.File(self.info.filepath, mod) as h5:
            population_group = h5.create_group(f"/{self._population_type}/{self.info.name}")
            population_group.create_dataset(f"{self._population_type[:-1]}_type_id",
                                            data=np.full(self.info.size, fill_value=-1),
                                            dtype=np.int64)
            properties_group = population_group.create_group("0")
            for prop_name, prop_data in self.data.items():
                type_ = self.property_config[prop_name]["type"]
                if type_ == "text" and self._population_type == "nodes":
                    if LIBRARY not in properties_group:
                        library = properties_group.create_group(LIBRARY)
                    else:
                        library = properties_group[LIBRARY]
                    lib_data = np.sort(np.unique(prop_data)).astype(TYPE_DISPATCH[type_])
                    library.create_dataset(prop_name, data=lib_data)

                    prop_data = np.searchsorted(lib_data, prop_data).astype(np.uint32)
                else:
                    prop_data = np.asarray(prop_data).astype(TYPE_DISPATCH[type_])
                properties_group.create_dataset(prop_name, data=prop_data)


class NodeGenerator(Generator):
    @property
    def _ok_types(self):
        return []

    @property
    def _population_type(self):
        return "nodes"


class EdgeGenerator(Generator):
    def __init__(self, info, property_config):
        super().__init__(info, property_config)
        self._check_source_target_types()
        self.topology = {}

    @property
    def _ok_types(self):
        return []

    @property
    def _ok_source_types(self):
        return []

    @property
    def _ok_target_types(self):
        return []

    def _check_source_target_types(self):
        if self.info.source.type not in self._ok_source_types:
            raise GeneratorError(f"Bad input type source {self.info.source} "
                                 f"for the edge data {self.info.name}")
        if self.info.target.type not in self._ok_target_types:
            raise GeneratorError(f"Bad input type target {self.info.target} "
                                 f"for the edge data {self.info.name}")

    @property
    def _population_type(self):
        return "edges"

    def _create_topology(self):
        size = self.info.size
        if self.info.target.name != self.info.source.name:
            self.topology["target_node_id"] = np.random.choice(self.info.target.size, size).astype(
                np.int64)
            self.topology["source_node_id"] = np.random.choice(self.info.source.size, size).astype(
                np.int64)
        else:
            if self.info.target.size == 1:
                raise GeneratorError(f"Trying to create a edge in a graph with a single node. "
                                     f"Please increase the number of nodes in "
                                     f"the {self.info.target.name} population.")
            targets = np.random.choice(self.info.target.size, size)
            unique = np.unique(targets)
            if len(unique) == 1:
                values = np.arange(self.info.target.size)
                targets[0] = np.random.choice(values[values != unique])
            self.topology["target_node_id"] = targets.astype(np.int64)
            sources = []
            for target in targets:
                sources.append(np.random.choice(targets[targets != target]))
            self.topology["source_node_id"] = np.array(sources, dtype=np.int64)

    def _write_topology(self):
        with h5py.File(self.info.filepath, 'r+') as h5:
            pop_group = h5[f"/{self._population_type}/{self.info.name}"]
            source = pop_group.create_dataset("source_node_id",
                                              data=self.topology["source_node_id"], dtype="u8")
            source.attrs['node_population'] = self.info.source.name
            target = pop_group.create_dataset("target_node_id",
                                              data=self.topology["target_node_id"], dtype="u8")
            target.attrs['node_population'] = self.info.target.name

    def _write_indexing(self):
        libsonata.EdgePopulation.write_indices(
            str(self.info.filepath),
            self.info.name,
            self.info.source.size,
            self.info.target.size,
        )

    def create_data(self):
        super().create_data()
        self._create_topology()

    def save(self):
        super().save()
        self._write_topology()
        self._write_indexing()
