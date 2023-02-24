.. _sonata_overview:
.. |bbp| replace:: `BBP`


SONATA Circuit overview
=======================

This section describes the `SONATA` specification as used within |bbp|.

History
-------

The `SONATA` specification loosely defines a container interface to store
nodes and edges of a circuit.  A full "definition" can be found in the official
specification_, while this document will only refer to a subset of the `SONATA`
specification to instruct its use.

Objective
---------

The format should be used to disseminate files to the public.

Circuit Config
--------------

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
            "node_types_file": null,
            "populations": {
              "node_population_a": {
                "type": "biophysical"
              }
            }
          },
          {
            "nodes_file": "$NETWORK_DIR/projections.h5",
            "node_types_file": null,
            "node_population_b": {
              "type": "virtual"
            }
          }
        ],
        "edges": [
          {
            "edges_file": "$NETWORK_DIR/edges.h5",
            "edge_types_file": null,
            "populations": {
                "edges-AB": {}
            }
          }
        ]
      }
    }

.. warning:: Within |bbp| we do not use ``.csv`` files as defined in the specification!

Nodes and Edges
---------------


Sonata is a graph format created to represent the brain structures
and their connections. The standard usage is to represent a
neuronal circuit as a `graph`, with `nodes` being the brain cells
and `edges` for their connections (touches, synapses, etc).


Formally speaking, Sonata graphs are multipart edge-labeled
directed multigraphs. It means:

* nodes and edges can be separated into different subsets (i.e: populations)
* multiple edges between two nodes are allowed
* the edges are oriented (A->B is different than B->A)

Moreover, the format is specialized to compactly represent graphs with a lot of connections between two nodes.


Populations
-----------

To distinguish between nodes and edges contained or connecting different
brain parts, `polulations` are used as per the `SONATA` specification.
For detailed information see the next section :ref:`here <sonata_population>`.


.. _specification: https://github.com/AllenInstitute/sonata/blob/master/docs/SONATA_DEVELOPER_GUIDE.md

Groups
------

As per the `SONATA` specification it is possible to define several node groups, but within BBP we restrict to a single group ``0``.
Therefore, the sonata-fields ``node_group_id`` and ``node_group_index`` are **not used** (see :ref:`here <sonata_tech>` for details about the fields).

This decision has been taken to reduce the number of indirection to access the different attributes of the nodes and edges in order to improve the performance.


Morphologies
------------

In the |bbp| realm we use only ``.swc`` files consistent with the `SONATA` definition.
