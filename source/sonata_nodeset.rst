.. _sonata_nodeset:

SONATA Node Sets
----------------

Introduction
~~~~~~~~~~~~

The `SONATA Node Sets File <https://github.com/AllenInstitute/sonata/blob/master/docs/SONATA_DEVELOPER_GUIDE.md#node-sets-file>`_ is a way of declaratively specifying groups of nodes.
Instead of listing each GID as per the original *target* files, instead, attribute values in the *nodes* files can be used to match and create collections of nodes.

For example:

.. code-block:: js

   {
     "Excitatory": {"synapse_class": "EXC"}
   }

This will select all the nodes with the attribute ``synapse_class`` equal to the value: ``EXC`` (see also :ref:`here <sonata_tech>`).

The format of a node set file is:

.. code-block:: js

   {
     "Name": Expression,
     "AnotherName": AnotherExpression
   }

There is a containing dictionary with keys naming expressions, this key-value pair is considered a ``nodeset``.
The name is to be used like the *target name* in the old style target files.
Different node sets are defined inside the ``node sets file`` as per the above example.
This allows one name declare different queries.

The expression are broken down into ``simple`` and ``compound``.

Simple Expressions
~~~~~~~~~~~~~~~~~~

A ``simple`` expression names a desired attribute, or attributes, and the values that should match.

You can have multiple node sets with selections based on all sonata fields, like the Excitatory example above, or:

.. code-block:: js

   {
     "SLM_PPA": {"mtype": "SLM_PPA"}
   }

Simple expressions can also contain lists to match:

.. code-block:: js

   {
     "SLM_PPA_and_SP_PC": {"mtype": ["SLM_PPA", "SP_PC"]},
   }


.. note:: A list means `or`: ``SLM_PPA_and_SP_PC`` is interpreted as ``mtype`` == ``SLM_PPA`` **or** ``SP_PC``


They can also contain dictionaries:

.. code-block:: js

   {
     "Excitatory_SLM_PPA": {"synapse_class": "EXC", "mtypes": "SLM_PPA"}
   }

.. note:: A dictionary means `and`: ``Excitatory_SLM_PPA`` is interpreted as ``synapse_class`` == ``EXC`` **and** ``mtypes`` ==  ``SLM_PPA``

.. warning:
    This is an extension available in libsonata, and isn't covered by the SONATA specification

They can also contain simple expressions:

.. code-block:: js

   {
     "ALL_SP": {"mtype": {"$regex": "^SP_.*"}}
   }


The format is the *name of the desired attribute* as the key, and another dictionary as the value.
This dictionary is composed of a `operator` as the key, and the value is the what the operator uses.
In the above example, the `operator` is `$regex`, and the value is a regular expression `^SP_.*`

The available operators are:

======== =============== =====================
Operator Applicable Type Meaning
======== =============== =====================
$regex   String          `Regular Expression`_
$gt      Numeric         Greater than
$lt      Numeric         Less than
$gte     Numeric         Equal or greater than
$lte     Numeric         Equal or less than
======== =============== =====================


Compound Expressions
~~~~~~~~~~~~~~~~~~~~

One can also combine the different node sets using *compounds* node sets.

.. code-block:: js

   {
     "SP_PC": {"mtype": "SP_PC"},
     "cACpyr": {"etype": "cACpyr"},
     "SP_PC_cACpyr": ["SP_PC", "cACpyr"]
   }

In this example, ``SP_PC_cACpyr`` means nodes with ``mtype`` equal to ``SP_PC`` **or** ``etype`` equal to ``cCpyr``.

.. warning::
    In the compounds, only lists of node sets are allowed. So you cannot combine a node set name with an
    additional query:

    .. code-block:: js

       {
         "SP_PC": {"mtype": "SP_PC"},
         "cACpyr": {"etype": "cACpyr"},
         "WRONG_COMPOUND": ["SP_PC", "cACpyr", {"mtype"; "SLM_PPA"}]
       }

    **is not correct**.


It is also possible to create compounds of compounds:

.. code-block:: js

   >> node_sets.resolved
   {
     "SLM_PPA": {"mtype": "SLM_PPA"},
     "SP_PC": {"mtype": "SP_PC"},
     "bAC": {"etype": "bAC"},
     "cAC": {"etype": "cAC"},
     "SLM_PPA_SP_PC": ["SP_PC", "SLM_PPA"],
     "bAC_cAC": ["bAC", "cAC"],
     "SLM_PPA_SP_PC_bAC_cAC": ["SLM_PPA_SP_PC", "bAC_cAC"]
   }


Key "population"
~~~~~~~~~~~~~~~~

In addition, there are also two predefined keys one can use to select particular node_ids and populations: ``population`` and ``node_id``.
This pre-defined key is used to select all nodes from a given population.

.. code-block:: js

    {
      "Hippocampus": {"population": "hippocampus_neurons"},
      "Projection" :  {"population": "hippocampus_projections"},
      "All": {"population": ["hippocampus_neurons", "hippocampus_projections"]}
    }

``Hippocampus`` will select all the nodes inside the ``hippocampus_neurons`` population.
``All`` selects all the nodes from the ``hippocampus_neurons`` and from the ``hippocampus_projections``.

Key "node_id"
~~~~~~~~~~~~~

This pre-defined key selects the ``node_ids`` to extract from the circuit.

.. code-block:: js

    {
      "Sample": {"node_id": [10, 11, 12, 13, 14, 15]},
    }

``Sample`` will select the nodes with the ``node_ids`` : ``[10, 11, 12, 13, 14, 15]``.
This is important to notice the node_ids are defined in a list so you can interpret this as a ``or``.

If the ``node_id`` key is used alone, then the corresponding ``node_ids`` from all populations are returned.
If you want to select the ``node_ids`` from a single population only, you should use the ``node_id`` in combination with the ``population`` key:

.. code-block:: js

    {
      "Sample": {"node_id": [10, 11, 12, 13, 14, 15]},
      "Hippocampus_sample": {"population": "hippocampus_neurons",
                             "node_id": [10, 11, 12, 13, 14, 15]},
    }

.. _`Regular Expression`: https://262.ecma-international.org/5.1/#sec-15.10
