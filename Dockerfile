FROM python:3.6.5

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python3", "puffin.py"]
CMD ["up"]

