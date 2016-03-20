FROM debian:jessie

RUN apt-get update && apt-get install -y dnsmasq wget

RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.0.1/dumb-init_1.0.1_amd64
RUN chmod +x /usr/local/bin/dumb-init

COPY dnsmasq.conf /etc/dnsmasq.conf.template
COPY docker-entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
