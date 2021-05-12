import os
import json
import click
import yaml
import h5py
import numpy as np
from collections import namedtuple


def create_config_file(simulation_config_file, output_dir):
    """Create a simulation SONATA configuration file based on the simulation_config"""
    config = {'version': 1,
              'manifest': {"$OUTPUT_DIR": "./" + simulation_config_file["globals"]["output_dir"],
                           "$INPUT_DIR": "./"
                           },
              'run': {
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
        }
        reports[report_name] = sub_config

    config['reports'] = reports
    with open(os.path.join(output_dir, 'simulation_sonata.json'), 'w') as f:
        json.dump(config, f, indent=4)
    return config


NodePopulation = namedtuple('NodePopulation', ["name", "size"])


def create_spikes_report(usecase_config, output_dir):
    config = usecase_config["simulations"]["globals"]
    tstart = config["tstart"]
    tstop = config["tstop"]
    dt = config["dt"]
    spikes_count = config["spikes_count"]
    reporting_dir = os.path.join(output_dir, config["output_dir"])
    filepath = os.path.join(reporting_dir, config["spikes_file"])

    node_populations = []
    for files in usecase_config["nodes"]:
        for population in files['populations']:
            node_populations.append(NodePopulation(population["name"], population["size"]))

    sorting_type = h5py.enum_dtype({"none": 0, "by_id": 1, "by_time": 2})

    with h5py.File(filepath, 'w') as h5f:
        h5f.create_group('spikes')
        for node_population in node_populations:
            timestamps_base = np.random.choice(np.arange(tstart, tstop + dt, dt), spikes_count)
            node_ids_base = np.random.choice(node_population.size, spikes_count)
            pop_spikes = h5f.create_group('/spikes/' + node_population.name)
            pop_spikes.attrs.create('sorting', data=2, dtype=sorting_type)
            timestamps, node_ids = zip(*sorted(zip(timestamps_base, node_ids_base)))
            pop_spikes.create_dataset('timestamps', data=timestamps, dtype=np.double)
            pop_spikes.create_dataset('node_ids', data=node_ids, dtype=np.uint64)


def create(usecase_config, output_dir, verbosity="ERROR"):
    usecase_config = yaml.full_load(open(usecase_config))
    simulation_config = usecase_config.get("simulations", None)
    if simulation_config is None:
        return
    create_config_file(simulation_config, output_dir)
    report_output_dir = os.path.join(output_dir, simulation_config["globals"]["output_dir"])
    if not os.path.exists(report_output_dir):
        os.mkdir(report_output_dir)
    create_spikes_report(usecase_config, output_dir)


@click.command()
@click.argument('usecase_config', type=click.Path(file_okay=True))
@click.argument('output_dir', type=click.Path(dir_okay=True))
@click.option('-v', '--verbosity', default="ERROR")
def create_sample_data(usecase_config, output_dir, verbosity):
    create(usecase_config, output_dir, verbosity=verbosity)


if __name__ == '__main__':
    create_sample_data()
