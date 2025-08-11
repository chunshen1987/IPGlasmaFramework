#!/usr/bin/env bash

Green='\033[0;32m'
NC='\033[0m'

CCFlag=$1
CXXFlag=$2
FCFlag=$3

if [ -z "$CCFlag" ]; then
    CCFlag=gcc
fi
if [ -z "$CXXFlag" ]; then
    CXXFlag=g++
fi
if [ -z "$FCFlag" ]; then
    FCFlag=gfortran
fi

machine="$(uname -s)"
case "${machine}" in
    Linux*)     number_of_cores=`nproc --all`;;
    Darwin*)    number_of_cores=`sysctl -n hw.ncpu`;;
    *)          number_of_cores=1;;
esac
number_of_cores_to_compile=$(( ${number_of_cores} > 10 ? 10 : ${number_of_cores} ))

# compile IPGlasma
echo -e "${Green}compile IPGlasma ... ${NC}"
(
    cd ipglasma_code
    mkdir -p build
    cd build
    rm -fr *
    CC=${CCFlag} CXX=${CXXFlag} cmake .. -DdisableMPI=ON
    make -j$number_of_cores_to_compile
    make install
)
status=$?
if [ $status -ne 0 ]; then
    exit $status
fi

# compile subnucleondiffractiop
echo -e "${Green}compile subnucleondiffraction ... ${NC}"
(
    cd subnucleondiffraction_code
    mkdir -p build
    cd build
    rm -fr *
    CC=${CCFlag} CXX=${CXXFlag} cmake ..
    make -j$number_of_cores_to_compile subnucleondiffraction
)
status=$?
if [ $status -ne 0 ]; then
    exit $status
fi
