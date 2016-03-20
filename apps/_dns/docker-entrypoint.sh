#!/usr/local/bin/dumb-init /bin/bash
set -e

HOST=`/sbin/ip route|awk '/default/ { print $3 }'`

sed "s/\$HOST/$HOST/" /etc/dnsmasq.conf.template > /etc/dnsmasq.conf

/usr/sbin/dnsmasq -k
