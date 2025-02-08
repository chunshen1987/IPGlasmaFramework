FROM opensciencegrid/software-base:23-el9-release

MAINTAINER Chun Shen <chunshen@wayne.edu>

RUN yum -y install \
        cmake \
        cmake3 \
        git \
        eigen3-devel \
        gcc \
        gcc-c++ \
        gcc-gfortran \
        gsl-devel \
        fftw \
        fftw-devel \
        hdf5-devel \
        zlib-devel \
        make \
        openmpi-devel \
        python3 \
        python3-pip \
        time \
        vim \
        wget \
        && \
    yum clean all

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

# Cleaning caches to reduce size of image
RUN yum clean all

# required directories
RUN for MNTPOINT in \
        /cvmfs \
        /hadoop \
        /hdfs \
        /lizard \
        /mnt/hadoop \
        /mnt/hdfs \
        /xenon \
        /scratch \
        /spt \
        /stash2 \
    ; do \
        mkdir -p $MNTPOINT ; \
    done

ENV PYTHONIOENCODING utf-8
WORKDIR ${HOME}/

