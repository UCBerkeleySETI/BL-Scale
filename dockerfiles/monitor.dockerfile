FROM ubuntu:18.04

USER root

ENV LANG C.UTF-8

RUN apt update
RUN apt install -y git curl python3-pip

RUN curl -sSL https://sdk.cloud.google.com | bash
ENV PATH $PATH:/root/google-cloud-sdk/bin

RUN mkdir /code
WORKDIR /code
COPY . /code/BL-Scale
WORKDIR /code/BL-Scale/
RUN pip3 install --upgrade pip
RUN pip3 install zmq kubernetes tqdm numpy pandas matplotlib Pyrebase

# hack to remove carrige return
# RUN sed $'s/\r$//' /code/BL-Scale/scripts/start_monitor_pod.sh > /code/BL-Scale/scripts/start_monitor_pod.sh

CMD sh /code/BL-Scale/scripts/start_monitor_pod.sh
