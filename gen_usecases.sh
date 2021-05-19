#!/usr/bin/env bash
base_path=usecase_examples

echo Creating virtual env
python3 -m venv sg-venv
source sg-venv/bin/activate

echo Install library
pip install -U pip setuptools
pip install -e .

for usecase_id in {1..4}
do
    echo Processing usecase ${usecase_id}
    circuit_cmd="sonata-generator circuit -vvv create ./$base_path/config/nodes_configuration.yaml ./$base_path/config/edges_configuration.yaml ./$base_path/config/usecase${usecase_id}/population_config.yaml $PWD/$base_path/components ./results/usecase${usecase_id} -s 0"
    echo $circuit_cmd
    $circuit_cmd
    reports_cmd="sonata-generator reports -vvv create ./$base_path/config/usecase${usecase_id}/population_config.yaml $PWD/$base_path/components ./results/usecase${usecase_id} -s 0"
    echo $reports_cmd
    $reports_cmd
    [ $? -eq 0 ] || exit 1

    find ./results  -name "*.h5"  -exec bash -c "h5dump -y {} > {}.txt" \;
    [ $? -eq 0 ] || exit 1
done
