#!/bin/sh

if [ "$#" -ne 1 ]; then
    echo "You have to specify directory to generate test for"
    exit 1
fi

if [ -d $1 ]; then 
    for dir in $1/*; do
        if [ -d $dir ]; then
            dirname="$(basename "$dir")"
            if ! [ "$dirname" = "__pycache__" ]; then
                echo "------------------------------$dirname"
                ( cd $dir && rm -rf ./pynguin_results ; pynguin --project-path . --output-path . --module-name $dirname --report-dir ./pynguin_results/ --maximum-iterations 80 -v )
            fi
        fi
    done
else
    echo "You have to specify a directory as first argument"
    exit 1
fi