FROM kernsuite/base:dev

USER root

ENV DEBIAN_FRONTEND=noninteractive

# install base dependencies
RUN docker-apt-install \
     python3-setuptools \
     python3-scipy \
     python3-matplotlib \
     python3-bitshuffle \
     python3-h5py \
     python3-pip \
     git \
     curl
RUN pip3 install zmq tqdm pandas wget google-cloud-storage

RUN mkdir /code
WORKDIR /code

RUN git clone https://github.com/FX196/SETI-Energy-Detection.git
RUN git clone https://github.com/FX196/BL-Scale.git
RUN git clone https://github.com/FX196/alien_hunting_algs.git

CMD python3 -m alien_hunting_algs.$ALG_SUB_PACKAGE.$ALG_NAME
