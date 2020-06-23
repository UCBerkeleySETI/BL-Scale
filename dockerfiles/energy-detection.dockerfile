FROM kernsuite/base:dev

USER root

ENV DEBIAN_FRONTEND=noninteractive

# install base dependencies
RUN apt-get update
RUN apt-get install -y git curl \
    python3-setuptools \
    python3-scipy \
    python3-matplotlib \
    python3-h5py \
    python3-pip \
    python3-pandas \
    python3-tqdm

RUN mkdir /code
WORKDIR /code

RUN git clone https://github.com/FX196/SETI-Energy-Detection.git
