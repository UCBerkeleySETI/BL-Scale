FROM ubuntu:18.04

USER root

ENV LANG C.UTF-8

RUN apt update
RUN apt install -y git curl python3-pip gunicorn3

RUN mkdir /code
WORKDIR /code
COPY . /code/BL-Scale
WORKDIR /code/BL-Scale/webapp
RUN pip3 install -r requirements.txt

CMD gunicorn3 -k=gevent -b :5000 --log-level=debug "main_bp:config_app()"
