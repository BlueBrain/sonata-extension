import os
import tempfile

import h5py
import numpy as np
import pytest
import sonata_generator.generators as generators
import sonata_generator.writer as writer

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, "data")
np.random.seed(1)

properties_config = {
    "propInt": {
        "type": "int",
        "values": [1, 9]
    },
    "propFloat": {
        "type": "float",
        "values": [1.0, 9.0]
    },
    "propText": {
        "type": "text",
        "values": ["A", "B", "C"]
    },
    "propEnum": {
        "type": "enum",
        "values": ["A", "B", "C"]
    },
    "propDerived": {
        "type": "float",
        "values": "derived"
    },
    "propMorph": {
        "type": "text",
        "values": "morphology"
    }
}

properties_config_no_derived = {
    "propInt": {
        "type": "int",
        "values": [1, 9]
    },
    "propFloat": {
        "type": "float",
        "values": [1.0, 9.0]
    },
    "propText": {
        "type": "text",
        "values": ["A", "B", "C"]
    },
    "propEnum": {
        "type": "enum",
        "values": ["A", "B", "C"]
    },
    "propMorph": {
        "type": "text",
        "values": "morphology"
    }
}
population_config = {"size": 2, "morphologies_swc": "morphologies"}


def test_generate_properties_dataset():

    ret = generators.generate_properties_dataset(properties_config,
                                                 population_config,
                                                 TEST_DATA_DIR)
    assert (ret['propInt'].shape == (2, ))
    assert (ret['propInt'].dtype == np.dtype('int64'))
    assert (np.all(ret['propInt'] < 10) and np.all(ret['propInt'] > 0))

    assert (ret['propFloat'].shape == (2, ))
    assert (ret['propFloat'].dtype == np.dtype('float64'))
    assert (np.all(ret['propFloat'] < 10) and np.all(ret['propFloat'] > 0))

    assert (ret['propText'].shape == (2, ))
    assert (ret['propText'].dtype == np.dtype('<U1'))
    assert (np.all(np.isin(ret['propText'], ["A", "B", "C"])))

    assert (ret['propEnum'].shape == (2, ))
    assert (ret['propEnum'].dtype == np.dtype('<U1'))
    assert (np.all(np.isin(ret['propEnum'], ["A", "B", "C"])))

    assert (ret.get('propDerived', None) == None)

    assert (ret['propMorph'].shape == (2, ))
    assert (ret['propMorph'].dtype == np.dtype('<U37'))
    assert (np.all(
        np.isin(ret['propMorph'], [
            'sm100330b1-2_idB', 'vd130423_idC',
            'C270106C_-_Scale_x1.000_y1.050_z1.000'
        ])))


def test_write_properties_datasets():

    ret = generators.generate_properties_dataset(properties_config_no_derived,
                                                 population_config,
                                                 TEST_DATA_DIR)
    temp_dir = tempfile.mkdtemp()
    with h5py.File(os.path.join(temp_dir, "test_node.h5"), 'w') as h5file:
        group = h5file.create_group('0')
        writer.write_properties_datasets(group, properties_config_no_derived,
                                         ret)
        assert (len(group.get('@library').keys()) == 1)
        assert (len(group.items()) == 6)
        assert (group.get('propInt').dtype == np.dtype('int64'))
        assert (group.get('propFloat').dtype == np.dtype('float64'))
        assert (group.get('propEnum').dtype == np.dtype('uint32'))
        assert (group.get('propMorph').dtype == np.dtype('O'))
        assert (group.get('@library').get('propEnum').dtype == np.dtype('O'))
        assert (group.get('propText').dtype == np.dtype('O'))
        for prop in [
                'propInt', 'propFloat', 'propEnum', 'propMorph', 'propText'
        ]:
            assert (group.get(prop).shape == (2, ))
