# sonata-extension

This documentation covers circuit and simulation related file format used at blue brain. This documentation is an extension to the SONATA format as described per http://dx.doi.org/10.1371/journal.pcbi.1007696

Blue Brain Project aims at reconstructing the entire mouse brain. The format has been extended to support:

- vasculature models
- glial cell models
- glia to glia cell connectivity
- tripartite neuroglial connectivity
- gliovascular connectivity
- neuromodulatory projections
- plasticity
- gap junctions

In addition, this documentation covers in more details than the original publication all the properties used by models delivered by Blue Brain Project. Some technical extension have been added to improve composability of network models (model being built separately and assembled later).

The definition of the various stimuli and reports supported by Neuron and CoreNeuron are covered too in more details than the original publication.

The reference implementation to load data for this extension is provided by [links libsonata](links https://github.com/BlueBrain/libsonata)

## How-to:

- To update the documentation, update the rst files located in the source directory.
- To update the version number, modify the "version" entry in package.json.
- To build locally the documentation, just run `tox -e docs`.


## Examples

## Funding & Acknowledgement

The development of this software was supported by funding to the Blue Brain Project, a research center of the École polytechnique fédérale de Lausanne (EPFL), from the Swiss government’s ETH Board of the Swiss Federal Institutes of Technology.

Copyright (c) 2022 Blue Brain Project/EPFL
