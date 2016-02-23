#!/usr/local/bin/dumb-init /bin/bash

# wait for database startup
sleep 6

python3 -u puffin.py db create
python3 -u puffin.py db upgrade
python3 -u puffin.py user create puffin
python3 -u puffin.py machine proxy

if [[ "$@" != "" ]]; then
    python3 -u puffin.py "$@"
fi

