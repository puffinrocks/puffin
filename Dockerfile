FROM python:3-onbuild

COPY docker-entrypoint.sh entrypoint.sh

ENV VIRTUAL_HOST=${SERVER_NAME:-localhost}

ENTRYPOINT ["./entrypoint.sh"]
CMD ["server"]

