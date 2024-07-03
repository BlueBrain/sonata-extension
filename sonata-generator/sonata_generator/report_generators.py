# SPDX-License-Identifier: Apache-2.0
import logging

import os
import json

import h5py
import numpy as np
import yaml

from sonata_generator.utils import load_morphology, collect_node_populations


L = logging.getLogger("Reports")


def create_config_file(simulation_config_file, output_dir):
    """Create a simulation SONATA configuration file based on the simulation_config."""
    config = {'version': 1,
              'manifest': {"$OUTPUT_DIR": "./" + simulation_config_file["globals"]["output_dir"],
                           "$INPUT_DIR": "./"
                           },
              'run': {
                  'random_seed': simulation_config_file["globals"]["random_seed"],
                  'tstart': simulation_config_file["globals"]["tstart"],
                  'tstop': simulation_config_file["globals"]["tstop"],
                  'dt': simulation_config_file["globals"]["dt"],
              },
              'output': {
                  'output_dir': '$OUTPUT_DIR',
                  'spikes_file': simulation_config_file["globals"]["spikes_file"],
                  'spikes_sort_order': simulation_config_file["globals"]["spikes_sort_order"]
              }
              }

    reports = {}
    for report in simulation_config_file.get('reports', []):
        report_name = report['name']
        sub_config = {
            'cells': report['cells'],
            'variable_name': report['variable_name'],
            'sections': report['sections'],
            'type': report['type'],
            'start_time': simulation_config_file["globals"]["tstart"],
            'end_time': simulation_config_file["globals"]["tstop"],
            'dt': simulation_config_file["globals"]["dt"],
        }
        reports[report_name] = sub_config

    config['reports'] = reports
    with open(os.path.join(output_dir, 'simulation_sonata.json'), 'w') as f:
        json.dump(config, f, indent=4)
    return config


def spike_generator(spike_count, pop_size, tstart, tstop, dt):
    """Simple spike generator.

    Args:
        spike_count(int): number of spikes per populations.
        pop_size(int): size of the node population.
        tstart (float): starting time for the simulation.
        tstop (float): ending time for the simulation.
        dt (float): time step for the simulation.

    Returns:
         zip of the timestamps and node ids.

    Notes:
        The algorithm is naive and does not scale. It is meant for small dataset only.
    """
    step_count = int((tstop - tstart) / dt)
    if spike_count > step_count * pop_size:
        raise RuntimeError("Impossible to populate the report too many spikes: spike_count >= step_count * pop_size.")
    available_values = dict()
    all_times = np.arange(tstart, tstop + dt, dt)
    for time in all_times:
        values = np.arange(pop_size)
        np.random.shuffle(values)
        available_values[time] = list(values)

    times = []
    nodes = []
    for _ in range(spike_count):
        time = np.random.choice(list(available_values.keys()))
        node = available_values[time].pop()
        if len(available_values[time]) == 0:
            available_values.pop(time)
        times.append(time)
        nodes.append(node)
    return zip(*sorted(zip(times, nodes)))


def create_spikes_report(usecase_config, components_path, output_dir):
    """Create the spike report for all biophysical node populations.

    The report is created in such a way the node ids should not be reported twice during the same timestamp.

    Args:
        usecase_config(dict): the usecase config parsed by yaml lib.
        components_path(str): the component directory.
        output_dir(str): the output directory.
    """
    L.info("Starts the spike report creation.")
    config = usecase_config["simulations"]["globals"]
    tstart = config["tstart"]
    tstop = config["tstop"]
    dt = config["dt"]
    spike_count = config["spikes_count"]
    reporting_dir = os.path.join(output_dir, config["output_dir"])
    filepath = os.path.join(reporting_dir, config["spikes_file"])
    node_populations = collect_node_populations(usecase_config, output_dir,
                                                components_path=components_path,
                                                filter_types="biophysical")

    sorting_type = h5py.enum_dtype({"none": 0, "by_id": 1, "by_time": 2})

    with h5py.File(filepath, 'w') as h5f:
        h5f.create_group('spikes')
        for node_population in node_populations:
            pop_spikes = h5f.create_group('/spikes/' + node_population.name)
            pop_spikes.attrs.create('sorting', data=2, dtype=sorting_type)
            timestamps, node_ids = spike_generator(spike_count, node_population.size, tstart, tstop, dt)
            pop_spikes.create_dataset('timestamps', data=timestamps, dtype=np.double)
            pop_spikes.create_dataset('node_ids', data=node_ids, dtype=np.uint64)


def create_compartment_report(usecase_config, components_path, output_dir):
    """Compartment report creation for biophysical node populations.

    It can be used for soma or compartment reports. Both are the same except the soma report only have a single
    compartment per node.

    A random number between 3 and 8 is used as the number of compartments per sections. This random number is renewed
    at every compartment of each node.
    The values for each frames are taken at random and are between 0 and 1.

    Args:
        usecase_config(dict): the usecase config parsed by yaml lib.
        components_path(str): the component directory.
        output_dir(str): the output directory.
    """
    L.info("Starts the compartment report creation.")
    config = usecase_config["simulations"]["globals"]
    tstart = config["tstart"]
    tstop = config["tstop"]
    dt = config["dt"]
    reporting_dir = os.path.join(output_dir, config["output_dir"])
    node_populations = collect_node_populations(usecase_config, output_dir,
                                                components_path=components_path,
                                                filter_types="biophysical")

    report_configs = usecase_config["simulations"]["reports"]
    string_dtype = h5py.special_dtype(vlen=str)

    for report_config in report_configs:
        filepath = os.path.join(reporting_dir, report_config["name"] + ".h5")
        sections = report_config["sections"]
        times = (tstart, tstop, dt)
        with h5py.File(filepath, 'w') as h5f:
            h5f.create_group('report')

            for node_population in node_populations:
                node_ids = np.arange(node_population.size)
                index_pointers = []
                element_ids = []
                total_size = 0
                frame_count = int((tstop - tstart) / dt)
                # don t use the nodesets yet so I am using all the node_ids.
                for node_id in node_ids:
                    index_pointers.append(total_size)
                    if sections == "soma":
                        total_size += 1
                        element_ids.append(0)
                    else:
                        morph = load_morphology(node_population, node_id)
                        for i in range(len(morph.sections)):
                            nb_compartment = np.random.randint(3, 8)
                            total_size += nb_compartment
                            element_ids.extend([i for _ in range(nb_compartment)])

                index_pointers.append(total_size)  # need to add the last one at the end
                full_data = np.random.random((frame_count, total_size)) * 90 - 80  # uniform between -80 and 10

                pop_report = h5f.create_group('report/' + node_population.name)
                data = pop_report.create_dataset('data', data=full_data, dtype=np.float32)
                data.attrs.create('units', data="mV", dtype=string_dtype)

                mapping = h5f.create_group('report/' + node_population.name + '/mapping')
                nodes = mapping.create_dataset('node_ids', data=node_ids, dtype=np.uint64)
                nodes.attrs.create('sorted', data=True, dtype=np.uint8)

                mapping.create_dataset('index_pointers', data=index_pointers, dtype=np.uint64)
                mapping.create_dataset('element_ids', data=element_ids, dtype=np.uint32)

                dtimes = mapping.create_dataset('time', data=times, dtype=np.double)
                dtimes.attrs.create('units', data="ms", dtype=string_dtype)


def create(usecase_config, components_path, output_dir, seed=0):
    """Create the report files using the usecase_config."""
    np.random.seed(seed)
    usecase_config = yaml.full_load(open(usecase_config))
    simulation_config = usecase_config.get("simulations", None)
    if simulation_config is None:
        return
    create_config_file(simulation_config, output_dir)
    report_output_dir = os.path.join(output_dir, simulation_config["globals"]["output_dir"])
    if not os.path.exists(report_output_dir):
        os.makedirs(report_output_dir)
    create_spikes_report(usecase_config, components_path, output_dir)

    if "reports" in simulation_config:
        create_compartment_report(usecase_config, components_path, output_dir)
