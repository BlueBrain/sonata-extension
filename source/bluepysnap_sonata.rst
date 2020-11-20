.. _bluepysnap_sonata:
.. |snap| replace:: ``Blue Brain SNAP``
.. |bbp| replace:: `BBP`
.. include:: <isonum.txt>

Blue Brain SNAP SONATA interpretation
======================================

The `Blue Brain SNAP <https://github.com/BlueBrain/snap>`_ library is the default library at |bbp|
for reading sonata circuits in python.

This page describes the major sonata interpretation done by |snap| to read a sonata circuit.
This circuit or the simulation configs are the objects that bound altogether the different parts of
a circuit or a simulation campaign. They are the entry points for the snap main interface:
`Circuit` and `Simulation`.

The Circuit Config
------------------

The circuit config is used for the static part of the circuit. That is, the network.
This file is a standard json file with multiple keys corresponding to the different parts of the
circuit or utilities for accessing the files.

A standard circuit config at |bbp| is :

.. code-block:: shell

    $ cat circuit_config.json
    {
      "manifest": {
        "$BASE_DIR": ".",
        "$COMPONENT_DIR": "./component",
        "$NETWORK_DIR": "$BASE_DIR/network"
      },
      "components": {
        "morphologies_dir": "$COMPONENT_DIR/morphologies",
        "biophysical_neuron_models_dir": "$COMPONENT_DIR/biophysical_neuron_models"
      },
      "node_sets_file": "$BASE_DIR/node_sets.json",
      "networks": {
        "nodes": [
          {
            "nodes_file": "$NETWORK_DIR/neurons.h5",
            "node_types_file": "$NETWORK_DIR/node_types.csv"
          },
          {
            "nodes_file": "$NETWORK_DIR/projections.h5",
            "node_types_file": null
          }
        ],
        "edges": [
          {
            "edges_file": "$NETWORK_DIR/edges.h5",
            "edge_types_file": null
          }
        ]
      }
    }

We read this file using the class :

.. code-block:: python

   >> from bluepysnap import Config
   >> Config("circuit_config.json").resolve()


Key "manifest"
~~~~~~~~~~~~~~

The manifest keys is a not mandatory section used to define the different anchor paths and to
resolve all the file paths from the ``circuit_config.json``. The associated value to the
``manifest`` key is a dictionary with different paths which can be absolute or relative to an anchor.

In |snap|, we resolve all the anchor paths as absolute paths and the rules are:
    - All anchors must be resolved as absolute paths.
    - A dot ``.``  is interpreted as the directory containing the ``circuit_config.json`` itself; it will be called
      the ``configdir`` below and it is an absolute path.
    - All the ``./path`` are resolved from the ``configdir``.
    - ``$BASE_DIR/path`` : ``$BASE_DIR`` is first resolved and then ``path`` is attached to it.

Examples: with ``circuit_config.json`` in a ``\circuit\config`` directory:
   - ``{"$BASE_DIR": "."}`` |rarr| ``\circuit\config``
   - ``{"$COMPONENT_DIR": "./component"}`` |rarr| ``\circuit\config\component``
   - ``{"$NETWORK_DIR": "$BASE_DIR/network"}`` |rarr| ``\circuit\config\network``

.. note::
    User needs to keep in mind that all the returned values will be **paths** and not text. So
    combining two anchors is equivalent to: ``os.path.join(abs_path1, abs_path2)`` |rarr| ``abs_path2``

.. warning:: To avoid possible errors, some cases are forbidden :

   - ``{"$MULTIPLE_ANCHORS": "$BASE_DIR/$COMPONENT_DIR/is_wrong"}``: this would combine two absolute paths
     which does not make sense (see note above).
   - if the anchor cannot be interpreted as an absolute path. That is: ``{"$BASE_DIR": "relative_directory"}``,
     the ``Config`` class raises. You need to use : ``{"$BASE_DIR": "./relative_directory"}`` or
     ``{"$BASE_DIR": "$ANCHOR/relative_directory"}`` instead.

Paths in the config files
^^^^^^^^^^^^^^^^^^^^^^^^^

A json file cannot distinguish between a normal string and a path.
Therefore only string values containing an anchor or starting with a ``'.'`` are considered as a path, at the config level.
All the strings starting with a ``'.'`` are resolved from the ``configdir`` even if
the manifest is not present.


Key "components"
~~~~~~~~~~~~~~~~

This key is not mandatory and defines the "extra files" for the circuit. All the possible extra files
are described in the `specs <https://github.com/AllenInstitute/sonata/blob/master/docs/SONATA_DEVELOPER_GUIDE.md#tying-it-all-together---the-networkcircuit-config-file>`_.

In |snap| currently only ``"morphologies_dir"`` is used and only for the biophysical nodes.

Key "Node sets file"
~~~~~~~~~~~~~~~~~~~~

The `node sets file` defines sub-group of nodes from the circuit. There is **only one** node sets file
per circuit and this file is a simple ``.json`` file.


Key "networks"
~~~~~~~~~~~~~~

In the ``networks`` section the path to the network files are specified.
These are the ``nodes`` and ``edges`` file described in the section :ref:`here <sonata_tech>`.


The Simulation Config
---------------------

The `simulation config` is used for the dynamic part of the circuit, i.e. the simulations.
This file is a standard json file with multiple keys corresponding to the different parts of the circuit and some
scientific inputs.

A standard simulation config at |bbp| looks for example like this:

.. code-block:: python

    {
      "manifest": {
        "$OUTPUT_DIR": "./reporting",
        "$INPUT_DIR": "./"
      },
      "run": {
        "tstop": 1000.0,
        "dt": 0.01,
        "spike_threshold": -15,
        "nsteps_block": 10000,
        "seed": 42
      },
      "target_simulator":"my_simulator",
      "network": "$INPUT_DIR/circuit_config.json",
      "conditions": {
        "celsius": 34.0,
        "v_init": -80,
        "other": "something"
      },
      "node_sets_file": "$INPUT_DIR/node_sets_simple.json",
      "mechanisms_dir": "../shared_components_mechanisms",
      "inputs": {
        "current_clamp_1": {
          "input_type": "current_clamp",
          "module": "IClamp",
          "node_set": "Layer23",
          "amp": 190.0,
          "delay": 100.0,
          "duration": 800.0
        }
      },

      "output":{
        "output_dir": "$OUTPUT_DIR",
        "log_file": "log_spikes.log",
        "spikes_file": "spikes.h5",
        "spikes_sort_order": "time"
      },

      "reports": {
        "soma_report": {
          "cells": "Layer23",
          "variable_name": "m",
          "sections": "soma",
          "enabled": true
        },
        "section_report": {
          "cells": "Layer23",
          "variable_name": "m",
          "sections": "all",
          "start_time": 0.2,
          "end_time": 0.8,
          "dt": 0.02,
          "file_name": "compartment_named"
        }
      }
    }


Key "manifest"
~~~~~~~~~~~~~~

The manifest part is exactly the same as the `circuit config manifest` and the paths are resolved the
same way.

.. warning:: Other keys needs to be defined by HPC team.


Node Sets
---------

In |snap| they are handled by the `NodeSets <https://github.com/BlueBrain/snap/blob/master/bluepysnap/node_sets.py>`_ class:

.. code-block:: python

   >> from bluepysnap.node_sets import NodeSets
   >> node_sets = NodeSets("node_sets_file.json")
   >> node_sets.resolved
   {
   'Excitatory': {'synapse_class': 'EXC'},
   }


The different node sets are defined inside the node sets file using different queries to select the
corresponding nodes.

In the example above, there is only one node set named ``"Excitatory"``.
This node set will select all the nodes with a field ``"synapse_class"`` equal to the
value: ``"EXC"`` (see also :ref:`here <sonata_tech>`).

You can have multiple node sets with selections based on all sonata fields:

.. code-block:: python

   >> node_sets.resolved
   {'Excitatory': {'synapse_class': 'EXC'}}
    'SLM_PPA': {'mtype': 'SLM_PPA'},
   }

and/or more complex node sets:

.. code-block:: python

   >> node_sets.resolved
   {'SLM_PPA_and_SP_PC': {'mtype': ['SLM_PPA', 'SP_PC']},
    'Excitatory_SLM_PPA': {'synapse_class': 'EXC', 'mtypes': 'SLM_PPA'}
   }

.. note:: Definitions:

  - a list means `or`: ``"SLM_PPA_and_SP_PC"`` |rarr| ``"mtype"`` == ``"SLM_PPA"`` **or** ``"SP_PC"``
  - a dictionary means `and`: ``"Excitatory_SLM_PPA"`` |rarr| ``"synapse_class"`` == ``"EXC"`` **and** ``"mtypes"`` ==  ``"SLM_PPA"``

Compounds
~~~~~~~~~

You can also combine the different node sets using "compounds" node sets. The implementation of the
compounds in snap is a `or` of all the node sets composing the compound.

.. code-block:: python

   >> node_sets.resolved
   {
   'SP_PC': {'mtype': 'SP_PC'},
   'cACpyr': {'etype': 'cACpyr'},
   'SP_PC_cACpyr': ['SP_PC', 'cACpyr']
   }

In this example, ``SP_PC_cACpyr`` means nodes with ``mtype`` equal to ``SP_PC`` **or**
``etype`` equal to ``cCpyr``.

.. warning::
    In the compounds, only lists of node sets are allowed. So you cannot combine a node set name with an
    additional query:

    .. code-block:: python

       >> node_sets.resolved
       {
       'SP_PC': {'mtype': 'SP_PC'},
       'cACpyr': {'etype': 'cACpyr'},
       'WRONG_COMPOUND': ['SP_PC', 'cACpyr', {'mtype'; 'SLM_PPA'}]
       }

    **is not correct**.


It is also possible to create compounds of compounds:

.. code-block:: python

   >> node_sets.resolved
   {
   'SLM_PPA': {'mtype': 'SLM_PPA'},
   'SP_PC': {'mtype': 'SP_PC'},
   'bAC': {'etype': 'bAC'},
   'cAC': {'etype': 'cAC'},
   'SLM_PPA_SP_PC': ['SP_PC', 'SLM_PPA'],
   'bAC_cAC': ['bAC', 'cAC'],
   'SLM_PPA_SP_PC_bAC_cAC': ['SLM_PPA_SP_PC', 'bAC_cAC']
   }

.. warning::
    If a node set name cannot be resolved, then the compound is not valid and an error is thrown.


Key "population"
~~~~~~~~~~~~~~~~

In addition, there are also two predefined keys one can use to select particular node_ids and
populations: ``population`` and ``node_id``.
This pre-defined key is used to select all nodes from a given population.

.. code-block:: python

    >> node_sets.resolved
    {
    'Hippocampus': {'population': 'hippocampus_neurons'},
    'Projection' :  {'population': 'projection_neurons'},
    'All': {'population': ['hippocampus_neurons', 'projection_neurons']}
    }

``Hippocampus`` will select all the nodes inside the ``hippocampus_neurons`` population.
``All`` selects all the nodes from the ``hippocampus_neurons`` and from the ``projection_neurons``.

Key "node_id"
~~~~~~~~~~~~~

This pre-defined key selects the ``node_ids`` to extract from the circuit.

.. code-block:: python

    >> node_sets.resolved
    {
    'Sample': {'node_id': [10, 11, 12, 13, 14, 15]},
    }

``Sample`` will select the nodes with the ``node_ids`` : ``[10, 11, 12, 13, 14, 15]``. This is important
to notice the node_ids are defined in a list so you can interpret this as a `or`.

If the ``"node_id"`` key is used alone, then the corresponding ``node_ids`` from all populations are
returned. If you want to select the ``node_ids`` from a single population only, you should
use the ``node_id`` in combination with the ``population`` key:

.. code-block:: python

    >> node_sets.resolved
    {
    'Sample': {'node_id': [10, 11, 12, 13, 14, 15]},
    'Hippocampus_sample': {'population': 'hippocampus_neurons',
                           'node_id': [10, 11, 12, 13, 14, 15]},
    }
    # ids is the snap function to access nodes from a population
    >>  circuit.nodes["hippocampus_neurons"].ids("Sample")
    [10, 11, 12]
    >> circuit.nodes["projection_neurons"].ids("Sample")
    [10, 11, 12]
    >> circuit.nodes["hippocampus_neurons"].ids("Hippocampus_sample")
    [10, 11, 12]
    >> circuit.nodes["projection_neurons"].ids("Hippocampus_sample")
    []

Rotations
---------

The rotations can be described in multiple ways in SONATA but |snap| can read some of them but not all.

The `official` way to define the rotation is to use a h5 column of size : ``[Nx4]``. The four
values are the 4 values of the quaternion that define the rotation and N is the number of nodes from the
population.

However, in its current state, ``libsonata`` cannot read 2D tables but only 1D arrays.
Therefore the 4-tuple has been split into 4 1D arrays with names:  ``orientation_w``,  ``orientation_x``,
``orientation_y``,  ``orientation_z``. This is the preferred representation of the rotation.

In addition, one can use the Euler angle representation. It consists of 3 angles: ``rotation_angle_xaxis``,
``rotation_angle_yaxis``, ``rotation_angle_zaxis``. The combination of the angle is with this ordering: :math:`z*y*x`.
The output of an orientation call is a 3D rotation matrix.
