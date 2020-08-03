FROM ubuntu:18.04

USER root

ENV LANG C.UTF-8

RUN apt update
RUN apt install -y git curl python3-pip

RUN mkdir /code
WORKDIR /code
COPY . /code/BL-Scale
WORKDIR /code/BL-Scale/
RUN pip3 install zmq kubernetes

CMD sleep 1000000
