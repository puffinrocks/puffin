FROM python:3-onbuild

COPY docker-entrypoint.sh entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["server"]

