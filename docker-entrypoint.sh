#!/usr/local/bin/dumb-init /bin/sh

# wait for database startup
sleep 1

python3 -u puffin.py db create
python3 -u puffin.py db upgrade
python3 -u puffin.py machine proxy

python3 -u puffin.py server

