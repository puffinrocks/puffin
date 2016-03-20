#!/bin/bash
set -e

# Don't change secret on every restart
if [[ ! -f /data/gogs/conf/secret ]]; then
    SECRET=`head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12`
    echo "SECRET=$SECRET" > /data/gogs/conf/secret
fi

cp /app/gogs/app.ini  /data/gogs/conf/app.ini
chown -R git /data/gogs/conf

. /data/gogs/conf/secret

sed -i "s/\$SECRET/$SECRET/" /data/gogs/conf/app.ini
sed -i "s/\$DOMAIN/$VIRTUAL_HOST/" /data/gogs/conf/app.ini

docker/start.sh $@
