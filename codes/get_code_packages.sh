#!/usr/bin/env bash

# download the code package

# download IPGlasma
rm -fr ipglasma_code
git clone --depth=1 https://github.com/wenbin1501110084/ipglasma -b stingy_proton_jimwlk ipglasma_code
#(cd ipglasma_code; git checkout 492e80291b2e68d3bc28644bf524e59dc1af9c7d)
rm -fr ipglasma_code/.git

# download subnucleondiffraction
rm -fr subnucleondiffraction_code
#git clone --depth=1 https://github.com/hejajama/subnucleondiffraction subnucleondiffraction_code
git clone --depth=1 https://github.com/chunshen1987/subnucleondiffraction -b integratedCrossSection subnucleondiffraction_code
(cd subnucleondiffraction_code; git checkout 8eaefcd5a4ea90eef1c5fbe4edb6604c5c1f2b9a)
rm -fr subnucleondiffraction_code/.git

