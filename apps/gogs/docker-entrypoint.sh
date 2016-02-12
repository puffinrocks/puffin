#!/bin/bash
set -e

# Don't change secret on every restart
if [[ ! -f /data/gogs/conf/app.ini ]]; then
    mkdir -p /data/gogs/conf
    SECRET=`head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12`
    sed "s/\$SECRET/$SECRET/" /app/gogs/app.ini >  /data/gogs/conf/app.ini
fi

sed -i "s/\$DOMAIN/$VIRTUAL_HOST/" /data/gogs/conf/app.ini

chown -R git /data/gogs/conf

docker/start.sh $@
