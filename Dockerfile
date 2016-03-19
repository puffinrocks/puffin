FROM python:3-onbuild

COPY docker-entrypoint.sh entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
CMD ["db create", "db upgrade", "user create puffin", "machine network", "machine proxy", "machine mail", "server"]

