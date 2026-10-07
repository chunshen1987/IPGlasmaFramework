#!/usr/bin/env bash

# download the code package

# download IPGlasma
rm -fr ipglasma_code
#git clone --depth=5 https://github.com/chunshen1987/ipglasma -b ipglasma_jimwlk ipglasma_code
git clone --depth=5 https://github.com/schenke/ipglasma -b devel ipglasma_code
(cd ipglasma_code; git checkout f793db6a66092d5fc8cb3ebc91434570b41ca5ff)
rm -fr ipglasma_code/.git

# download subnucleondiffraction
rm -fr subnucleondiffraction_code
#git clone --depth=1 https://github.com/hejajama/subnucleondiffraction subnucleondiffraction_code
git clone --depth=5 https://github.com/chunshen1987/subnucleondiffraction -b roch/devel subnucleondiffraction_code
(cd subnucleondiffraction_code; git checkout bfd879b4d5c1d3c57b46a12f3058de27a18eb03d)
rm -fr subnucleondiffraction_code/.git

# download nucleus configurations for IP-Glasma
(cd ipglasma_code/nucleusConfigurations; bash download_nucleusTables.sh;)
