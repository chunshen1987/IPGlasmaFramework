#!/usr/bin/env bash

# download the code package

# download IPGlasma
rm -fr ipglasma_code
#git clone --depth=1 https://github.com/schenke/ipglasma ipglasma_code
git clone --depth=1 https://github.com/chunshen1987/ipglasma ipglasma_code
rm -fr ipglasma_code/.git

# download subnucleondiffraction
rm -fr subnucleondiffraction_code
git clone --depth=1 https://github.com/hejajama/subnucleondiffraction -b UPC_diff subnucleondiffraction_code
rm -fr subnucleondiffraction_code/.git
