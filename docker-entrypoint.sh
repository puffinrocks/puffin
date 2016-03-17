#!/usr/local/bin/dumb-init /bin/bash

# wait for database startup
sleep 6

for ARG in "$@"
do
    python3 -u puffin.py $ARG
done

