FROM ubuntu:18.04

USER root

ENV LANG C.UTF-8

RUN apt update
RUN apt install -y git curl python3.8 python3.8-distutils
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.8 get-pip.py
RUN python3.8 -m pip install --upgrade pip setuptools wheel

RUN curl -sSL https://sdk.cloud.google.com | bash
ENV PATH $PATH:/root/google-cloud-sdk/bin

RUN mkdir /code
WORKDIR /code
COPY . /code/BL-Scale
WORKDIR /code/BL-Scale/
RUN pip3.8 install --upgrade pip
RUN pip3.8 install zmq kubernetes tqdm

# hack to remove carrige return
# RUN sed $'s/\r$//' /code/BL-Scale/scripts/start_scheduler_pod.sh > /code/BL-Scale/scripts/start_scheduler_pod.sh

RUN cat /code/BL-Scale/scripts/start_scheduler_pod.sh

CMD sh /code/BL-Scale/scripts/start_scheduler_pod.sh
