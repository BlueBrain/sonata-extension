.. _recipe:

Recipe Description
==================

.. highlight:: xml

TODO
----

 - Exact definition of `mtype`
 - Exact definition of `etype`

History
-------

Objective
---------

Specify all parameters required to generate the connectome of a circuit.

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
        <touchRule fromLayer="*" fromMType="*PC" toLayer="*" toMType="*" type="soma" />
        <touchRule fromLayer="*" fromMType="*PC" toLayer="*" toMType="*" type="dendrite" />
    </TouchRules>

where ``*`` denotes a wildcard to match anything. In this example, touches
are allowed between all layers, but only originating from cells with
`mtype` ending in ``PC``. The former rule matches all synapses with a soma
on the post-synaptic side, while the latter matches with a dendrite on the
post-synaptic side.

Allowed parameters:

 - ``fromLayer`` the layer of the pre-synaptic cell (*to be deprecated*)
 - ``toLayer`` the layer of the post-synaptic cell (*to be deprecated*)

 - ``fromMType`` the `mtype` of the pre-synaptic cell
 - ``toMType`` the `mtype` of the post-synaptic cell

 - ``type`` the classification of the post-synaptic branch. May be one of
   the following:

    - ``*`` to match all branches
    - ``soma`` to match the soma
    - ``dendrite`` to match all dendrites
    - ``basal`` for basal dendrites
    - ``apical`` for apical dendrites

ConnectionRules
~~~~~~~~~~~~~~~

These rules determine the distribution of synapses. They may take the
following form::

    <ConnectionRules>
      <mTypeRule from="L1_NGC-DA" to="*" bouton_reduction_factor= "0.114" active_fraction= "0.50" cv_syns_connection= "0.25" />
      <mTypeRule from="L1_HAC" to="*" bouton_reduction_factor= "0.13" active_fraction= "0.50" cv_syns_connection= "0.25" />
    </ConnectionRules>

Allowed rule classes:

 - ``mTypeRule`` to apply rules between `mtype`
 - ``sClassRule`` to apply rules between synapse classes
 - ``layerRule`` to apply rules between layers (*to be deprecated*)

Properties:

 - ``from`` the pre-synaptic matching requirement
 - ``to`` the post-synaptic matching requirement

 - ``bouton_reduction_factor``
 - ``active_fraction``

 - ``cv_syns_connection``
 - ``mean_syns_connection``
 - ``stdev_syns_connection``

 - ``probability``

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
      ``I`` for inhibitory connections.

Two optional attributes may be set:

 - ``neuralTransmitterReleaseDelay`` with a default of 0.1
 - ``axonalConductionVelocity`` with a default of 300 m/s

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

 - `gsyn`, following a Gamma distribution
 - `d`, following a Gamma distribution
 - `f`, following a Gamma distribution
 - `u`, following a truncated Normal distribution
 - `dtc`, following a truncated Normal distribution
 - `nrrp`, following a Poisson distribution

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

    - `StructuralType` or any other entity with the attributes

        - `id` to describe the `mtype` 
        - `spineLength` given in μm to increase the overlap detection
          radius for both basal and apical dendrites.

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
