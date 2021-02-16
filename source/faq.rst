.. _faq:

Frequently Asked Questions
==========================

How are synapses locations addressed?
-------------------------------------

There are two representations of synapse locations, which can be distinguished by whether they are a triplet or a tuple.
The necessary nomenclature is 'section' and 'segment', displayed in this diagram:

.. image:: _static/section_segment.svg

A section is thus the neurite between two branch points, which can be made up of multiple segments.
The segments are the straight conical frustums that model the morphologies.

With that, the two representations are:

``(section_id, segment_id, offset)``
   Where:

   - `section_id` is how NEURON identifies the section
   - `segment_id` is the nth segment in that section
   - `offset` is the distance, in um, along the addressed segment


``(section_id, offset)``
   Where:

   - ``section_id`` is how NEURON identifies the section
   - ``offset`` is the normalized distance (0, 1] along the section; ie: the fraction of the distance computed by summing all sections

   The morph-tool_ utility can be helpful to load morphologies, and calculate the `section_id` that NEURON expects.

   .. _morph-tool: https://bbpteam.epfl.ch/documentation/projects/morph-tool/latest/index.html


Why doesn't SONATA have global ids?
-----------------------------------

Not having global IDs in SONATA was a concious decision.
One of the goals of SONATA was to make composition easier: if there are global ids, there may be collisions, thus they were not added.

As it stands, the ``(population_name, node_id)`` are globally unique, and should be used to identify cells.
Relying on other IDs may make using reports, simulators, etc harder.

SNAP handles it like this, as described `here <https://github.com/BlueBrain/snap/commit/c211d79ccc01bf2b0dcc621d12a5bba054a03ff7>`_.


What do I do about a 'missing the 'node_population' attribute' errors?
----------------------------------------------------------------------

Depending on the vintage of your circuit edge files, it's possible they don't conform exactly to the SONATA spec.
Once can fix this error by setting the attributes to the correct values.

For instance, with python and h5py:

.. code-block:: python

   with h5py.File(..., 'r+') as h5:
       h5['/edges/$edge_population/source_node_id'].attrs['node_population'] = '$related_source_population_name'
       h5['/edges/$edge_population/target_node_id'].attrs['node_population'] = '$related_target_population_name'


Where `$edge_population` is the name HDF5 dataset, and the `$related_source_population_name` and `$related_target_population_name` are the names of the source and target populations in the `nodes.h5` file.
