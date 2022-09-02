.. _endfeet_meshes:

Astrocyte Endfeet Description
=============================

Astrocytes project branches that attach on the surface of the vasculature, wrapping around its surface, forming patches known as perivascular endfeet. Astrocytic endfeet are reconstructed during the ngv circuit building as two-dimensional triangulated surfaces. In order to approximate a three-dimensional object, a constant thickness is assigned to each two-dimensional endfoot surface.

The endfeet establish connections between astrocytes (glia) and the vasculature. Therefore, endfoot data is indexed by :ref:`endfoot edge ids<endfoot_edges>`, where more than one value (e.g. points, triangles) corresponds to each id. For this reason the grouped properties file layout is used to store the endfeet data (See :ref:`here <grouped_properties>` for more details).

.. table::

    ============= ============================= ========== =========== ============================================================================
    Group         Field                         Type       Requirement Description
    ============= ============================= ========== =========== ============================================================================
    /data         points                        float32    Mandatory   Positions (x, y, z) of the mesh vertices in µm
    /data         triangles                     int64      Mandatory   Triangular connectivity of the point vertices
    /data         surface_area                  float32    Mandatory   Surface area in µm²
    /data         surface_thickness             float32    Mandatory   Thickness in µm
    /data         unreduced_surface_area        float32    Mandatory   Surface area in µm² before reduction by the target distribution
    /offsets      points                        int64      Mandatory   Ranges for the points dataset
    /offsets      triangles                     int64      Mandatory   Ranges for the triangles dataset
    ============= ============================= ========== =========== ============================================================================

Geometry
~~~~~~~~

Perivascular endfeet are stored as 2D surfaces in the 3D space. Their discretized geometry consists of points (vertices) and triangles, forming triangular meshes. Given that biological endfeet have three-dimensional geometries, a surface thickness has been assigned to each endfoot to roughly approximate its extent along the normals of the 2D surface.

Surface Areas
~~~~~~~~~~~~~

During the endfeet surface generation stage in the NGV building workflow, the surface meshes are first grown competitively on the surface of the vasculature until there is no available space. These initial surface areas are stored as the property ``unreduced_surface_area``.

Then the mesh geometry is pruned, shrinking the endfeet, so that their surface area distribution matches the biological target distribution. The final surface areas are stored as ``surface_area`` and correspond to the surface area from the ``points`` and ``triangles`` stored in the file.

