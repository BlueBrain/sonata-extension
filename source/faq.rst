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
