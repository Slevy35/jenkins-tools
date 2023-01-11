FROM python:3.10-slim-buster

WORKDIR /tools

COPY tools .
COPY setup.py .

RUN python setup.py install