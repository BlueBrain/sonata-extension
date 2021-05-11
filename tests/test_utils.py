import sonata_generator.utils as utils
import yaml

test_yaml = '''
nodes:
  - filepath: nodes.h5
    populations:
      - name: CircuitA
        type: biophysical
        size: 2
        morphologies_asc: CircuitA/morphologies/asc
        morphologies_swc: CircuitA/morphologies/swc
        biophysical_neuron_models_dir: CircuitA/hoc
      - name: VirtualPopA
        type: virtual
        size: 2

edges:
  - filepath: edges.h5
    populations:
      - source: CircuitA
        target: CircuitA
        type: chemical
        size: 4
  - filepath: projections.h5
    populations:
      - source: VirtualPopA
        target: CircuitA
        type: chemical
        size: 4
'''


def test_get_node_population_config():
    pop_conf = yaml.full_load(test_yaml)
    cfg = utils.get_node_population_config('VirtualPopA', pop_conf)
    assert (cfg['type'] == 'virtual')
    cfg = utils.get_node_population_config('CircuitA', pop_conf)
    assert (cfg['type'] == 'biophysical')
