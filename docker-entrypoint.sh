#!/usr/local/bin/dumb-init /bin/bash

# wait for database startup
sleep 3

python3 -u puffin.py db create
python3 -u puffin.py db upgrade
python3 -u puffin.py machine proxy
python3 -u puffin.py user create puffin

if [[ $# -ne 0 ]]; then
    python3 -u puffin.py "$@"
fi

