.. _projection-example:

BlueConfig Projections and Replay
=================================

Adding a Projection to a BlueConfig
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specifying projections in a BlueConfig is done via a "Projection" block.

Frequently one wants to attach a Spike Replay to the projection, so that the spikes
originating in another brain region, previously simulated, can be used as input to the
current target region being simulated.

Spike replay files are commonly named "input.dat", after a rename of the "out.dat" file.


.. code::

    Projection NewProjection
    {
        Path /path/projection/file
        Source Name_Of_Projection
    }

    Stimulus spikeReplay
    {
        Mode Current
        Delay 0.0
        Duration 2000
        Pattern SynapseReplay
        # this file contains spike times of neurons from Name_Of_Projection, you must
        # generate it on your own, see an example below
        SpikeFile /path/to/spikes_file.dat
    }

    StimulusInject spikeReplayIntoUniverse
    {
        Stimulus spikeReplay
        Target Mosaic
    }

    Connection scheme_External
    {
        Source Name_Of_Projection
        Destination Mosaic
        SynapseConfigure %s.Use = 0.86
    }



.dat Spike Files
~~~~~~~~~~~~~~~~

Spike files used with BlueConfigs follow a very simple ".dat" text spec.
They have a `/scatter` header followed by lines of "<time-ms>  <cell-id>".

Example:

```
/scatter
015.7384     221086
015.8529     222256
015.8538     221131
015.8726     221285
```

**NOTE**: The <cell-id> is a 1-based NEURON cell Id, which is consistent
with legacy MVD formats.

Example Generating a .dat Spikes File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    def generate_spike_file(spike_file_path):
        import random
        import numpy as np
        from bluepy.v2 import Circuit
        SIMULATION_TIME = 2000  # 2 seconds, update it for your simulation

        def _gen_single_poisson_process():
            t = 0
            while t < SIMULATION_TIME:
                t += random.expovariate(.5) * 1000
                yield t

        c = Circuit('BlueConfig')
        proj_gids = c.cells.ids('Name_Of_Projection')
        # there are 310 fibers per mc column in the O1.v5
        assert (len(proj_gids) / 7. == 310.)
        gids = np.arange(proj_gids[0] + 2 * 310, proj_gids[0] + 3 * 310)

        with open(spike_file_path, 'w') as f:
            f.write(f'/scatter\n')
            for gid in gids:
                for t in  _gen_single_poisson_process():
                    f.write(f'{t} \t{gid}\n')


    generate_spike_file("/path/to/spikes_file.dat")
