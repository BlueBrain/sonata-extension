.. _recipe:

Recipe description
==================

.. highlight:: json

This document specifies all parameters required to generate the connectome of a circuit.

Components of the recipe are used by TouchDetector and Functionalizer as noted.  An
example or a TouchDetector configuration may look like:

.. code:: yaml

   recipe:
     bouton_distances:
       min_distance: 0.1
       max_distance: 10.0
       region_gap: 5.0
     structural_spine_lengths:
       - mtype: L7_A
         spine_length: 5.0
       - mtype: L9_DKE
         spine_length: 12.3

.. _selection:

Generic pathway selection
-------------------------

One can create rules that only apply to certain "pathways" by restricting attributes of
source and target node populations.
As such, the rules have properties that are prefixed with `src_` to match attributes from
the source node population, and likewise prefixed with `dst_` to match target node
population attributes.  All attributes are described in :ref:`node_file`, the currently
supported ones are:

- ``etype``
- ``mtype``
- ``region``
- ``synapse_class``

All supported attributes support the use of simple wild cards.  The following rule matches
all synapses connecting cells of MType starting with ``L6_`` to ones with MType
``L1_PYR``, from any source region to the target region ``SPYR``:

.. code:: yaml

   - src_mtype: "L6_*"
     src_region: "*"
     dst_mtype: "L1_PYR"
     dst_region: "SPYR"

When a component can be stored as a Pandas DataFrame, all used attributes have to be
referred to with a ``_i`` suffix and stored as numerical values corresponding to the index
of the attribute value in the `@library` field of the node files.  Wildcards are no longer
allowed, but a numerical value of ``-1`` may be used to match all possible values.

.. warning::

   Storing recipe components in DataFrames ties the recipe strongly to one circuit.  Only
   if the order in the used `@library` fields matches exactly may the recipe be reused
   for a different circuit.

Given MType values of ``L1_PYR``, ``L2_FOO``, ``L6_SPAM``, ``L6_HAM``, ``L6_EGGS``, and
region values of ``BLARGH``, ``SPYR``, the above rule then turns into:

.. table::

   =========== ============ =========== ============
   src_mtype_i src_region_i dst_mtype_i dst_region_i
   =========== ============ =========== ============
   3           -1           0           1
   4           -1           0           1
   5           -1           0           1
   =========== ============ =========== ============

Generic Components
------------------

``version``
^^^^^^^^^^^

*Required*.

An integer representing the current version of the recipe.  This document describes
version 1.

Components specific to TouchDetector
------------------------------------

Both components are *required* when running TouchDetector.

``bouton_interval``
^^^^^^^^^^^^^^^^^^^

*Required*.

Distances used when transforming touch regions into synapse candidates.

.. table::

   =============================== =========== ===
   Property                        Requirement Description
   =============================== =========== ===
   ``min_distance``                Mandatory   The minimum distance at which two synapse candidates are placed from each other in µm.
   ``max_distance``                Mandatory   The maximum distance at which two synapse candidates are placed from each other in µm.
   ``region_gap``                  Mandatory   The maximum distance between two touch regions at which they are merged in µm.
   =============================== =========== ===

``structural_spine_lengths``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*Required*.

A list that specified how long the spines for certain MTypes may be. Requires that all
MTypes have a spine length assigned. Each item of the list must have the following
properties:

.. table::

   =============================== =========== ===
   Property                        Requirement Description
   =============================== =========== ===
   ``mtype``                       Mandatory   The MType to apply the spine length to.
   ``spine_length``                Mandatory   Maxiumum spine length, in µm.
   =============================== =========== ===

Components specific to Functionalizer
-------------------------------------

Components used by Functionalizer may only be required when the corresponding filter is
used. I.e., if only the `SynapseProperties` filter is used, only the
``synapse_properties`` part of the recipe is required.

``bouton_distances``
^^^^^^^^^^^^^^^^^^^^

*Optional*.

Minimum distances for synapses, as measured along the branch length, starting at the soma.
Synapses with less than the specified distance will be removed by Functionalizer.

.. table::

   =============================== =========== ===
   Property                        Requirement Description
   =============================== =========== ===
   ``excitatory_synapse_distance`` Optional    The minimum distance from the soma for a synapse of post-synaptic excitatory cells in µm. Defaults to 5µm.
   ``inhibitory_synapse_distance`` Optional    The minimum distance from the soma for a synapse of post-synaptic inhibitory cells in µm. Defaults to 25µm.
   =============================== =========== ===

``connection_rules``
^^^^^^^^^^^^^^^^^^^^

*Required*.

A list of rules that are used to determine how synapse distributions are calculated for
pathways, and used to reduce the structural connectome to a functional one.

Each rule may have properties corresponding to :ref:`selection`. In addition to the
selection attributes, exactly one set of parameters have to be used:

- ``mean_syns_connection``, ``stdev_syns_connection``, and ``active_fraction``
- ``bouton_reduction_factor``, ``cv_syns_connection``, and ``active_fraction``
- ``bouton_reduction_factor``, ``cv_syns_connection``, and ``mean_syns_connection``
- ``bouton_reduction_factor``, ``cv_syns_connection``, and ``probability``
- ``bouton_reduction_factor``, ``pMu_A``, and ``p_A``

Where the parameters signify:

.. table::

   =============================== ===
   Parameter                       Description
   =============================== ===
   ``active_fraction``             The fraction of synapses to be removed in the third pruning step.
   ``bouton_reduction_factor``     The fraction of synapses to be removed in all three pruning steps.
   ``cv_syns_connection``          The target value for the coefficient of variation of the distribution of synapses per connection distribution of synapses per connections.
   ``mean_syns_connection``        The target value for the mean of the distribution of synapses per connections.
   ``p_A``                         The reduction factor.
   ``pMu_A``                       Used as input to the survival rate.
   ``probability``                 The target connection probability. To be deprecated.
   ``stdev_syns_connection``       The target value for the standard deviation of the distribution of synapses per connection.
   =============================== ===

``gap_junction_properties``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

*Optional*.

A global default setting for the conductance produced by Functionalizer.

.. table::

   =============================== =========== ===
   Property                        Requirement Description
   =============================== =========== ===
   conductance                     Optional    The conductance to be used by all synapses. Defaults to 0.2.
   =============================== =========== ===

``seed``
^^^^^^^^

*Optional*.

One of the random number seeds to be used when drawing distributions to cut synapses or
determine properties.

``synapse_properties``
^^^^^^^^^^^^^^^^^^^^^^

*Required*.

Settings to generate synaptic properties for appositions.  Each apposition is classified
by rules and synaptic properties are generated per cell-cell connection following the
parameters of the property configuration.

.. table::

   =============================== =========== ===
   Property                        Requirement Description
   =============================== =========== ===
   ``rules``                       Mandatory   Rules to classify synapses
   ``classes``                     Mandatory   Synapse classes used to assign properties
   =============================== =========== ===

``rules``
~~~~~~~~~

Each rule may have properties corresponding to :ref:`selection`. In addition to the
selection attributes, the following parameters may be present:

.. table::

   ==================================== =========== ===
   Property                             Requirement Description
   ==================================== =========== ===
   ``class``                            Mandatory   A name that will be referenced by ``classes``.  It has to start with either ``E`` for excitatory connections or ``I`` for inhibitory connections.
   ``neural_transmitter_release_delay`` Optional    Defaults to 0.1 ms
   ``axonal_conduction_velocity``       Optional    Defaults to 300 μm/ms
   ==================================== =========== ===

Please note that contrary to the legacy XML recipe, precedence is handled very strict:
later rules always override earlier ones.  There is no special treatment for more general
rules to not override more specialized ones.

``classes``
~~~~~~~~~~~

Here, the ``class`` field has to match a ``class`` value of the
``rules``. The properties are assigned using the following
random number distributions, using a mean `m` and standard deviation `sd`:

- A Gamma-distribution, with shape parameter equal to `m² / sd²`, and
  scale parameter equal to `sd² / m`.
- A truncated Normal-distribution, where values are redrawn until they are
  both positive and within the range of `m±sd`.
- A Poisson-distribution using only `m`.

The same drawn number is reused for all synapses within the same source to
target cell connection.

The following properties are supported, with the mean specified by the
property name, and the standard deviation by appending ``_sd`` to the
property name:

.. table::

   ==================================== =========== ===
   Property                             Requirement Description
   ==================================== =========== ===
   ``conductance_mu``                   Mandatory   The central value for the peak conductance (in nS) for a single synaptic contact, following a Gamma distribution.
   ``conductance_sd``                   Mandatory   Standard deviation of ``conductance``.
   ``depression_time_mu``               Mandatory   Central value for the time constant (in ms) for recovery from depression, following a Gamma distribution.
   ``depression_time_sd``               Mandatory   Standard deviation of ``depression_time``.
   ``facilitation_time_mu``             Mandatory   Central value for the time constant (in ms) for recovery from facilitation, following a Gamma distribution.
   ``facilitation_time_sd``             Mandatory   Standard deviation of ``f``.
   ``u_syn_mu``                         Mandatory   Central value for the utilization of synaptic efficacy, following a truncated Normal distribution.
   ``u_syn_sd``                         Mandatory   Standard deviation of ``u``.
   ``decay_time_mu``                    Mandatory   Central value for the decay time constant (in ms), following a truncated Normal distribution.
   ``decay_time_sd``                    Mandatory   Standard deviation of ``dtc``.
   ``n_rrp_vesicles_mu``                Mandatory   Central value for the number of vesicles in readily releasable pool, following a Poisson distribution.

   ``conductance_scale_factor``         Optional    The scale factor for the conductance; `SRSF`: 'synaptic receptor scaling factor'.
   ``u_hill_coefficient``               Optional    A coefficient describing the scaling of `u` to be done by the simulator.
   ==================================== =========== ===

Truncated Normal distributions are limited to the central value ±σ and are
re-rolled until positive values has been obtained.

The ``u_hill_coefficient`` is used as follows:

.. math::

   u_\text{final} = u \cdot y \cdot \frac{ca^4}{u_\text{Hill}^4 + ca^4}

where :math:`ca` denotes the simulated calcium concentration in millimolar and :math:`y` a
scalar such that at :math:`ca = 2.0:\ u_\text{final} = u`. (Markram et al., 2015)

These attributes will be copied for each synapse corresponding to its
classification.  If they are not specified, no corresponding columns will
be created in the output.

``synapse_reposition``
^^^^^^^^^^^^^^^^^^^^^^

*Required*.

.. table::

   =============================== =========== ===
   Property                        Requirement Description
   =============================== =========== ===
   ``src_mtype``                   Mandatory   The MType of the source cell.
   ``dst_mtype``                   Mandatory   The MType of the target cell.
   ``class``                       Mandatory   Has to be ``AIS``.
   =============================== =========== ===

``touch_rules``
^^^^^^^^^^^^^^^

*Required*.

Determines which touches are allowed, depending on source and target node population
MType, as well the section type on either the source or target side of the touch.

.. table::

   =============================== =========== ===
   Property                        Requirement Description
   =============================== =========== ===
   ``src_mtype``                   Mandatory   The MType of the source cell.
   ``dst_mtype``                   Mandatory   The MType of the target cell.
   ``afferent_section_type``       Optional    The section type of the target cell
   ``efferent_section_type``       Optional    The section type of the source cell.
   =============================== =========== ===

The ``afferent_section_type`` and ``efferent_section_type`` may take the values ``soma``,
``axon``, ``apical``, and ``basal``.  A special value ``dendrite`` may be used to signify
both ``apical`` and ``basal`` types.

``touch_reduction``
^^^^^^^^^^^^^^^^^^^

*Required*.

Used to cut touches according to a flat survival rate set by the user.  Affects all
touches the same way.

.. table::

   =============================== =========== ===
   Property                        Requirement Description
   =============================== =========== ===
   ``survival_rate``               Mandatory   A flat survival probability of touches.
   =============================== =========== ===
