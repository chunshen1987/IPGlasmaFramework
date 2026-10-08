#!/usr/bin/env bash

# download the code package

# download IPGlasma
rm -fr ipglasma_code
#git clone --depth=5 https://github.com/chunshen1987/ipglasma -b ipglasma_jimwlk ipglasma_code
git clone --depth=5 https://github.com/schenke/ipglasma -b devel ipglasma_code
(cd ipglasma_code; git checkout c51676b0703862aa4304e3d5fe7e78127116bf62)
rm -fr ipglasma_code/.git

# download subnucleondiffraction
rm -fr subnucleondiffraction_code
#git clone --depth=1 https://github.com/hejajama/subnucleondiffraction subnucleondiffraction_code
git clone --depth=5 https://github.com/chunshen1987/subnucleondiffraction -b roch/devel subnucleondiffraction_code
(cd subnucleondiffraction_code; git checkout bc9bf0b22a68b89cdf102e4a7093a1e4289af37c)
rm -fr subnucleondiffraction_code/.git

# download nucleus configurations for IP-Glasma
(cd ipglasma_code/nucleusConfigurations; bash download_nucleusTables.sh;)
