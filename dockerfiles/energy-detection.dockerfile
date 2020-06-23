FROM kernsuite/base:dev

USER root

ENV DEBIAN_FRONTEND=noninteractive

# install base dependencies
RUN docker-apt-install \
     python3-setuptools \
     python3-astropy \
     python3-scipy \
     python3-pandas \
     python3-tqdm \
     python3-matplotlib \
     python3-bitshuffle \
     python3-h5py \
     python3-slalib \
     python3-pytest-runner \
     python3-pytest \
     python3-pip \
     git \
     curl

RUN mkdir /code
WORKDIR /code

RUN git clone https://github.com/FX196/SETI-Energy-Detection.git
