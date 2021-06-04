:orphan:

usecase 3
=========

.. image:: _static/usecase3.svg
   :align: center

This usecase 3 is 2 populations of biophysical neurons in 2 separate files with chemical synapses between neurons of their population and the other population.

circuit configuration
---------------------
.. include:: usecases/usecase3/circuit_sonata.json
   :literal:


node files
----------

node population A
^^^^^^^^^^^^^^^^^

.. include:: usecases/usecase3/nodes_A.h5.txt
   :literal:

node population B
^^^^^^^^^^^^^^^^^

.. include:: usecases/usecase3/nodes_B.h5.txt
   :literal:

edge files
----------

edges between the biophysical neurons of nodes_A
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. include:: usecases/usecase3/local_edges_A.h5.txt
   :literal:

edges between the biophysical neurons of nodes_B
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. include:: usecases/usecase3/local_edges_B.h5.txt
   :literal:

edges between the 2 populations A and B
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. include:: usecases/usecase3/edges_AB.h5.txt
   :literal:

reports
-------

simulation config used (report section only)

.. include:: usecases/usecase3/simulation_sonata.json
   :literal:

spike report
^^^^^^^^^^^^

.. include:: usecases/usecase3/reporting/spikes.h5.txt
   :literal:


soma report
^^^^^^^^^^^

.. include:: usecases/usecase3/reporting/soma_report.h5.txt
   :literal:

compartment report
^^^^^^^^^^^^^^^^^^

.. include:: usecases/usecase3/reporting/compartment_report.h5.txt
   :literal:
