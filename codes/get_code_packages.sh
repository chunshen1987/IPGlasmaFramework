#!/usr/bin/env bash

# download the code package

# download IPGlasma
rm -fr ipglasma_code
git clone --depth=1 https://github.com/chunshen1987/ipglasma -b ipglasma_jimwlk ipglasma_code
(cd ipglasma_code; git checkout e3e7b1528554df04b062fc88cda721d5b78a09a6)
rm -fr ipglasma_code/.git

# download subnucleondiffraction
rm -fr subnucleondiffraction_code
git clone --depth=1 https://github.com/hejajama/subnucleondiffraction subnucleondiffraction_code
rm -fr subnucleondiffraction_code/.git
