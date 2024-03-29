.. _mvd3:

MVD version 3
=============

.. warning:: This file format is deprecated and has been superseded by the SONATA
             :ref:`node_file`.

History
-------

The `MVD` version 2 files are text based files that contain the properties of the
neurons in a circuit.  It doesn't support 3 dimensional rotations of
morphologies, and thus cannot be used for anatomically realistic circuits. The
`MVD` version 3 format should be able to handle these circuits and allow for
larger circuits. In addition, a structured file format is required, to reduce
the need to parse string data formats, and to preserve numbers without having
to rely on string conversion routines and differences.

Objective
---------
The format must be extensible as we foreseen the appearance of new fields
beyond the current classifications of cells.

File Format
-----------

Fields
~~~~~~

The file represents a description of a group of cells. It contains, for each
cell, the values of a set of properties or fields.

.. note:: **No field is mandatory and new ones may be added in the future.** The
 container API provides a way to query the presence or absence of fields.

The following is a list of all of the known fields used in the current pipeline
by different tools:

- position: X, Y, Z, stored as 3 floats. The unit is micrometer.
- orientation: A *unit* quaternion, X Y Z W stored as 4 floats.
- etype: electrical type.
- mtype: morphological type.
- synapse_class: inhibitory/excitatory.
- morphology: morphology name (i.e. the `.h5` or `.asc` filename without
  the extension).
- exc_mini_frequency: mini-frequency of a cell in response to an incoming excitatory
  connection, with a value that depends on the receiving cell's layer.
- inh_mini_frequency: mini-frequency of a cell in response to an incoming inhibitory
  connection, with a value that is constant across all layers.

Additional fields can be added (optionals) as static parameters for the circuit generation.
These parameters are located under the group `/circuit` (e.g `/circuit/seeds` )

Container
~~~~~~~~~
`MVD3` uses `HDF5` as the structured data container. It is the `HPC` standard for
saving data, and there are libraries for accessing it with C++ and Python.
Floating-point numeric properties (like position and orientation) are stored
as individual datasets under `/cells/*`.
Text-based properties where most of the entires will be duplicated (like
`etype`, `mtype` and `synapse_class`) are stored as two datasets:

- One containing the list of all unique used values under `/library/*`
- One containing an index into the first one for each cell under
   `/cells/properties/*`

.. note:: String types are currently encoded as variable length UTF-8
    (H5T_CSET_UTF8 in `HDF5`)

`version` is an attribute defining major and minor version of the format.
`format` is a string attribute defining the format itself.

The following is an example of the structure of an `HDF5` containing all known
cell properties:

::

/                                       Group                            DataType
/version                                Attribute. value being [3, 0]    (an array with [mayor, minor])
/format                                 Attribute. value being "MVD"     (vlen string)
/circuit                                Group
/circuit/seeds                          Dataset {4}                      double float
/cells                                  Group
/cells/orientations                     Dataset {N, 4}                   double float
/cells/positions                        Dataset {N, 3}                   double float
/cells/properties                       Group
/cells/properties/etype                 Dataset {N}                      unsigned int
/cells/properties/morphology            Dataset {N}                      unsigned int
/cells/properties/mtype                 Dataset {N}                      unsigned int
/cells/properties/synapse_class         Dataset {N}                      unsigned int
/cells/properties/exc_mini_frequency    Dataset {N}                      double float
/cells/properties/inh_mini_frequency    Dataset {N}                      double float
/library                                Group
/library/etype                          Dataset {E}                      vlen string
/library/morphology                     Dataset {M}                      vlen string
/library/mtype                          Dataset {T}                      vlen string
/library/synapse_class                  Dataset {S}                      vlen string



Where the cardinality is::

    N - number of cells.
    M - number of unique morphologies.
    E - number of unique e-types.
    T - number of unique m-types.
    S - number of unique synapse classes.

To which can be added the following optional circuit parameters::

    /circuit                        Group
    /circuit/seeds                  Dataset {1,4} (double float)

Consumers
---------

- TouchDetector. Required fields are positions, orientations, morphology
- Functionalizer. Required fields are positions, orientations, morphology
  etype, mtype, synapse_class
- Brion.
- Neurodamus.  Required fields are exc_mini_frequency, inh_mini_frequency, mtype
