.. _endfeet_area:

Endfeet Geometry Description
============================

The endfoot geometry consists of a 2-D triangular mesh that is generated along the surface of the vasculature.
For each endfoot, 1-D attributes are calculated during building.
The size the attributes is the same as the total number of endfeet and each positional index in the attribute array corresponds to the endfoot with ``endfoot_id``.

.. table::

    ============= ============================= ========== =========== ============================================================================
    Group         Field                         Type       Requirement Description
    ============= ============================= ========== =========== ============================================================================
    /attributes   surface_area                  float32    Mandatory   Surface area in :math:`\mu m^2`.
    /attributes   surface_thickness             float32    Mandatory   Thickness in :math:`\mu m`.
    /attributes   unreduced_surface_area        float32    Mandatory   Surface area in :math:`\mu m^2` before reduction by the target distribution.
    ============= ============================= ========== =========== ============================================================================

During the endfeet surface generation in the NGV building, the surface meshes are first grown competitively on the surface of the vasculature until there is no available space ``unreduced_surface_area``.
Then they are reduced so that the ``surface_area`` distribution matches the biological target distribution.
Each endfoot is also assigned a ``surface_thickness``, i.e. an extent along the normal of the vascular surface.

Endfeet meshes
~~~~~~~~~~~~~~

A triangular endfoot mesh is represented as ``points`` and ``triangles``, where each ``endfoot_id`` corresponds to a group ``/objects/endfoot_{endfoot_id}`` in the file.
Therefore, a total number of groups equal to the total number of endfeet is expected.

.. table::

    ============================== =============== ========== =========== ========================================================
    Group                          Field           Type       Requirement Description
    ============================== =============== ========== =========== ========================================================
    /objects/endfoot_{endfoot_id}  points          float32    Mandatory   Positions of the triangular mesh vertices :math:`\mu m`.
    /objects/endfoot_{endfoot_id}  triangles       float32    Mandatory   Triangular connectivity of the point ids above.
    ============================== =============== ========== =========== ========================================================

