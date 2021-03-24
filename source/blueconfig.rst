BlueConfig File Format
======================

Objective
---------

`BlueConfigs` are text files used for storing circuit and simulation parameters,
(like stimulus injection and simulation output), and paths to files (like
morphologies, models).

History
-------

Has been around since at least 2007


File Format
-----------

The general structure is a C-like braced system.  The config file contains one
or more configuration `Sections`, that have a `Type`, and a `Name`.
Within an entry, there are multiple key value pairs: the key is a series of
ASCII characters, followed by whitespace.  These are called `Values`

::

  Type0 Name0                 |         |
  {                           |         |
      key0 value0   | Value   | Section |
      key1 value1             |         |
  }                           |         |
  Type1 Name1                           | File
  {                                     |
      key0 value0                       |
      key1 value1                       |
  }                                     |


.. note:: Names can currently be reused for multiple stanzas.

.. note:: Commenting out the `Type Name` comments out the following block.  EX:

    ::

        #Foo Bar
        {
          #Nothing in here is used
        }

Section Types
-------------

The following section types are defined for BlueConfigs.  The authoritative
parser lives in
Neurodamus `here. <https://bbpcode.epfl.ch/browse/code/sim/neurodamus/bbp/tree/lib/hoclib/ConfigParser.hoc?h=HEAD>`_

.. blueconfig_section_index::


.. blueconfig_section:: Run
    :description:
     Defines the versioning, data sources, and simulation-wide parameters

    .. blueconfig_value:: ForwardSkip
        :type: int
        :required: False
        :unit:
        :description:
         Run without Stimulus or Reports for a given duration using a large
         timestep. This is to get the cells past any initial transience.

    .. blueconfig_value:: CurrentDir
        :type: abspath
        :required: False
        :unit:
        :description:
         | Simulation execution directory. Will be prepended to other Run parameters if they do not use an absolute path: E.g.: OutputRoot, TargetFile. 
         | Default value: Path to BlueConfig
         | NOTE: Relative paths are not allowed, the only exception being "." strictly for test jobs.

    .. blueconfig_value:: Restore
        :type: string
        :required: False
        :unit:
        :description:
         Restore the state of the simulation saved in the provided file/directory.

    .. blueconfig_value:: MeshPath
        :type: abspath
        :required: False
        :unit:
        :description:
         Location of mesh files for 3D visualization

    .. blueconfig_value:: NumBonusFiles
        :type: int
        :required: False
        :unit:
        :description:
         Temporary support for allowing synapses from external sources (e.g.
         Thalamocortical input). Superseded by Projection section

    .. blueconfig_value:: TargetFile
        :type: path
        :required: True
        :unit:
        :description:
         Parameter giving location of custom user targets stored in the named
         file, referred to as user.target in the remainder of the document. The
         file contains descriptions for Cell/Compartment/Section targets. Use of
         relative paths is discouraged and DEPRECATED, unless CurrentDir is also set.

    .. blueconfig_value:: Note
        :type: string
        :required: False
        :unit:
        :description:
         Description field for adding details about the simulation. Recommended
         topics might be purpose of the sim, changes from other sims, paper
         references if trying to duplicate experiments, etc.

    .. blueconfig_value:: Duration
        :type: float
        :required: True
        :unit: ms
        :description:
         Simulation duration

    .. blueconfig_value:: Version
        :type: string
        :required: False
        :unit:
        :description:
         Revision number of bglib to take from git/svn

    .. blueconfig_value:: OutputRoot
        :type: abspath
        :required: True
        :unit:
        :description:
         Location where output files should be written, namely spikes and reports.
         Prefer using absolute paths. Relative paths are interpreted relative to CurrentDir.

    .. blueconfig_value:: Time
        :type: time
        :required: False
        :unit:
        :description:
         Time of config creation/modification with format hh:mm:ss

    .. blueconfig_value:: RNGMode
        :type: string
        :required: False
        :unit:
        :description:
         Random number generator used for simulation : MCellRan4 (default) or Random123

    .. blueconfig_value:: Simulator
        :type: string
        :required: False
        :unit:
        :description:
         Simulator engine used for execution : NEURON (default) or CORENEURON

    .. blueconfig_value:: ModelBuildingSteps
        :type: int
        :required: False
        :unit:
        :description:
         Number of steps used by NEURON to construct a model. If a given network model
         can not be loaded into memory, NEURON can divide a model into smaller pieces
         and then pass all pieces to CORENEURON for simulation. For example, with given
         number of compute nodes if NEURON can only simulate half of the model (due to
         limited memory), ModelBuildingSteps can be set to 2.

    .. blueconfig_value:: KeepModelData
        :type: string
        :required: False
        :unit:
        :description:
         Keep the CORENEURON model data if this parameter is set to True.
         By default, the CORENEURON model data is deleted after simulation except for
         the save/restore process.

    .. blueconfig_value:: gitPath
        :type: string
        :required: False
        :unit:
        :description:
         URL from where bglib simulation files can be downloaded

    .. blueconfig_value:: ElectrodesPath
        :type: abspath
        :required: False
        :unit:
        :description:
         File path

    .. blueconfig_value:: METypePath
        :type: abspath
        :required: True
        :unit:
        :description:
         Location of metypes or CCells, the files defining morphological and
         electrical combinations used by the simulation.

    .. blueconfig_value:: MorphologyPath
        :type: abspath
        :required: True
        :unit:
        :description:
         Location of morphology files. If MorphologyType is not specified,
         '/ascii' is automatically appended to the path and morphology loading
         assumes 'asc' type (legacy handling).

    .. blueconfig_value:: MorphologyType
        :type: string
        :required: False
        :unit:
        :description:
         Type of morphology files. This is required if you wish to specify the
         morphology type (asc, swc, h5, hoc). NOTE: if this option is set, then
         MorphologyPath is not suffixed with '/ascii' anymore. For example:
          MorphologyPath /path/to/swc/v1
          MorphologyType swc


    .. blueconfig_value:: Save
        :type: path
        :required: False
        :unit:
        :description:
         name of the file or directory where the state of the simulation will be stored
         after a duration of "Time".

    .. blueconfig_value:: BioName
        :type: string
        :required: False
        :unit:
        :description:

    .. blueconfig_value:: CircuitPath
        :type: abspath
        :required: False
        :unit:
        :description:
         Root location of the circuit, where start.target and cell geometry info
         (MVD / SONATA nodes) should be found.

    .. blueconfig_value:: CellLibraryFile
        :type: string
        :required: False
        :unit:
        :description:
         Specify the file containing cell geometry info. Default is start.ncs.
         "start.ncs" is searched within nrnPath, "circuit.mvd3" within CircuitPath. Any other value
         is interpreted as a path to a format readable by MVDtool, namely SONATA nodes.

    .. blueconfig_value:: BaseSeed
        :type: int
        :required: False
        :unit:
        :description:
         For random sequences, the BaseSeed is added in order to give the user
         the capacity to change the sequences.

    .. blueconfig_value:: nrnPath
        :type: abspath
        :required: True
        :unit:
        :description:
         | Location of connectvity file(s): SONATA Edges or older Syn2, Nrn formats.
         | Option: specify a population name after the path, format "path:population".
         | NOTES:
         |  - For compat reasons, users can provide a path to a folder, in which case it will look for SONATA files, followed by syn2 and nrn. Such usage is DEPRECATED and file paths should be used.
         |  - DEPRECATED: Having start.ncs or start.target in this location.
         |    They should be within CircuitPath instead.

    .. blueconfig_value:: RunMode
        :type: RunMode
        :required: False
        :unit:
        :description:
         Optional parameter which currently accepts WholeCell and LoadBalance
         as a valid values. Neurons will be distributed round-robin, otherwise.
         If CORENEURON simulator is being used, WholeCell should be used.

    .. blueconfig_value:: Dt
        :type: float
        :required: True
        :unit: ms
        :description:
         Duration of a single integration timestep

    .. blueconfig_value:: ProspectiveHosts
        :type: int
        :required: False
        :unit:
        :description:
         deprecated, use ModelBuildingSteps instead

    .. blueconfig_value:: BonusSynapseFile
        :type: abspath
        :required: False
        :unit:
        :description:
         Use Projection instead. Name of additional files containing synapse
         data. This is useful for introducing synapses from "external" sources
         such as long range connections from other brain regions.

    .. blueconfig_value:: CircuitTarget
        :type: string
        :required: False
        :unit:
        :description:
         Parameter which will restrict the neurons instantiated to those in the named target.
         Target can be from start.target or target file given in the TargetFile parameter.
         Option: specify a population name before the target name, format "population:target_name".

    .. blueconfig_value:: ExtracellularCalcium
        :type: float
        :required: False
        :unit:
        :description:
         Extracellular calcium concentration.
         This parameter, together with the uHill parameter of synapses,
         is used to scale the U parameter of synapses,
         and is working for py-neurodamus not hoc-neurodamus.

    .. blueconfig_value:: SecondOrder
        :type: int
        :required: False
        :unit:
        :description:
         Selects the NEURON/CoreNEURON integration method.
         This parameter sets the NEURON global variable h.secondorder.
         The allowed values are '0' for default implicit backward euler,
         '1' for Crank-Nicolson and '2' for Crank-Nicolson with fixed
         ion currents. For more info see:
         https://www.neuron.yale.edu/neuron/static/py_doc/simctrl/programmatic.html?highlight=second%20order#secondorder

    .. blueconfig_value:: V_Init
        :type: float
        :required: False
        :unit: mV
        :description:
         Initial voltage value for cells.
         This value is used in finitialize() function in Neuron.

    .. blueconfig_value:: Celsius
        :type: float
        :required: False
        :unit: degrees centigrade
        :description:
         Temperature of the simulation in degrees centigrade (celsius).

    .. blueconfig_value:: SpikeLocation
        :type: string
        :required: False
        :unit:
        :description:
         The spike detection location.
         Can be either 'SOMA' for detecting spikes in the soma or 'AIS' for
         detecting spikes on the AIS.

    .. blueconfig_value:: SpikeThreshold
        :type: float
        :required: False
        :unit: mV
        :description:
         The spike detection threshold.
         A spike is detected whenever the voltage in the spike detection location
         goes over the spike threshold value.

    .. blueconfig_value:: MinisSingleVesicle
        :type: int
        :required: False
        :unit:
        :description:
         Spont minis to use a single release vesicle, as discussed in BBPBGLIB-660.

    .. blueconfig_value:: RandomizeGabaRiseTime
        :type: string
        :required: False
        :unit:
        :description:
         A global parameter to skip randomizing the GABA_A rise time in the helper functions.

.. blueconfig_section:: Conditions
    :description:
     Specifies global parameters.

    .. blueconfig_value:: randomize_Gaba_risetime
        :type: string
        :required: False
        :unit:
        :description:
         An option to skip randomizing the GABA_A rise time in the helper functions,
         the same as RandomizeGabaRiseTime in the Run section.

    .. blueconfig_value:: SYNAPSES__init_depleted
        :type: boolean(1/0)
        :required: False
        :unit:
        :description:
         An option to initialize synapses in depleted state.

.. blueconfig_section:: Stimulus
    :description:
     Describes one pattern of stimulus that can be injected into multiple
     locations using one or more StimulusInject sections

    .. blueconfig_value:: NumOfSynapses
        :type: int
        :required: False
        :unit:
        :description:
         For NPoisson Stimulus. The number of synapses to create. Not for SONATA config.

    .. blueconfig_value:: Name
        :type: string
        :required: False
        :unit:
        :description:

    .. blueconfig_value:: PercentLess
        :type: float
        :required: False
        :unit:
        :description:
         For Subthreshold stimulus, each cell has a defined amount of current
         which will trigger one spike in 2 seconds. This pattern will use that
         defined current and scale it according to the PercentLess value

    .. blueconfig_value:: Pattern
        :type: Pattern
        :required: True
        :unit:
        :description:
         Type of stimulus: Linear, RelativeLinear, Pulse, NPoisson,
         NPoissonInhomogeneus, Sinusoidal(deprecated), Subthreshold, Noise,
         SynapseReplay, Hyperpolarizing, ReplayVoltageTrace, SEClamp

    .. blueconfig_value:: SynapseConfigure
        :type: string
        :required: False
        :unit:
        :description:
         For NPoisson Stimuli, allows the user to specify a Synapse object type
         which is available to the simulator. The default is ExpSyn. Possible
         values are : ProbAMPANMDA_EMS, ProbGABAAB_EMS, and ExpSyn.

    .. blueconfig_value:: PercentStart
        :type: float
        :required: False
        :unit:
        :description:
         For RelativeLinear, the percentage of a cell's threshold current to
         inject at the start of the injection

    .. blueconfig_value:: Delay
        :type: float
        :required: True
        :unit: ms
        :description:
         Time when stimulus commences

    .. blueconfig_value:: Width
        :type: float
        :required: False
        :unit: ms
        :description:
         For Pulse Stimulus, the duration in ms of a single pulse

    .. blueconfig_value:: Mode
        :type: Mode
        :required: True
        :unit:
        :description:
         Current is used for most stimuli.  Exceptions include
         ReplayVoltageTrace and SEClamp which then use "Voltage" instead

    .. blueconfig_value:: Var
        :type: float
        :required: False
        :unit:
        :description:
         deprecated

    .. blueconfig_value:: Variance
        :type: float
        :required: False
        :unit:
        :description:
         For Noise stimuli, the variance around the mean

    .. blueconfig_value:: MeanPercent
        :type: float
        :required: False
        :unit:
        :description:
         For Noise stimulus, the mean value of current to inject is a
         percentage of a cell's threshold current.  Used instead of 'Mean'

    .. blueconfig_value:: AmpStart
        :type: float
        :required: False
        :unit: nA
        :description:
         The amount of current initially injected when the stimulus activates

    .. blueconfig_value:: Weight
        :type: float
        :required: False
        :unit:
        :description:
         For NPoisson Stimulus. The strength of the created synapse

    .. blueconfig_value:: Format
        :type: Format
        :required: False
        :unit:
        :description:

    .. blueconfig_value:: PercentEnd
        :type: float
        :required: False
        :unit:
        :description:
         For RelativeLinear, the percentage of a cell's threshold current to
         inject at the end of the injection

    .. blueconfig_value:: AmpEnd
        :type: float
        :required: False
        :unit: nA
        :description:
         The final current when a stimulus concludes. Used by Linear

    .. blueconfig_value:: Frequency
        :type: float
        :required: False
        :unit: Hz
        :description:
         For Pulse Stimulus, the frequency of pulse trains

    .. blueconfig_value:: Voltage
        :type: float
        :required: False
        :unit:
        :description:
         For SEClamp, specifies the membrane voltage the targeted cells should
         be held at.

    .. blueconfig_value:: File
        :type: abspath
        :required: False
        :unit:
        :description:
         File path

    .. blueconfig_value:: Offset
        :type: float
        :required: False
        :unit:
        :description:
         For Pulse Stimulus, a std dev value each cell will apply to the Delay
         in order to add variation to the stimulation. Not for SONATA config.

    .. blueconfig_value:: Duration
        :type: float
        :required: True
        :unit: ms
        :description:
         Time length of stimulus duration

    .. blueconfig_value:: SpikeFile
        :type: path
        :required: False
        :unit:
        :description:
         For SynapseReplay, indicates the location of the file with the spike
         info for injection

    .. blueconfig_value:: Dt
        :type: float
        :required: False
        :unit:
        :description:

    .. blueconfig_value:: Mean
        :type: float
        :required: False
        :unit: nA
        :description:
         For Noise stimulus, the mean value of current to inject

    .. blueconfig_value:: Electrode
        :type: string
        :required: False
        :unit:
        :description:
         Electrode section to use

.. blueconfig_section:: StimulusInject
    :description:
     Pairs a Stimulus with a Target so that the stimulus is applied to the
     cells that make up the target.

    .. blueconfig_value:: Stimulus
        :type: string
        :required: True
        :unit:
        :description:
         Named stimulus

    .. blueconfig_value:: Target
        :type: target
        :required: True
        :unit:
        :description:
         Name of a target in start.target or user.target toreceive the
         stimulation

.. blueconfig_section:: Modification
    :description:
     (Deprecated, will need a new version for SONATA) Applies the necessary steps to simulate a chosen tissue manipulation
     from those available

    .. blueconfig_value:: GifParamsPath
        :type: abspath
        :required: False
        :unit:
        :description:
         Description: Define path to .h5 file where parameters for simplified
         GIF neurons are stored

    .. blueconfig_value:: Type
        :type: string
        :required: True
        :unit:
        :description:
         Name of one of the available Tissue Manipulations. Currently
         available: TTX

    .. blueconfig_value:: Target
        :type: target
        :required: True
        :unit:
        :description:
         Name of the target in start.target or user.target to receive the
         manipulation

.. blueconfig_section:: Report
    :description:
     Controls data collection during the simulation to collect things like
     compartment voltage.

    .. blueconfig_value:: Scaling
        :type: string
        :required: False
        :unit:
        :description:
         For Summation reports, the user can specify the handling of density
         values: "None" disables all scaling, "Area" (default) converts density
         to area values. This makes them compatible with values from point
         processes such as synapses.

    .. blueconfig_value:: Electrode
        :type: string
        :required: False
        :unit:
        :description:
         Name of an electrode section

    .. blueconfig_value:: Target
        :type: target
        :required: True
        :unit:
        :description:
         Defines what is to be reported. Note that cell targets versus compartment
         targets can influence report behavior. The same applies to section targets,
         that could request axon, dend, or apic inside the user.target file. Note
         that CoreNEURON has limited support for section targets (i.e., only one
         subtarget is allowed per section target).

    .. blueconfig_value:: StartTime
        :type: float
        :required: True
        :unit:
        :description:
         Time to start reporting

    .. blueconfig_value:: Format
        :type: string
        :required: True
        :unit:
        :description:
         ASCII, SONATA or Bin defining report output format

    .. blueconfig_value:: ReportOn
        :type: string
        :required: True
        :unit:
        :description:
         The NEURON variable to access

    .. blueconfig_value:: Dt
        :type: float
        :required: True
        :unit:
        :description:
         Frequency of reporting in milliseconds

    .. blueconfig_value:: EndTime
        :type: float
        :required: True
        :unit:
        :description:
         Time to stop reporting

    .. blueconfig_value:: Type
        :type: string
        :required: True
        :unit:
        :description:
         Compartment, Summation, or Synapse. Compartment means that each
         compartment outputs separately in the report file. Summation will sum
         up the currents and compartments to write a single value to the report
         (soma target) or sum up the currents and leave them in each compartment
         (compartment target). Synapse indicates that each synapse will have a
         separate entry in the report.

    .. blueconfig_value:: Unit
        :type: string
        :required: True
        :unit:
        :description:
         String to output as descriptive test for unit recorded. Not validated
         for correctness

.. blueconfig_section:: Connection
    :description:
     Adjusts the synaptic strength between two sets of cells.

    .. blueconfig_value:: Destination
        :type: target
        :required: True
        :unit:
        :description:
         Target defining postsynaptic cells

    .. blueconfig_value:: SynapseConfigure
        :type: string
        :required: False
        :unit:
        :description:
         Provide a snippet of hoc code which is to be executed on the synapse
         objects created under this Connection section

    .. blueconfig_value:: Delay
        :type: float
        :required: False
        :unit:
        :description:
         The weight modifications of this Connection can be applied after a
         specified delay has elapsed. Note that only Weight modifications are
         applied and no other features of Connection sections

    .. blueconfig_value:: Source
        :type: target
        :required: True
        :unit:
        :description:
         Target defining presynaptic cells

    .. blueconfig_value:: Weight
        :type: float
        :required: False
        :unit:
        :description:
         Scalar used to adjust synaptic strength

    .. blueconfig_value:: SpontMinis
        :type: float
        :required: False
        :unit:
        :description:
         During simulation, Synapses created under this Connection section will
         spontaneously trigger with the given rate

    .. blueconfig_value:: ModOverride
        :type: string
        :required: False
        :unit:
        :description:
         Override synaptic helper function (GABAABHelper.hoc or
         AMPANMDAHelper.hoc) with this new helper function. Only give prefix,
         e.g. "Newfun" uses NewfunHelper.hoc

    .. blueconfig_value:: SynDelayOverride
        :type: float
        :required: False
        :unit: ms
        :description:
         Value to override the synaptic delay time originally set in the edge file,
         and to be given to netcon object.

.. blueconfig_section:: Electrode
    :description:
     Will not be used for SONATA config.

    .. blueconfig_value:: y
        :type: float
        :required: True
        :unit: um
        :description:
         y position

    .. blueconfig_value:: x
        :type: float
        :required: True
        :unit: um
        :description:
         x position

    .. blueconfig_value:: z
        :type: float
        :required: True
        :unit: um
        :description:
         z position

    .. blueconfig_value:: Version
        :type: int
        :required: False
        :unit:
        :description:
         version of the reader to use

    .. blueconfig_value:: File
        :type: path
        :required: True
        :unit:
        :description:
         file name under the electrodePath directory

.. blueconfig_section:: Projection
    :description:
     Designed to take into account axons projecting to and from different
     areas of the brain. It can also be used to take gap junctions into
     account. In order to enable a Projection, you also need to activate it
     with Stimulus and StimulusInject blocks. For details see BlueConfig Projection example.
     For Sonata config, projections are additional edge files in "networks" (circuit_config file).

    .. blueconfig_value:: Path
        :type: abspath
        :required: True
        :unit:
        :description:
         Location of data files with additional connectivity info
         Option: specify a population name after the path, format "path:population".

    .. blueconfig_value:: Type
        :type: string
        :required: False
        :unit:
        :description:
         Distinguishes "Synaptic" projections from "GapJunction" projections.
         If omitted, Synaptic is assumed.

    .. blueconfig_value:: NumSynapseFiles
        :type: int
        :required: False
        :unit:
        :description:
         The number of synapse files. To be made obsolete once better metadata
         handling is added.

    .. blueconfig_value:: Source
        :type: target
        :required: False
        :unit:
        :description:
         Optional. Provides new gids if the connection sources are external to
         the main circuit

    .. blueconfig_value:: PopulationID
        :type: int
        :required: False
        :unit:
        :description:
         Defines an ID for the population for RNG seeding purposes.
         Default is 0, which is used by circuit connections (e.g. nrn.h5) so using 0 for projections
         would create overlapping streams. User should set it to 1 or greater.
         Should they be unique?  It depends on if the projections should be considered as coming
         from the same 'source'. If the user creates multiple projections from a population to
         different destination groups, then it would make sense to reuse the same populationID.
         This should be considered a temporary fix until we fully support SONATA population labels
         NOTE: With MCellRan4, the max value accepted is 255 and for Random123 it is 65535.

    .. blueconfig_value:: AppendBasePopulation
        :type: int
        :required: False
        :unit:
        :description:
         When using a Sonata projection file containing legacy gid-offset connections,
         in order to merge connections with base connectivity and avoid creating a new
         PopulationID (implying different seeding), this option should be set to 1.
         Default is disabled (0)
