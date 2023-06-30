#!/usr/bin/env bash
base_path=results
bluepysnap=bluepysnap

if [[ -d $base_path ]]
then
    files=( $(find $base_path -type f -name circuit_sonata.json | sort) )
fi

if [ ${#files[@]} -lt 1 ]
then
    echo "ERROR: Generated files not found"
    exit 1
fi

exit_code=0
for file in ${files[@]}
do
    echo "Validating $file ..."
    if ! $bluepysnap validate $file
    then
        exit_code=1
    fi
    echo
done

exit $exit_code
