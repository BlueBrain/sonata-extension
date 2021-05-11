#!/usr/bin/env bash
base_path=usecase_examples

for usecase_id in {1..4}
do
    mkdir -p ./results/usecase${usecase_id}
    python ./sonata_generator/circuit_generator.py ./$base_path/config/nodes_configuration.yaml ./$base_path/config/edges_configuration.yaml ./$base_path/config/usecase${usecase_id}/population_config.yaml $PWD/$base_path/components ./results/usecase${usecase_id} 
    [ $? -eq 0 ] || exit 1

    for h5_file in `ls -1 ./results/usecase${usecase_id}/*.h5`
    do
        h5dump -y  ${h5_file} > ${h5_file}.txt
        [ $? -eq 0 ] || exit 1
    done
done

