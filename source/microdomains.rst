.. _microdomains:

Astrocyte Microdomains Description
==================================

Microdomains are convex polygons representing the available bounding region for each astrocyte.
Each polygon is represented as a collection of points linked together via triangles.
In addition, each microdomain has access to its adjacent neighbors.
Their size is the same as the number of astrocytes, i.e. one per astrocyte.

The microdomains file has a total of 4 datasets.
Three of them (points, triangle_data, neighbors) contain information concerning the geometry of the domains their neighbors.
The offsets dataset contains three independent ranges, which specify the slices for each one of the three aforementioned datasets.

.. table::

    ========== =================== ========== =========== ============================================================================================
    Group      Field               Type       Requirement Description
    ========== =================== ========== =========== ============================================================================================
    /data      points              float32    Mandatory   Positions of the triangular mesh vertices in :math:`\mu m`
    /data      triangle_data       uint64     Mandatory   Polygon ids and triangles. Columns : (polygon_id, point_index_i, point_index_j, point_index_k)
    /data      neighbors           int64      Mandatory   Ids of either astrocytes (positive) or adjacent walls (negative)
    /          offsets             uint64     Mandatory   Ranges in the datasets above. Columns: (points_offsets, triangle_data_offsets, neighbors_offsets)
    ========== =================== ========== =========== ============================================================================================

More specifically, the ``/offsets`` dataset specify the ranges for all the datasets in ``/data``.
For instance, an astrocyte with a node id ``i`` will have a microdomain with a geometry of:

    * ``points[offsets[i, 0]: offsets[i+1, 0]]``
    * ``triangles[offsets[i, 1]: offsets[i+1, 1]]``
    * ``neighbors[offsets[i, 2]: offsets[i+1, 2]]``

Because each face of the microdomain is a polygon that has been triangulated in order to be stored as a collection of triangles, the ``polygon_id`` is also stored in ``triangle_data``.
Thus, the polygons can be reconstructed without finding coordinate overlaps.

The ``/data/neighbors`` dataset includes both positive indices corresponding to astrocytic node ids, and negative ones to adjacent walls.
A circuit hyperrectangle has six bounding faces or walls. Currently, the respective wall geometry to each negative id is not stored.

The ngv building outputs two microdomain files, the tessellation of the convex polygons and the same tessellation in which each domain has been uniformly scaled so that it overlaps with its neighbors.
Astrocytes do not form a tight mathematic tessellation, rather they form an overlapping region with their neighbors.
In the future these two files may be merged into one where the scaling factor is stored for each domain instead of replicating the datasets just for the scaling.
