.. _sonata_config:

SONATA Configuration file
=========================

version
-------

*Optional*.

An integer defining the version of the SONATA specification.
The default value is "1" as for the specification described in the SONATA original paper.
This version is "2".


manifest
--------

*Optional*.

A set of variables defining paths.
A variable can be defined as:

- "." which is the path to the directory containing the circuit_config.json

- an absolute path

- the concatenation of a variable followed by a path element.

"." is always resolved as the directory containing the circuit_config.json even in the absence in manifest.


components
----------

*Optional*.

These properties can be found under components where they will act as default values for the populations.
They can be found also under "populations" where in that case the property applies only to the particular population.

.. table::

   =============================== =========== ====================================
   Property                        Requirement Description
   =============================== =========== ====================================
   morphologies_dir                Optional    Path to the directory containing the morphologies.
                                               This path is used in conjonction with the morphology property (see :doc:`sonata_tech`) to find the morphology.
                                               By default, the concatenation of the morphology_dir + morphology_property + ".swc" extension.
                                               There must be one defined for `biophysical` node populations.
   `alternate_morphologies`_       Optional    Dictionary for alternate directory paths.
   biophysical_neuron_models_dir   Optional    Path to the template HOC files defining the E-Model.
                                               There must be one defined for `biophysical` node populations.
                                               This is used in concatenation with the `model_template` property (see :doc:`sonata_tech`) to retrieve the path the the actual HOC file.
   vasculature_file                Optional    Path to the .h5 file containing the vasculature morphology.
                                               Only for `vasculature` node populations where it is mandatory.
   vasculature_mesh                Optional    Path to the .obj file containing the mesh of a vasculature morphology.
                                               Only for `vasculature` node populations where it is mandatory.
   end_feet_area                   Optional    Path to the .h5 representing end feet meshes.
                                               Only for `endfoot` edge populations where it is mandatory.
   spine_morphologies_dir          Optional    Path to the directory containing the dendritic spine morphologies.
                                               This path is used in conjonction with the spine_morphology property (see :doc:`sonata_tech`) to find the spine_morphology.
                                               By default, the concatenation of the spine_morphologies_dir + spine_morphology_property + ".h5" extension.
   =============================== =========== ====================================

alternate_morphologies
^^^^^^^^^^^^^^^^^^^^^^
An *optional* dictionary for different representations of the morphologies than the default .swc.

.. table::

   =============================== =========== ====================================
   Property                        Requirement Description
   =============================== =========== ====================================
   'neurolucida-asc'               Optional    Path to the directory containing the morphologies in neurolucida ascii format.
   'h5v1'                          Optional    Path to the directory containing the morphologies in h5v1 format.
   =============================== =========== ====================================

example::

  Certain tools prefer alternative morphologies representation than the default SONATA ones.

  "components": {
       "morphologies_dir": "/gpfs/bbp.epfl.ch/path/to/swc",
       "alternate_morphologies": {
           "neurolucida-asc": "/gpfs/bbp.epfl.ch/path/to/neurolucida/asc",
           "h5v1": "/gpfs/bbp.epfl.ch/path/to/h5v1"
       }

  }

node_sets_file
--------------

*Optional*.

A file defining the list of nodesets applicable to this circuit. (see :doc:`sonata_nodeset`)

.. todo::

    will be defined along with nodesets file specification.

networks
--------

*Mandatory*.

A dictionary defining the nodes and edges properties.

nodes
^^^^^

*Mandatory*.

A list defining the available populations of nodes.
Node files must be relative to ".".

.. table::

   ============================== ============ ==========================================
   Property                       Requirement  Description
   ============================== ============ ==========================================
   nodes_file                     Mandatory    The node file containing one or multiple node populations.
   node_types_file                Optional     Unused at BBP.
   populations                    Mandatory    Additional properties to override components related to the populations.
   ============================== ============ ==========================================


populations
"""""""""""

*Mandatory*.

A property of a node overriding default components. This property is **mandatory within BBP** but optional to the outside community.
It is a dictionary with keys being node population names contained in the nodes_file and the values are dictionaries with the same properties as in `components`_.
There is also one additional field `type` used to denote the population type.

- The `populations` dictionary should contain only the node populations that are part of the circuit.
  It must contain at least one population, but it doesn't need to contain all the populations present in the `nodes_file` if there are more.
  It cannot be empty because it would mean that it's incomplete (ie: a population that should have been added, wasn't), or that the `nodes_file` shouldn't be added to the circuit.
- The dictionary associated to each population may be empty if the components properties don't need to be overridden: see the `node_population_c` in the example that follows.

.. _sonata_config_node_type:

.. table::

   ============================== ============ ==========================================
   Property                       Requirement  Description
   ============================== ============ ==========================================
   ...                            ...          Same as in `components`_
   type                           Optional     The type of the population, one of:
                                                  * :ref:`biophysical <biophysical_node_type>`
                                                  * `virtual`
                                                  * `single_compartment`
                                                  * `point_neuron`
                                                  * :ref:`astrocyte <astrocyte_node_type>`
                                                  * :ref:`vasculature <vasculature_node_type>`

                                               Default is `biophysical`.
   ============================== ============ ==========================================

example::

  node_population_a overriding the default components with its own.
  node_population_b and node_population_c do not override anything.

  "components": {
       "morphologies_dir": "/gpfs/bbp.epfl.ch/default//path/to/swc",
       "alternate_morphologies": {
           "neurolucida-asc": "/gpfs/bbp.epfl.ch/default/path/to/neurolucida/asc",
           "h5v1": "/gpfs/bbp.epfl.ch/default/path/to/h5v1"
       }

  },
  "nodes": [
        {
            "nodes_file": "$NETWORK_DIR/V1/v1_nodes.h5",
            "populations": {
                "node_population_a": {
                   "type": "biophysical",
                   "morphologies_dir": "...",
                   "biophysical_neuron_models_dir": "...",
                   "alternate_morphologies": ...
                },
                "node_population_b": {
                  "type": "virtual"
                },
                "node_population_c": {}
            }
        },
        ...
    ]

.. note::
    Type is redundant with model_type and defines the expected properties for the nodes.
    The initial SONATA specification requires a complete dataset with the same value for model_type for *all* the nodes, which is inefficient in terms of storage.
    Another option could be to have it as an H5 attribute.
    The same pattern applies to the edges but the SONATA specification does not defined anything here to differentiate chemical, electrical, endfoot...
    The proposal is to have it in the .json in both cases for the nodes and for the edges.

edges
^^^^^

*Mandatory*.

A list defining the available populations of edges.
Edge files must be relative to ".".

.. table::

   ============================== ============ ==========================================
   Property                       Requirement  Description
   ============================== ============ ==========================================
   edges_file                     Mandatory    A edge file path containing one or multiple node populations.
   edge_types_file                Optional     Unused at BBP.
   populations                    Mandatory    Additional properties to override components related to the populations.
   ============================== ============ ==========================================

populations
"""""""""""

*Mandatory*.

A property of an edge overriding default components. This property is **mandatory within BBP** but optional to the outside community.
It is a dictionary with keys being edge population names contained in the edges_file and the values are dictionaries with the same properties as in `components`_.
There is also one additional field `type` used to denote the population type.

- The `populations` dictionary should contain only the edge populations that are part of the circuit.
  It must contain at least one population, but it doesn't need to contain all the populations present in the `edges_file` if there are more.
  It cannot be empty because it would mean that it's incomplete (ie: a population that should have been added, wasn't), or that the `edges_file` shouldn't be added to the circuit.
- The dictionary associated to each population may be empty if the components properties don't need to be overridden.

.. table::

   ============================== ============ ==========================================
   Property                       Requirement  Description
   ============================== ============ ==========================================
   ...                            ...          Same as in `components`_
   type                           Optional     The connection type of the population, one of:
                                                  * `chemical`
                                                  * `electrical`
                                                  * `synapse_astrocyte`
                                                  * `endfoot`

                                               Default is `chemical`.
   ============================== ============ ==========================================
