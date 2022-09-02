.. circuit documentation master file, created by
   sphinx-quickstart on Mon Jun 29 10:27:08 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Circuit and simulation files format documentation
=================================================

This documentation covers circuit and simulation related file format used at Blue Brain. It is an extension to the SONATA format as described per `<http://dx.doi.org/10.1371/journal.pcbi.1007696>`_

As the Blue Brain Project aims at reconstructing the entire mouse brain this format has been extended to support:

- vasculature models
- glial cell models
- glia to glia cell connectivity
- tripartite neuroglial connectivity
- gliovascular connectivity
- neuromodulatory projections
- plasticity
- gap junctions

In addition, this documentation covers all the properties used by models delivered by the Blue Brain Project in more details compared to the original publication. Some technical extension have been added to improve composability of network models (model being built separately and assembled later).

The definition of the various stimuli and reports supported by Neuron and CoreNeuron are covered as well in more details than the original publication.

The reference implementation to load data for this extension is provided by `libsonata <https://github.com/BlueBrain/libsonata>`_

.. toctree::
   :hidden:

   Home <self>
   blueconfig
   blueconfig-projection-example
   circuit_files
   recipe
   sonata
   NGV
   faq
   legacy

