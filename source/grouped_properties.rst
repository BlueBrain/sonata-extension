.. _grouped_properties:

Grouped Properties Layout
=========================

Properties stored in the SONATA node files must be linear, i.e., there should be one property value per node id. However, there are cases where extra data needs to be stored where more than one values correspond to one node id. The grouped properties file layout allows storing multidimensional grouped properties, where each group corresponds to one id in the corresponding node population.

There are two mandatory groups in the root / :

- data/
- offsets/

Property values are stored in the ``data/`` group and may have multiple dimensions:

::

    /data/property1
    /data/property2
    .
    .
    .

If the property is `linear`, which means there is one value per node population id, then the dataset above can be indexed directly using the node id. There will be no additional `offsets` dataset in this case.

If the property assumes multiple values per node id (group), then an additional dataset will be present in the ``offsets/`` group with the same name as in ``data/``:

::

    /offsets/property1
    /offsets/property2
    .
    .
    .

For `N` groups, the ``/offsets/`` dataset will be an 1-D integer array of `N+1` values.

The data rows corresponding to the ``i-th`` node id can be retrieved by first obtaining the range from the ``(i, i+1)`` entries of the property dataset in ``offsets/``. The resulting ``(start_offset, end_offset)`` range determines the rows to extract from the property dataset in ``data/``.

Both `linear` and `grouped` properties can co-exist in the same file. However, if the `linear` properties are more relevant to the respective SONATA node or edge populations, please consider adding them there.
