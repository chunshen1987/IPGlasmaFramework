#!/usr/bin/env bash

# download the code packages at the pinned commits; stop at the first error
set -e

# get_pinned <repository> <commit> <folder>: download exactly <commit>. It is
# fetched by its hash, so it is found however far the branch has moved on
# (a shallow clone of the branch loses it after a few new commits).
get_pinned() {
    rm -fr "$3"
    git init -q "$3"
    git -C "$3" fetch -q --depth=1 "$1" "$2"
    git -C "$3" checkout -q FETCH_HEAD
    echo "$3: $(git -C "$3" log -1 --format='%h %s')"
    rm -fr "$3/.git"
}

# download IPGlasma (devel branch)
#git clone --depth=5 https://github.com/chunshen1987/ipglasma -b ipglasma_jimwlk ipglasma_code
get_pinned https://github.com/schenke/ipglasma \
    50c14a4630e0b4dceed5679dac09d270a999183b ipglasma_code

# download subnucleondiffraction (master branch)
get_pinned https://github.com/hejajama/subnucleondiffraction \
    1cc1fed59c1124042c225076a48fa4209a8e3b95 subnucleondiffraction_code

# download nucleus configurations for IP-Glasma
(cd ipglasma_code/nucleusConfigurations; bash download_nucleusTables.sh;)
