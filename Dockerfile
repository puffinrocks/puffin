FROM python:3-onbuild

ENTRYPOINT ["python3", "-u", "puffin.py"]
CMD ["up"]

