#!/bin/sh

if [ "$#" -ne 1 ]; then
    echo "You have to specify directory to generate test for"
    exit 1
fi

PY_PARS=" --coverage-metrics BRANCH --assertion-generation NONE --maximum-iterations 1000 --create-coverage-report True --algorithm DYNAMOSA -v "

if [ -d $1 ]; then 
    for dir in $1/*; do
        if [ -d $dir ]; then
            dirname="$(basename "$dir")"
            if ! [ "$dirname" = "__pycache__" ]; then
                echo "------------------------------$dirname"
                ( cd $dir && rm -rf ./pynguin_results ; pynguin $PY_PARS --project-path . --output-path . --module-name $dirname --report-dir ./pynguin_results/  )
            fi
        fi
    done
else
    echo "You have to specify a directory as first argument"
    exit 1
fi
