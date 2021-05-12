#!/usr/bin/env bash
base_path=usecase_examples

for usecase_id in {1..4}
do
    echo Processing usecase ${usecase_id}
    mkdir -p ./results/usecase${usecase_id}
    python ./sonata_generator/circuit_generator.py ./$base_path/config/nodes_configuration.yaml ./$base_path/config/edges_configuration.yaml ./$base_path/config/usecase${usecase_id}/population_config.yaml $PWD/$base_path/components ./results/usecase${usecase_id}
    python ./sonata_generator/report_generator.py  ./$base_path/config/usecase${usecase_id}/population_config.yaml ./results/usecase${usecase_id} -v DEBUG
    [ $? -eq 0 ] || exit 1

    find ./results  -name "*.h5"  -exec bash -c "h5dump -y {} > {}.txt" \;
    [ $? -eq 0 ] || exit 1
done
