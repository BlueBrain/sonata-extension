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

A list of default properties where to find circuit components.

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
   populations                    Optional     Additional properties to override components related to the populations.
   type                           Optional     The type of the population: a value in [`biophysical`, `virtualnode`, `single_compartment`, `point_neuron`].
                                               Default is `biophysical`.
   ============================== ============ ==========================================

.. note:: Type is redundant with model_type and defines the expected properties for the nodes. The initial SONATA specification requires a complete dataset with the same value for model_type for *all* the nodes, which is inefficient in term of storage and access to the information. Another option could be to have it as an H5 attribute. The same pattern applies to the edges but the SONATA specification does not defined anything here to differentiate chemical_synapses, electrical, endfoot... The proposal is to have it in the .json in both cases for the nodes and for the edges. 


populations
"""""""""""

*Optional*.

A property of a node overriding default components.
This property is a dictionary with keys being node population names contained in the nodes_file and the values are dictionaries with the same properties than `components`_.

example::

  node_population_a overriding the default components with its own.
  node_population_b do not override anything.

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
                   "type: "biophysical",
                   "morphologies_dir": "...",   
                   "biophysical_neuron_models_dir": "...",
                   "alternate_morphologies": ...
                ...},
                "node_population_b": {
                  "type": "virtualnode"
            }
        },
        ...
    ] 


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
   populations                    Optional     Additional properties to override components related to the populations.
   type                           Optional     The connection type of the population: a value in [`chemical_synapse`, `electrical`, `synapse_astrocyte`, `endfoot`].
                                               Default is `chemical_synapse`.
   ============================== ============ ==========================================

populations
"""""""""""

*Optional*.

A property of an edge overriding default components.
This property is a dictionary with keys being edge population names contained in the edges_file and the values are dictionaries with the same properties than `components`_.
