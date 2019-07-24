.. _sonata:

SONATA circuit description
==========================

History
-------

The `SONATA` specification loosely defines a container interface to store
nodes and edges.  A full "definition" can be found in the official
specification_, this document will only refer to a subset of the `SONATA`
specification to instruct its use.

Objective
---------

The format should be used to disseminate files to the public.

File Format
-----------

The following is the practical definition of the files used in the
pipeline.

Populations
~~~~~~~~~~~

To distinguish between nodes and edges contained or connecting different
brain parts, we will use populations, as per the `SONATA` specification.
For simplicity, it is recommended to save each population in a separate
file.

For nodes, the following naming scheme is proposed::

    /nodes/${part}_${type}

Where ``${part}`` may be `NCX` for the neocortex, and ``${type}`` can
presently take the following values:

 - `neurons`
 - `astrocytes`

Examples::

    /nodes/thalamus_astrocytes
    /nodes/thalamus_neurons
    /nodes/ncx_astrocytes
    /nodes/ncx_neurons

Connectivity between these populations is directional, and edges will be
contained in populations specifying `source` and `target` node populations
as well as connection type::

    /edges/${source_population}__${target_population}__${connection_type}

If `source` and `target` population are identical, a single population may
also be bi-directional.

Currently, the following connection types are supported:

 - `electrical`
   this includes gap junctions for instance.
 - `chemical_synapse`
   this would include the following possible subtypes: glutamatergic, gabaergic, dopaminergic, serotinergic, adrenergic
 - `synapse_astrocyte`
   this manages the connection from an astrocyte to a particular synapse
 - `endfoot`
   this manages the connection between a vasculature and an astrocyte


Examples::

    /edges/thalamus_neurons__ncx_neurons__chemical

Fields for Nodes
~~~~~~~~~~~~~~~~

The following attributes are mandatory as per specification and are used in the pipeline:

 - `x`, `y`, `z` stored as float in μm:

       The position of the center of the soma in the local world.

 - `orientation_w`, `orientation_x`, `orientation_y`, `orientation_z`
   stored as float:

       Quaternion with the local world rotation of the morphology around the
       soma center.

 - `morphology` name, without file ending. The current implementation of
   connectome building expects a file ending in ``.h5``.

Furthermore, the following fields are required to be stored as an
`enumeration`_:

 - `etype`
 - `mtype`
 - `region`
 - `synapse_class`

As per `SONATA` specification, these values should be stored as integer
values and be resolved to strings.

Legacy fields that are not supported any longer:

 - `layer`, now contained within `mtype`


Fields for electrical_synapse connection type edges
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Fields for chemical connection type edges
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- `source_node_id`
- `target_node_id`
- `delay` the axonal delay
  NaN for dendro-dendritic synapses

Fields for synapse_astrocyte connection type edges
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- `source_node_id` the node id of the astrocyte
- `target_node_id` the node id of the post synaptic neuron
- `efferent_section_id` the astrocyte section id
- `efferent_section_pos` the position along the length of the efferent section of the astrocyte (normalized to the range [0, 1], where 0 is at the start of the section and 1 is at the end of the section)
- `edge_id` the edge id of the synapse

Fields for endfoot connection type edges
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- `source_node_id` the node id of the astrocyte
- `target_node_id` the node id of the vasculature
- `efferent_section_id` the astrocyte section id
- `efferent_section_pos` the position along the length of the efferent section of the astrocyte (normalized to the range [0, 1], where 0 is at the start of the section and 1 is at the end of the section)
- `afferent_section_id` the vasculature section id
- `afferent_section_pos` the position along the length of the afferent section of the vasculature (normalized to the range [0, 1], where 0 is at the start of the section and 1 is at the end of the section)

Consumers
---------

 - TouchDetector. Node fields utilized:

    - `x`, `y`, `z`
    - `orientation_w`, `orientation_x`, `orientation_y`, `orientation_z`
    - `morphology`
    - `region`
    - `mtype`

 - Spykfunc. Node fields utilized:

    - `morphology`
    - `etype`
    - `mtype`
    - `synapse_class`

.. _specification: https://github.com/AllenInstitute/sonata/blob/master/docs/SONATA_DEVELOPER_GUIDE.md
.. _enumeration: https://github.com/AllenInstitute/sonata/blob/master/docs/SONATA_DEVELOPER_GUIDE.md#nodes---enum-datatypes
