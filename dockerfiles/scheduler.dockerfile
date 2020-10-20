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
RUN pip3 install zmq kubernetes tqdm

CMD sh /code/BL-Scale/scripts/start_scheduler_pod.sh
