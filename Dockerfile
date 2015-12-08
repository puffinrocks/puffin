FROM python:3-onbuild

COPY docker-entrypoint.sh entrypoint.sh

CMD [ "python3", "-u", "puffin.py", "server" ]

