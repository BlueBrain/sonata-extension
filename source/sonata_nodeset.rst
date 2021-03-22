.. _sonata_nodeset:
.. include:: <isonum.txt>

SONATA Node Sets
----------------
 TODO: this section should specify nodeset. This should not relate to bluepysnap as bluepysnap specifics should be in bluepysnap documentation.

In snap they are handled by the `NodeSets <https://github.com/BlueBrain/snap/blob/master/bluepysnap/node_sets.py>`_ class:

.. code-block:: python

   >> from bluepysnap.node_sets import NodeSets
   >> node_sets = NodeSets("node_sets_file.json")
   >> node_sets.resolved
   {
   'Excitatory': {'synapse_class': 'EXC'},
   }


The different node sets are defined inside the node sets file using different queries to select the
corresponding nodes.

In the example above, there is only one node set named ``"Excitatory"``.
This node set will select all the nodes with a field ``"synapse_class"`` equal to the
value: ``"EXC"`` (see also :ref:`here <sonata_tech>`).

You can have multiple node sets with selections based on all sonata fields:

.. code-block:: python

   >> node_sets.resolved
   {'Excitatory': {'synapse_class': 'EXC'}}
    'SLM_PPA': {'mtype': 'SLM_PPA'},
   }

and/or more complex node sets:

.. code-block:: python

   >> node_sets.resolved
   {'SLM_PPA_and_SP_PC': {'mtype': ['SLM_PPA', 'SP_PC']},
    'Excitatory_SLM_PPA': {'synapse_class': 'EXC', 'mtypes': 'SLM_PPA'}
   }

.. note:: Definitions:

  - a list means `or`: ``"SLM_PPA_and_SP_PC"`` |rarr| ``"mtype"`` == ``"SLM_PPA"`` **or** ``"SP_PC"``
  - a dictionary means `and`: ``"Excitatory_SLM_PPA"`` |rarr| ``"synapse_class"`` == ``"EXC"`` **and** ``"mtypes"`` ==  ``"SLM_PPA"``

Compounds
~~~~~~~~~

You can also combine the different node sets using "compounds" node sets. The implementation of the
compounds in snap is a `or` of all the node sets composing the compound.

.. code-block:: python

   >> node_sets.resolved
   {
   'SP_PC': {'mtype': 'SP_PC'},
   'cACpyr': {'etype': 'cACpyr'},
   'SP_PC_cACpyr': ['SP_PC', 'cACpyr']
   }

In this example, ``SP_PC_cACpyr`` means nodes with ``mtype`` equal to ``SP_PC`` **or**
``etype`` equal to ``cCpyr``.

.. warning::
    In the compounds, only lists of node sets are allowed. So you cannot combine a node set name with an
    additional query:

    .. code-block:: python

       >> node_sets.resolved
       {
       'SP_PC': {'mtype': 'SP_PC'},
       'cACpyr': {'etype': 'cACpyr'},
       'WRONG_COMPOUND': ['SP_PC', 'cACpyr', {'mtype'; 'SLM_PPA'}]
       }

    **is not correct**.


It is also possible to create compounds of compounds:

.. code-block:: python

   >> node_sets.resolved
   {
   'SLM_PPA': {'mtype': 'SLM_PPA'},
   'SP_PC': {'mtype': 'SP_PC'},
   'bAC': {'etype': 'bAC'},
   'cAC': {'etype': 'cAC'},
   'SLM_PPA_SP_PC': ['SP_PC', 'SLM_PPA'],
   'bAC_cAC': ['bAC', 'cAC'],
   'SLM_PPA_SP_PC_bAC_cAC': ['SLM_PPA_SP_PC', 'bAC_cAC']
   }

.. warning::
    If a node set name cannot be resolved, then the compound is not valid and an error is thrown.


Key "population"
~~~~~~~~~~~~~~~~

In addition, there are also two predefined keys one can use to select particular node_ids and
populations: ``population`` and ``node_id``.
This pre-defined key is used to select all nodes from a given population.

.. code-block:: python

    >> node_sets.resolved
    {
    'Hippocampus': {'population': 'hippocampus_neurons'},
    'Projection' :  {'population': 'projection_neurons'},
    'All': {'population': ['hippocampus_neurons', 'projection_neurons']}
    }

``Hippocampus`` will select all the nodes inside the ``hippocampus_neurons`` population.
``All`` selects all the nodes from the ``hippocampus_neurons`` and from the ``projection_neurons``.

Key "node_id"
~~~~~~~~~~~~~

This pre-defined key selects the ``node_ids`` to extract from the circuit.

.. code-block:: python

    >> node_sets.resolved
    {
    'Sample': {'node_id': [10, 11, 12, 13, 14, 15]},
    }

``Sample`` will select the nodes with the ``node_ids`` : ``[10, 11, 12, 13, 14, 15]``. This is important
to notice the node_ids are defined in a list so you can interpret this as a `or`.

If the ``"node_id"`` key is used alone, then the corresponding ``node_ids`` from all populations are
returned. If you want to select the ``node_ids`` from a single population only, you should
use the ``node_id`` in combination with the ``population`` key:

.. code-block:: python

    >> node_sets.resolved
    {
    'Sample': {'node_id': [10, 11, 12, 13, 14, 15]},
    'Hippocampus_sample': {'population': 'hippocampus_neurons',
                           'node_id': [10, 11, 12, 13, 14, 15]},
    }
    # ids is the snap function to access nodes from a population
    >>  circuit.nodes["hippocampus_neurons"].ids("Sample")
    [10, 11, 12]
    >> circuit.nodes["projection_neurons"].ids("Sample")
    [10, 11, 12]
    >> circuit.nodes["hippocampus_neurons"].ids("Hippocampus_sample")
    [10, 11, 12]
    >> circuit.nodes["projection_neurons"].ids("Hippocampus_sample")
    []
