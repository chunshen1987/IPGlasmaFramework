#!/usr/bin/env bash

# download the code package

# download IPGlasma
rm -fr ipglasma_code
git clone --depth=1 https://github.com/schenke/ipglasma ipglasma_code
rm -fr ipglasma_code/.git

# download subnucleondiffraction
rm -fr amplitudelib_v2
git clone --depth=1 https://github.com/hejajama/amplitudelib amplitudelib_v2
rm -fr amplitudelib_v2/.git
rm -fr subnucleondiffraction_code
git clone --depth=1 https://github.com/hejajama/subnucleondiffraction subnucleondiffraction_code
rm -fr subnucleondiffraction_code/.git
