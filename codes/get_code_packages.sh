#!/usr/bin/env bash

# download the code package

# download IPGlasma
rm -fr ipglasma_code
git clone --depth=1 https://github.com/chunshen1987/ipglasma -b ipglasma_jimwlk ipglasma_code
(cd ipglasma_code; git checkout d45370ec15f95412ef60cbeabc5d9f23c95b7bbb)
rm -fr ipglasma_code/.git

# download subnucleondiffraction
rm -fr subnucleondiffraction_code
#git clone --depth=1 https://github.com/hejajama/subnucleondiffraction subnucleondiffraction_code
git clone --depth=1 https://github.com/chunshen1987/subnucleondiffraction subnucleondiffraction_code
(cd subnucleondiffraction_code; git checkout aea732301e773031f4dd106ce73da9f18c8039b4)
rm -fr subnucleondiffraction_code/.git
