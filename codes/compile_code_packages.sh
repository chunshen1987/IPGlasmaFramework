#!/usr/bin/env bash

Green='\033[0;32m'
NC='\033[0m'

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
    ./compile_IPGlasma.sh noMPI
)
status=$?
if [ $status -ne 0 ]; then
    exit $status
fi

# compile subnucleondiffraction
echo -e "${Green}compile subnucleondiffraction ... ${NC}"
(
    cd subnucleondiffraction_code
    mkdir build
    cd build
    cmake ..
    make -j$number_of_cores_to_compile
)
status=$?
if [ $status -ne 0 ]; then
    exit $status
fi
