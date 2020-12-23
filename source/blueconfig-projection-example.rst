.. _projection-example:

BlueConfig Projection example
=============================
How to properly add a Projection to a BlueConfig


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
        SpikeFile /path/to/spikes_file/
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

How to generate a spikes file for Projection

.. code:: python

    def generate_spike_file():
        import random
        import numpy as np
        from bluepy.v2 import Circuit
        SIMULATION_TIME = 2000  # 2 seconds, update it for your simulation

        def _gen_single_poisson_process():
            process = []
            t = 0
            while True:
                t += random.expovariate(.5) * 1000
                if t > SIMULATION_TIME:
                    return process
                process.append(t)

        c = Circuit('BlueConfig')
        proj_gids = c.cells.ids('Name_Of_Projection')
        # there are 310 fibers per mc column in the O1.v5
        assert (len(proj_gids) / 7. == 310.)
        gids = np.arange(proj_gids[0] + 2 * 310, proj_gids[0] + 3 * 310)

        spike_times = {}
        for gid in gids:
            spike_times[gid] = _gen_single_poisson_process()

        lines = []
        for gid, times in spike_times.items():
            for t in times:
                lines.append(f'{gid} {t}\n')

        with open('/path/to/spikes_file/', 'w') as f:
            f.writelines(lines)


    generate_spike_file()
