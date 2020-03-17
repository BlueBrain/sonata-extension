.. _mvd2:

MVD version 2
=============
The circuit.mvd2 file contains metadata regarding the cells in the network and
minicolumn metadata

File Format
-----------

Anything starting with # is a comment
The first 2 lines after the comments at the begining of the mvd2 file are
reserved for TBD.

No counts are given. Parsing is done by reading rows after a given section
label until a different section label is encountered.
Section labels: 'Neurons Loaded', 'MicroBox Data', 'MiniColumnsPosition',
'CircuitSeeds', 'MorphTypes', 'ElectoTypes'

Neurons Loaded
~~~~~~~~~~~~~~

::

    morphology name (string). The name of the morphology file without the extension
    database type (int). useless ?
    hyperColumn (int)
    miniColumn (int)
    layer (int)
    morphology type [index into MorphTypes below] (int)
    electrophysiology type [index into ElectroTypes below] (int)
    neuronCenter[0] (float)
    neuronCenter[1] (float)
    neuronCenter[2] (float)
    neuronRotation[1] (float). The Y axis rotation.
    metype (string). The name of the hoc file without extension.

MicroBox Data
~~~~~~~~~~~~~

:: 

    Column Size x coordinates (float)
    Column Size y coordinates (float)
    Column Size z coordinates (float)
    Layer 6 percentage in the column (float)
    Layer 5 percentage in the column (float)
    Layer 4 percentage in the column (float)
    Layer 3 percentage in the column (float)
    Layer 2 percentage in the column (float)

MiniColumnsPosition
~~~~~~~~~~~~~~~~~~~
::

    X coordinates (float)
    Y coordinates (float)
    Z coordinates (float)

CircuitSeeds
~~~~~~~~~~~~

::

    RecipeSeed (float)
    ColumnSeed (float)
    SynapseSeed (float)

MorphTypes
~~~~~~~~~~

::

    MorphologyName (string)
    PYR/INT (float)
    EXC/INH (float)

ElectoTypes
~~~~~~~~~~~

::

    ElectrophysiologyName (float)

Consumers
---------

- TouchDetector_. Required fields are positions, orientations, morphology
- Functionalizer_. Required fields are positions, orientations, morphology,
  etype, mtype, synapse_class

.. _TouchDetector: https://collab.humanbrainproject.eu/#/collab/161/nav/2979
.. _Functionalizer: https://collab.humanbrainproject.eu/#/collab/161/nav/2980
