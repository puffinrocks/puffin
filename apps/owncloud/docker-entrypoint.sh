#!/bin/bash
set -e

if [ ! -e '/var/www/html/version.php' ]; then
    tar cf - --one-file-system -C /usr/src/owncloud . | tar xf -
    chown -R www-data /var/www/html
fi

sed -i "s/\$DOMAIN/$VIRTUAL_HOST/" /var/www/html/config/config.php

exec "$@"
