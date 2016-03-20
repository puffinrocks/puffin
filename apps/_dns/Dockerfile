FROM debian:jessie

RUN apt-get update && apt-get install -y dnsmasq wget

COPY dnsmasq.conf /etc/dnsmasq.conf.template
COPY docker-entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
