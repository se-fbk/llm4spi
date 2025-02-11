#!/bin/sh

if [ "$#" -ne 2 ]; then
    echo "You have to specify directory to test and selected test suite"
    exit 1
fi

ROOT=$PWD

if [ -d $1 ]; then 
    for dir in $1/*; do
        if [ -d $dir ]; then
            dirname="$(basename "$dir")"
            if ! [ "$dirname" = "__pycache__" ]; then
                echo "------------------------------$dirname"
                mkdir ./mutation-report/$dirname
                ( cd $dir && poodle . --html $ROOT/mutation-report/$dirname/html/$2 --json $ROOT/mutation-report/$dirname/$dirname\_$2.json )
            fi
        fi
    done
    echo "Reports successfully created inside ./mutation-report"
else
    echo "You have to specify a directory as first argument"
    exit 1
fi