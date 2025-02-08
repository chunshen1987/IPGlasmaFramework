FROM ubuntu:22.04

MAINTAINER Chun Shen <chunshen@wayne.edu>

RUN export DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true && \
    apt-get update && apt-get install -y --no-install-recommends \
        cmake \
        cmake-data \
        curl \
        g++ \
        gcc \
        gfortran \
        git \
        hdf5-tools \
        libfftw3-dev \
        libgsl-dev \
        libhdf5-dev \
        libz-dev \
        make \
        pkg-config \
        python3 \
        python3-pip \
        time \
        vim \
        wget \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install pre-reqs python packages
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install numpy h5py scipy

ENV HOME /opt/

# download and compile the IPGlasma framework
RUN cd ${HOME} && \
    git clone --depth=1 https://github.com/chunshen1987/IPGlasmaFramework && \
    cd IPGlasmaFramework/codes && \
    ./get_code_packages.sh && \
    ./compile_code_packages.sh

ENV PYTHONIOENCODING utf-8
WORKDIR ${HOME}/IPGlasmaFramework

CMD /bin/bash
