#!/usr/bin/env bash

# download the code package

# download IPGlasma
rm -fr ipglasma_code
git clone --depth=5 https://github.com/chunshen1987/ipglasma -b ipglasma_jimwlk ipglasma_code
(cd ipglasma_code; git checkout e37b9f191c3e5be00edb3c298348a6c7aeb73e6a)
rm -fr ipglasma_code/.git

# download subnucleondiffraction
rm -fr subnucleondiffraction_code
#git clone --depth=1 https://github.com/hejajama/subnucleondiffraction subnucleondiffraction_code
git clone --depth=1 https://github.com/chunshen1987/subnucleondiffraction -b integratedCrossSection subnucleondiffraction_code
(cd subnucleondiffraction_code; git checkout 8eaefcd5a4ea90eef1c5fbe4edb6604c5c1f2b9a)
rm -fr subnucleondiffraction_code/.git

# download nucleus configurations for IP-Glasma
(cd ipglasma_code/nucleusConfigurations; bash download_nucleusTables.sh;)
