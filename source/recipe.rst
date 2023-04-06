.. _recipe:

Recipe Description
==================

.. highlight:: xml

This document should specify all parameters required to generate the
connectome of a circuit.

File Format
-----------

The recipe is specified in XML, and normally stored in a directory named
`bioname`.  Customarily, the recipe is split into two files:

- `builderRecipeAllPathways.xml`
- `builderConnectivityRecipeAllPathways.xml`

The latter is usually included in the former via the entity
``&connectivityRecipe`` and describes the connectivity sampling contained
in `ConnectionRules`_.

Components
----------

Seeds
~~~~~

Part of the connectome building uses statistical sampling, with random
numbers seeded by the following optional property::

    <Seeds recipeSeed="837632" columnSeed="2906729" synapseSeed="4236279"/>

Where the possible attributes are:

- ``recipeSeed``, with a default of 0. Not used.
- ``columnSeed``, with a default of 0. Not used.
- ``synapseSeed``, with a default of 0. Used to sample reduce and cut
  survival and synapse properties.

InterBoutonInterval
~~~~~~~~~~~~~~~~~~~

The `InterBoutonInterval` is used to re-distribute touches in a more
physical way. A typical specification::

    <InterBoutonInterval minDistance="5.0" maxDistance="7.0" regionGap="5.0"/>

All distances are specified in μm.

Following touch detection, `TouchDetector` groups touches into regions
along a pre-synaptic branch - any two touches closer than ``regionGap``
will be grouped into a region. New touches will be created on the
pre-synaptic branch, spaced between ``minDistance`` and ``maxDistance``
apart. `TouchDetector` will assign the post-synaptic side of the new
touches based on the previously detected ones.

Thus the parameters are:

- ``minDistance``: minimum distance between two synapses
- ``maxDistance``: maximum distance between two synapses in a `touch
  region`
- ``regionGap``: the minimum distance between two areas designated as
  `touch regions`.

StructuralSpineLengths
~~~~~~~~~~~~~~~~~~~~~~

The `StructuralSpineLengths` group is used to determine the initial
*maximum* distance for spines, measured in µm.
`TouchDetector` will use these attributes to enlarge the radius of the
cylindrical representation of branches identified as dendrites.
Touches will then be generated along the intersecting parts of cylinders
from different cells.

To specify the spine length allowed for a morphological type, use the
following form:
::

      <StructuralSpineLengths>
          <rule mType="L6_CHC" spineLength="2.5"/>
      </StructuralSpineLengths>

.. note::
   The legacy format contained more information and may require pruning.
   The following structure is also acceptable:
   ::

      <NeuronTypes>
          <StructuralType id="L6_CHC" spineLength="2.5"/>
      </NeuronTypes>

   Where the value of ``id`` identifies the morphology type to be
   associated with the spine length.

.. warning::
   No pattern expansion will be performed for this part of the recipe.
   One rule per `mtype` present in the circuit is required.

InitialBoutonInterval
~~~~~~~~~~~~~~~~~~~~~

An *optional* XML attribute that specifies the minimum distance in μm that a
synapse needs to have from the soma. It takes the following form::

    <InitialBoutonInterval inhibitorySynapsesDistance="5.0" excitatorySynapsesDistance="25.0" />

The attributes are defined as follows:

- ``inhibitorySynapsesDistance`` the minimum distance for a synapse for
  post-synaptic inhibitory cells (default value: 5.0 μm)
- ``excitatorySynapsesDistance`` the minimum distance for a synapse for
  post-synaptic excitatory cells (default value: 5.0 μm)


TouchRules
~~~~~~~~~~

The `TouchRules` create a filter to refine the touch space used by
`TouchDetector`. They take the following form::

    <TouchRules>
        <touchRule fromMType="*PC" toMType="*" fromBranchType="*" toBranchType="soma" />
        <touchRule fromMType="*PC" toMType="*" fromBranchType="*" toBranchType="dendrite" />
    </TouchRules>

where ``*`` denotes a wildcard to match anything. In this example, touches
are allowed between all layers, but only originating from cells with
`mtype` ending in ``PC``. The former rule matches all synapses with a soma
on the post-synaptic side, while the latter matches with a dendrite on the
post-synaptic side.

Allowed parameters:

- ``fromMType`` the `mtype` of the pre-synaptic cell
- ``toMType`` the `mtype` of the post-synaptic cell
- ``fromBranchType`` the classification of the pre-synaptic branch. May be one of
  the following:
  - ``*`` to match all branches
  - ``soma`` to match the soma
  - ``dendrite`` to match all dendrites
  - ``basal`` for basal dendrites
  - ``apical`` for apical dendrites
- ``toBranchType`` the classification of the post-synaptic branch. May
  also be referred to as ``type``, for backwards compatibility.

ConnectionRules
~~~~~~~~~~~~~~~

These rules determine the distribution of synapses. They may take the
following form::

    <ConnectionRules>
      <rule fromMType="L1_NGC-DA" toMType="*" bouton_reduction_factor= "0.114" active_fraction= "0.50" cv_syns_connection= "0.25" />
      <rule fromMType="L1_HAC" toMType="L1_DAC" bouton_reduction_factor= "0.13" active_fraction= "0.50" cv_syns_connection= "0.25" />
    </ConnectionRules>

.. note::
   In older recipes, the rules take the form of:
   ::

      <mTypeRule from="L1_HAC" to="L1_DAC" />

   which will be translated into:
   ::

      <rule fromMType="L1_HAC" toMType="L1_DAC" />

   automatically.

Every rule can be used to select a subset of connections using attributes
with the prefixes:

- ``from`` for the pre-synaptic matching requirement
- ``to`` for the post-synaptic matching requirement

And the following stems:

- ``MType`` to filter by the `mtype` column of the node file(s)
- ``EType`` to filter by the `etype` column of the node file(s)
- ``SClass`` to filter by the synaptic classification of the cell
  (customarily either ``EXC`` or ``INH``)
- ``Region`` to filter by the `region` column of the node file(s)

The order of the rules matters, later rules may override earlier ones if
they are at least as specific as the earlier ones.
I.e., the number of wildcards matching all of an attribute needs to be less
or equal the rule to be overwritten.
For example, ``<rule fromMType="bar" …/>`` will be superseded by ``<rule
fromMType="b*" …?>`` as the constraints are similar, but it will not be
replaced by ``<rule fromMType="*" …/>``, as that one is broader.

In addition to the selection attributes, exactly one set of constraints have to
be used:

- ``mean_syns_connection``, ``stdev_syns_connection``, and ``active_fraction``
- ``bouton_reduction_factor``, ``cv_syns_connection``, and ``active_fraction``
- ``bouton_reduction_factor``, ``cv_syns_connection``, and ``mean_syns_connection``
- ``bouton_reduction_factor``, ``cv_syns_connection``, and ``probability``
- ``bouton_reduction_factor``, ``pMu_A``, and ``p_A``

Where the constraints signify:

.. _active_fraction:

- ``active_fraction``, the fraction of synapses to be removed in the third pruning step

.. _bouton_reduction_factor:

- ``bouton_reduction_factor``, the fraction of synapses to be removed in all three pruning steps

.. _cv_syns_connection:

- ``cv_syns_connection``, the target value for the coefficient of variation of the distribution of synapses per connection distribution of synapses per connections

.. _mean_syns_connection:

- ``mean_syns_connection``, the target value for the mean of the distribution of synapses per connections

.. _p_A:

- ``p_A``, the reduction factor

.. _pMu_A:

- ``pMu_A``, used as input to the survival rate

.. _probability:

- ``probability``, the target connection probability. To be deprecated.

.. _stdev_syns_connection:

- ``stdev_syns_connection``, the target value for the standard deviation of the distribution of synapses per connection

SynapsesProperties
~~~~~~~~~~~~~~~~~~

The list of `SynapsesProperties` is used to determine which property
classification is assigned to synapses. It takes the form::

    <SynapsesProperties>
        <synapse fromSClass="EXC" toSClass="EXC" type="E2" axonalConductionVelocity="0" />
        <synapse fromSClass="INH" toSClass="INH" type="I2" />
        <synapse fromSClass="EXC" toMType="L*_ChC" type="E2_PT" />
        <synapse fromMType="L6_MC" toMType="L6_IPC" toEType="*" type="I1_L6_MC-L6_IPC" />
    </SynapsesProperties>

Each element within the list of `SynapsesProperties` selects a connection
given by source and target cell selection criteria. Multiple selections are
possible:

- ``fromSClass`` to select the pre-synaptic cell class
- ``toSClass`` to select the post-synaptic cell class
- ``fromMType`` to select the pre-synaptic `mtype` type
- ``toMType`` to select the post-synaptic `mtype` type
- ``fromEType`` to select the pre-synaptic `etype` type
- ``toEType`` to select the post-synaptic `etype` type

In case selections overlap, the last specified assignment takes precedence.
To assign synapse properties, the classification field needs to be set:

- ``type`` a name that will be referenced by the
  `SynapsesClassification`_.

  .. note::

     The type has to start with either ``E`` for excitatory connections or
     ``I`` for inhibitory connections.  This legacy behavior may be overriden by
     specifying the `model_template` parameter for the `SynapsesClassification` section.

Two optional attributes may be set:

- ``neuralTransmitterReleaseDelay`` with a default of 0.1 ms
- ``axonalConductionVelocity`` with a default of 300 μm/ms

These two attributes may also be present in the ``SynapsesProperties``
element, setting default values for all ``synapse`` elements::

    <SynapsesProperties neuralTransmitterReleaseDelay="10.5" axonalConductionVelocity="123.0">

.. _recipe_properties:

SynapsesClassification
~~~~~~~~~~~~~~~~~~~~~~

Once a classification is assigned to connections, properties are assigned
to connections by using the `SynapsesClassification` section::

    <SynapsesClassification>
      <class id="E2"  gsyn="0.792" gsynSD="0.528" nsyn="5.00" nsynSD="2.00" dtc="1.74" dtcSD="0.18" u="0.50" uSD="0.02" d="671" dSD="17" f="017" fSD="5" nrrp="1" />
    </SynapsesClassification>

Here, the ``id`` field has to match a ``type`` value of the
`SynapsesProperties`. The properties are assigned using the following
random number distributions, using a mean `m` and standard deviation `sd`:

- A Gamma-distribution, with shape parameter equal to `m² / sd²`, and
  scale parameter equal to `sd² / m`.
- A truncated Normal-distribution, where values are redrawn until they are
  both positive and within the range of `m±sd`.
- A Poisson-distribution using only `m`.

The same drawn number is reused for all synapses within the same source to
target cell connection.

The following properties are supported, with the mean specified by the
property name, and the standard deviation by appending ``SD`` to the
property name:

- `gsyn`, the peak conductance (in nS) for a single synaptic contact, following a Gamma distribution
- `d`, time constant (in ms) for recovery from depression, following a Gamma distribution
- `f`, time constant (in ms) for recovery from facilitation, following a Gamma distribution
- `u`, utilization of synaptic efficacy, following a truncated Normal distribution
- `dtc`, decay time constant (in ms), following a truncated Normal distribution
- `nrrp`, number of vesicles in readily releasable pool, following a Poisson distribution

Truncated Normal distributions are limited to the central value ±σ and are
re-rolled until positive values has been obtained.

Three optional attributes can be specified, where each attribute will have to
be given for all `SynapsesClassification` elements:

- `gsynSRSF`, the scale factor for the conductance; `SRSF`: 'synaptic receptor scaling factor'
- `uHillCoefficient`, a coefficient describing the scaling of `u` to be
  done by the simulator:

  .. math::

     u_\text{final} = u \cdot y \cdot \frac{ca^4}{u_\text{Hill}^4 + ca^4}

  where :math:`ca` denotes the simulated calcium concentration in
  millimolar and :math:`y` a scalar such that at
  :math:`ca = 2.0:\ u_\text{final} = u`. (Markram et al., 2015)
- `model_template`, to specify the filename stub (without a final extension) that should
  appear in the field with the same name in the corresponding SONATA edge file.  Presence
  of this attribute will suppress creating the `syn_type_id` field in the edge file.

These attributes will be copied for each synapse corresponding to its
classification.  If they are not specified, no corresponding columns will
be created in the output.

SynapsesReposition
~~~~~~~~~~~~~~~~~~

The `SynapsesReposition` section allows to shift the post-synaptic side of
touches, e.g., for chandelier cells from the soma to the first axon
section::

    <SynapsesReposition>
        <shift fromMType="L*_CHC" toMType="*" type="AIS"/>
        <shift fromMType="SP_AA" toMType="*" type="AIS"/>
    </SynapsesReposition>

Allowed properties are:

- ``fromMType`` to select the pre-synaptic cell `mtype`
- ``toMType`` to select the post-synaptic cell `mtype`
- ``type`` for the kind of shift. Currently only ``AIS`` for shifts to the
  first axon section from the soma is supported.

Consumers and invocation order
------------------------------

- TouchDetector. Uses the following parts:
   - `StructuralSpineLengths`_
   - `InterBoutonInterval`_
- Spykfunc. Uses the following parts:
   - `Seeds`_
   - `InitialBoutonInterval`_, used by the `BoutonDistance` filter
   - `TouchRules`_, used by the similarly named filter (functional execution only)
   - `ConnectionRules`_, used by the filter `ReduceAndCut` (functional execution only)
   - `SynapsesProperties`_, used to assign synapses classification
   - `SynapsesClassification`_, used to assign synapses properties
   - `SynapsesReposition`_, used to shift post-synaptic segments away from
     the soma
