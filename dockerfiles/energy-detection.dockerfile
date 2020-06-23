FROM kernsuite/base:dev

USER root

ENV DEBIAN_FRONTEND=noninteractive

# install base dependencies
RUN docker-apt-install libhdf5-serial-dev gfortran python3-pip git pkg-config curl
RUN apt-get update
RUN apt-get install -y git curl \
    python3-setuptools \
    python3-scipy \
    python3-matplotlib \
    python3-pip \
    python3-pandas \
    python3-tqdm

ENV CFLAGS="-I/usr/include/hdf5/serial -L/usr/lib/x86_64-linux-gnu/hdf5/serial"
RUN ln -s /usr/lib/x86_64-linux-gnu/libhdf5_serial.so /usr/lib/x86_64-linux-gnu/libhdf5.so
RUN ln -s /usr/lib/x86_64-linux-gnu/libhdf5_serial_hl.so /usr/lib/x86_64-linux-gnu/libhdf5_hl.so
RUN pip3 install git+https://github.com/h5py/h5py@8d96a14c3508de1bde77aec5db302e478dc5dbc4

RUN mkdir /code
WORKDIR /code

RUN git clone https://github.com/FX196/SETI-Energy-Detection.git
