FROM ubuntu:18.04

USER root

RUN apt update
RUN apt install -y git python3-pip

RUN mkdir /code
WORKDIR /code
RUN git clone --single-branch --branch shirley-dev https://github.com/UCBerkeleySETI/BL-Scale.git
WORKDIR /code/BL-Scale/webapp
RUN pip3 install -r requirements.txt

CMD python3 zproxy.py
