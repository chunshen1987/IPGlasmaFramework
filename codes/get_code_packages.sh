#!/usr/bin/env bash

# download the code package

# download IPGlasma
rm -fr ipglasma_code
git clone --depth=1 https://github.com/chunshen1987/ipglasma -b ipglasma_jimwlk ipglasma_code
(cd ipglasma_code; git checkout c352a3c476238e37dba70e2a880c186b65a06aee)
rm -fr ipglasma_code/.git

# download subnucleondiffraction
rm -fr subnucleondiffraction_code
#git clone --depth=1 https://github.com/hejajama/subnucleondiffraction subnucleondiffraction_code
git clone --depth=1 https://github.com/chunshen1987/subnucleondiffraction -b integratedCrossSection subnucleondiffraction_code
(cd subnucleondiffraction_code; git checkout b72a3c08c094842f1aa7933725bcab4c3ed051ce)
rm -fr subnucleondiffraction_code/.git
