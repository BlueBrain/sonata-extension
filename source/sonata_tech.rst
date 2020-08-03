.. _sonata_tech:
.. |snap| replace:: `Blue Brain SNAP`

SONATA Technical description
============================

The following is the definition of the file format used in the SONATA file.

Node File
---------

Example view of node file in a HDF viewer (might not show all possible fields):

.. image:: images/sonata_nodes.png
    :align: center
    :width: 300px
    :alt: alternate text


Fields for Nodes
~~~~~~~~~~~~~~~~

The following fields are mandatory as per specification and are used in the pipeline.

If the type of a field is ``text`` it is possible to use an enumeration in the `@library` for more efficient memory use.
That should be used preferably for the fields like

- ``morphology``
- ``model_type``
- ``etype``
- ``mtype``
- ``synapse_class``
- ``morph_class``

These attributes ``/<population>/<group>/X`` have a corresponding attribute ``/<population>/<group>/@library/X`` with a limited set of `text` values.
The group ``@library`` is reserved for this purpose.

.. As per ``SONATA`` specification, these values should be stored as integer values and be resolved to strings.

.. table::

    ==============================  ========== =========================================================================================
    Field                           Type        Description
    ==============================  ========== =========================================================================================
    ``x``, ``y``, ``z``             float      The position of the center of the soma in the local world in :math:`\mu m`.
    ``rotation_angle_[x|y|z]axis``  float      Euler angle representation of the rotation around the given axis of the morphology around the soma in radians.
    ``orientation_[w|x|y|z]``       float      Preferred way to define the rotation as quaternions.
    ``morphology``                  text       Morphology file name, without file extension. The current implementation of connectome building expects a file ending in ``.h5``.
    ``layer``                       text       Names the layer for the morphology.
    ``model_template``              text       See details below
    ``model_type``                  text       Has 4 valid values: `biophysical`, `virtual`, `single_compartment`, and `point_neuron`.
    ``morph_class``                 text       Used to define the morphology classification,. ... ***TBD***
    ``etype``                       text       Defines the electrical type of the node.
    ``mtype``                       text       Defines the morphological type of the node.
    ``synapse_class``               text       Defines the synapse type of the node () ... ***TBD***
    ``region``                      text       Attribute assigning a brain region to the associated cell.
    ``threshold_current``           float      The minimal amplitude (in nA) of a step current clamp injection that triggers an action potential.
    ``holding_current``             float      The current clamp amplitude (in nA) necessary to hold the cell at a predefined holding voltage (typically around -85 mV for BBP).
    ==============================  ========== =========================================================================================



model_template
~~~~~~~~~~~~~~

The ``model_template`` is used to reference a template or class describing the electrophysical
properties and mechanisms of the node(s).
Its value and interpretation is context-dependent on the corresponding ‘model_type’.
When there is no applicable model template for a given model type (i.e. model_type=virtual)
it is assigned a value of NULL.
Otherwise, within BBP, it uses a colon-separated string-pair with the following syntax:

   ``hoc:resource``

where ``resource`` is a reference to the template file-name or class.


Edge File
---------

Example view of node file in a HDF viewer (might not show all possible fields):

.. image:: images/sonata_edges.png
    :align: center
    :alt: alternate text

Fields for Edges
~~~~~~~~~~~~~~~~

The following fields are mandatory as per specification and are used in the pipeline.
For the type ``enum``, see details above.

.. table::

    =============================  ========== =========================================================================================
    Field                          Type        Description
    =============================  ========== =========================================================================================
    ``afferent_center_[x|y|z]``    float      Position on the `axis` of the cell's section/segment.
    ``afferent_surface_[x|y|z]``   float      Position on the surface of a cylindrical cell segment, radially outward from the center position in the direction of the other cell.
    ``afferent_section_id``        int        The specific section on the target node where a synapse is placed.
    ``afferent_section_pos``       float      Fractional position along the length of the section (normalized to the range [0, 1], where 0 is at the start of the section and 1 is at the end of the section).
    ``afferent_section_type``      int        ???
    ``afferent_segment_id``        int        Numerical index of the section of the cell (soma is index 0).
    ``afferent_segment_offset``    float      ???
    ``conductance``                float      The conductance of ??? in ??? .
    ``decay_time``                 float      ???
    ``delay``                      float      the axonal delay (in ms; ``NaN`` for dendro-dendritic synapses).
    ``depression_time``            float      ???
    ``efferent_center_[x|y|z``     float      Same as ``afferent_center_[x|y|z]``, but for the synapse position at the axon of the presynaptic cell.
    ``efferent_surface_[x|y|z]``   float      Same as ``efferent_center_[x|y|z]``, but the for the synapse location on the axon surface.
    ``efferent_section_id``        int        Same as ``afferent_section_id``, but for source node.
    ``efferent_section_pos``       float      Same as ``afferent_section_pos``, but for source node.
    ``efferent_section_type``      int        ???
    ``efferent_segment_id``        int        Numerical index of the section of the cell (soma is index 0).
    ``efferent_segment_offset``    float      ???
    ``faciliation_time``           float      ???
    ``n_rrp_vesicles``             int        ???
    ``spline_length``              float      Distance between the two surface positions (in unit ???).
    ``syn_type_id``                int        ???
    ``u_syn``                      float      ???
    ``edge_type_id``               int        ???
    ``source_node_id``             int        see below
    ``target_node_id``             int        see below
    =============================  ========== =========================================================================================



Fields for electrical_synapse connection type edges
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning:: To Be Done

Fields for chemical connection type edges
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``source_node_id``
- ``target_node_id``
- ``delay`` the axonal delay (in ms, ``NaN`` for dendro-dendritic synapses)

Fields for synapse_astrocyte connection type edges
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``source_node_id`` the node id of the astrocyte
- ``target_node_id`` the node id of the post synaptic neuron
- ``efferent_section_id`` the astrocyte section id
- ``efferent_section_pos`` the position along the length of the efferent section of the astrocyte (normalized to the range [0, 1], where 0 is at the start of the section and 1 is at the end of the section)

Fields for endfoot connection type edges
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``source_node_id`` the node id of the astrocyte
- ``target_node_id`` the node id of the vasculature
- ``efferent_section_id`` the astrocyte section id
- ``efferent_section_pos`` the position along the length of the efferent section of the cell (normalized to the range [0, 1], where 0 is at the start of the section and 1 is at the end of the section)
- ``afferent_section_id`` the vasculature section id
- ``afferent_section_pos`` the position along the length of the afferent section of the vasculature (normalized to the range [0, 1], where 0 is at the start of the section and 1 is at the end of the section)


Consumers
---------

Consumers use the sonata ``.h5`` files, and depending on the tool the required fields are different.

TouchDetector
~~~~~~~~~~~~~

Required fields for ``TouchDetector``:
   - ``x``, ``y``, ``z``
   - ``orientation_w``, ``orientation_x``, ``orientation_y``, ``orientation_z``
   - ``morphology``
   - ``region``
   - ``mtype``

Spykfunc
~~~~~~~~

Required fields for ``Spykfunc``:
   - ``morphology``
   - ``etype``
   - ``mtype``
   - ``synapse_class``

.. _specification: https://github.com/AllenInstitute/sonata/blob/master/docs/SONATA_DEVELOPER_GUIDE.md
.. _enumeration: https://github.com/AllenInstitute/sonata/blob/master/docs/SONATA_DEVELOPER_GUIDE.md#nodes---enum-datatypes
