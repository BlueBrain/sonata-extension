.. _report:

SONATA reports
==============

The goal of this document is to clarify the specification with respect to BBP needs.
The original report documentation is `located here <https://github.com/AllenInstitute/sonata/blob/master/docs/SONATA_DEVELOPER_GUIDE.md#output-file-formats>`_

Spike file
----------

Spikes are currently supported on the following model_type: ``biophysical``, ``point_neuron``.

.. table::

    ========================== ================== ========== ============= =========================================================================================
    Group                      Field              Type       Requirement   Description
    ========================== ================== ========== ============= =========================================================================================
    /spikes/{population_name}  timestamps         float64    Mandatory     The time when the spike is happening.
                                                                           Units is defined by the ``units`` attribute.
    /spikes/{population_name}  node_ids           uint64     Mandatory     The node id of the cell spiking
    ========================== ================== ========== ============= =========================================================================================

The population_name group has an HDF5 attribute ``sorting``.
Possible values are ``none``, ``by_id``, ``by_time``, note that this is an `HDF5 enum: <https://support.hdfgroup.org/HDF5/doc/H5.user/DatatypesEnum.html>`_
The default order is ``by_time``.

The i-th value of timestamps is a spike of the i-th node id cell in node_ids.

The ``timestamps`` dataset has a ``units`` attribute defining the unit of the timestamp.
Only ``ms`` is supported.


Frame oriented, element recordings
----------------------------------

Compartment report
^^^^^^^^^^^^^^^^^^

.. table::

    =================================== ================== ========== ============= =========================================================================================
    Group                               Field              Type       Requirement   Description
    =================================== ================== ========== ============= =========================================================================================
    /report/{population_name}           data               float32    Mandatory     The reported values.
                                                                                    Units is defined by the ``units`` attribute.
    /report/{population_name}/mapping   node_ids           uint64     Mandatory     The set of node ids (no duplicate).
    /report/{population_name}/mapping   index_pointers     uint64     Mandatory     The offset for each node in the data field.
    /report/{population_name}/mapping   element_ids        uint32     Mandatory     Represent the compartments as in NEURON, ordered
                                                                                    by compartment IDs and grouped by nodes.
                                                                                    For the 'lfp' report type, it represent the electrode IDs.
    /report/{population_name}/mapping   time               float64    Mandatory     3 values defining start time, end time, and time step.
                                                                                    end time is not part of the report.
    =================================== ================== ========== ============= =========================================================================================

For a node node_ids[i], the data for all the recorded elements is determined by data[index_pointer[i]: index_pointer[i + 1]].
Therefore the length of index_pointer is the length of node_ids + 1 (as opposed to the shape define in the SONATA repository)

``element_pos`` has mentioned in the SONATA paper is not supported at BBP.

The ``data`` field has a hdf5 attribute ``units`` of type string.
Hardcoded to ``mV`` for now at the BBP.

The ``node_ids`` field has an optional hdf5 attribute ``sorted`` of type uint8 (different from SONATA spec).
Default is 0 for not sorted.
This field is not implemented.

The ``time`` field has a property ``units`` of type string.
Hardcoded to ``ms``.


Soma report
^^^^^^^^^^^

"Soma" report is a special case of compartment report where only the values for 1 compartment of the cell are reported. It can be reported at the soma or in the axon initial segment (AIS) depending on the configuration. In the case of multiple compartments for the soma or the axon, the one in the middle is used (as the split is an odd number).
The element_ids are always 0.

Summation report
^^^^^^^^^^^^^^^^

Summation report is similar to a compartment report. It usually reports a membrane current in nA (although the ``units`` field says mV).

Synapse report
^^^^^^^^^^^^^^

In that case, the element_ids are the synapse ids with no particular order / grouping.
The node_ids are the one of the post synaptic cells.

LFP report
^^^^^^^^^^

In this case, the element_ids are the electrode ids described in the electrodes_file :ref:`here <sonata_tech>`.

Bloodflow report
^^^^^^^^^^^^^^^^

A particular type of compartment report for ``vasculature`` nodes. It is actually a set of 3 report files that store for each time-step 3 values per segment of the vasculature:

* radius (unit: µm)
* blood pressure (unit: µm^3.s^-1)
* blood flow (unit: g.µm^-1.s^-2)


Extracellular report
--------------------

Not supported.
