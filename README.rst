example usage
=============

base_path=sonata-generator/usecase_examples
python ./sonata-generator/sonata_generator/circuit_generator.py ./$base_path/config/nodes_configuration.yaml ./$base_path/config/edges_configuration.yaml ./$base_path/config/usecase1/population_config.yaml $PWD/$base_path/components ./results -v DEBUG



Usecases
========

Usecase 1
---------
1 population of biophysical neurons with chemical synapses between neurons of that population.

Usecase 2
---------
1 population of biophysical neurons with chemical synapses between neurons of that population + 1 virtual node population projecting into the biophysical neurons.

Usecase 3
---------
2 populations of biophysical neurons in 2 separate files with chemical synapses between neurons of their population and the other population.

Usecase 4
---------
2 populations of biophysical neurons with chemical synapses between neurons of their population and the other population + 2 virtual node population projecting each in 1 different population.

Usecase 5
---------
1 population of neurons, 1 population of glial, 1 population of vasculature with:
- chemical synapses between neurons
- electrical synapses between glial cells
- astrocyte to synapse from glial to neurons
- end foot from vasculature to glial

Usecase 6
---------
1 population of biophysical neurons with chemical synapses and with gap junctions between neurons of that population + 1 virtual node population projecting into the biophysical neurons

Usecase 7
---------
1 population of point neuron models with chemical synapses between neurons of that population

Usecase 8
---------
1 population of point neuron models and 1 population of biophysical neuron models with connections between (both ways ?) the 2 population

Usecase 9
---------
1 population of point neuron models and 1 population of biophysical neuron models with connections between (both ways ?) the 2 population + 2 virtual node population projection into each population


Usecase 10
----------
combine usecase 4 and 5 ?

TODO
====

- decide between 3-uple or 2-uple for synapses
- decide between rotation angle and quaternions
- decide if hoc files needs to match EType and morphologies (scientifically correct or not).
- soma and compartment reports generation
