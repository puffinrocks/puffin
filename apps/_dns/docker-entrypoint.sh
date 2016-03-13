#!/usr/local/bin/dumb-init /bin/bash
set -e

HOST=`/sbin/ip route|awk '/default/ { print $3 }'`

sed "s/\$HOST/$HOST/" /etc/dnsmasq.conf.template > /etc/dnsmasq.conf

echo "nameserver 127.0.0.1" > /etc/resolv.conf

/usr/sbin/dnsmasq -k
