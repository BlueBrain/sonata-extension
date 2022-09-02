.. _microdomains:

Astrocyte Microdomains Description
==================================

In biology, `astrocytic microdomains` are defined as the three-dimensional territories of astrocyte morphology. In circuit-building, `microdomains` are defined as a geometric abstraction that indicates the bounding region each astrocyte should occupy. This information is used throughout the NGV workflow to determine the potential synapses, vasculature sites, and soft boundaries within which astrocyte morphologies are grown. For the rest of this page, whenever the term ``microdomains`` is encountered it will refer to the circuit building geometrical abstraction, not the actual biological entities.

Each microdomain is a convex polygon, represented as a collection of points (vertices) linked together by triangles, and has access to its adjacent astrocytic neighbors.

The microdomains are properties of the :ref:`astrocytic node population<astrocyte_node_type>`. Therefore, there are as many microdomains as astrocytes in the circuit, and they are indexed by the respective astrocyte node id. However, in contrast to regular properties, microdomain information is grouped because there is more than one datum per astrocyte node id (e.g. the points of each domain). Therefore, the grouped properties file layout is used to store these properties. (See :ref:`here <grouped_properties>` for details)

.. table::

    ========== =================== ========== =========== ============================================================================================
    Group      Field               Type       Requirement Description
    ========== =================== ========== =========== ============================================================================================
    /data      points              float32    Mandatory   Positions (x, y, z) of the triangular domain vertices in µm.
    /data      triangle_data       int64      Mandatory   Polygon ids and triangles. Columns : (polygon_id, point_index_i, point_index_j, point_index_k).
    /data      neighbors           int64      Mandatory   Ids of either astrocytes (positive) or adjacent walls (negative).
    /data      scaling_factors     float64    Mandatory   Scaling factors that were used to uniformly scale the domain points to overlap.
    /offsets   points              int64      Mandatory   Ranges for the points dataset.
    /offsets   triangle_data       int64      Mandatory   Ranges for the triangle_data dataset.
    /offsets   neighbors           int64      Mandatory   Ranges for the neighbors dataset.
    ========== =================== ========== =========== ============================================================================================

Example data of a single microdomain:

.. code-block:: python

    points = [
        [-8.,  8., -7.],
        [78.,  7., -7.],
        [58., 78., 23.],
        [78., 78., -7.],
        [-8., 13.,  1.],
        [78., 39., 40.],
        [59., 78., -7.],
        [78., 78., 21.],
        [-8., 13., -7.],
        [16., 37., 47.],
        [44., 36., 45.],
        [78., 29., 34.]
    ]

    triangle_data = [
        [ 0,  1,  0,  4],
        [ 0,  1,  4,  9],
        [ 0,  1,  9, 10],
        [ 0,  1, 10, 11],
        [ 1,  1,  0,  8],
        [ 1,  1,  8,  6],
        [ 1,  1,  6,  3],
        [ 2,  1,  3,  7],
        [ 2,  1,  7,  5],
        [ 2,  1,  5, 11],
        [ 3,  7,  2,  9],
        [ 3,  7,  9, 10],
        [ 3,  7, 10,  5],
        [ 4,  6,  3,  7],
        [ 4,  6,  7,  2],
        [ 5,  8,  6,  2],
        [ 5,  8,  2,  9],
        [ 5,  8,  9,  4],
        [ 6,  4,  0,  8],
        [ 7,  5, 11, 10],
    ]

    neighbors = [ 3,  3,  3,  3, -5, -5, -5, -2, -2, -2,  0,  0,  0, -4, -4,  2,  2,
        2, -1,  4]

    scaling_factor = 1.1

Geometry
~~~~~~~~

A `microdomain` is a polygon mesh, comprised of triangles that are connected by their common edges or corners. This information is stored in ``/data/points`` and ``/data/triangle_data``, indexed by the respective ``/offsets/points`` and ``/offsets/triangle_data``.

The `triangle_data` dataset consists of 4 columns corresponding to `polygon_id`, followed by the triangle indices. Polygon ids allow reconstructing the polygonal face of each domain, which is stored as a collection of triangles with the same polygon id.

Connectivity
~~~~~~~~~~~~

The microdomains are calculated as a partition of the 3D space (tessellation) into convex polygons. Therefore, each microdomain is adjacent to either neighboring domains or bounding walls. The neighboring information is stored in the ``data/neighbors`` dataset, which is indexed by the respective offsets ``/offsets/neighbors`` dataset.

Positive ids stored corresponding to astrocytic node ids, and negative ones corresponding to adjacent walls respectively. A circuit hyperrectangle has six bounding faces or walls. Currently, the respective wall geometry to each negative id is not stored.

Scaling Factors
~~~~~~~~~~~~~~~

Microdomains are first calculated as a tessellation during building and are then scaled to slightly overlap, reproducing biological behavior. Only the scaled domains, which are used throughout the building workflow, are stored to file.

It is possible to reconstruct the regular tessellation by using the scaling factor used to scale each domain. The `scaling_factors` are stored in ``data/scaling_factors``. Note that there are no offsets for the `scaling_factors` because it's linear dataset with one value per domain.

The points of the regular microdomain before being scaled, can be reconstructed as follows:

``regular_points = (1 / scaling_factor) * (scaled_points - centroid) + centroid``

where ``scaled_points`` are the points stored in the specification described above, and ``centroid`` its the respective mean of these points.
